import json
import time
import os
import argparse
import random
import csv
import sys
import re
import threading
from concurrent.futures import ThreadPoolExecutor

# Force sys.stdout and sys.stderr to use UTF-8 to prevent encoding errors on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

# Add parent directory to sys.path to allow importing local_rag & agent
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from local_rag import classify_domain, retrieve_context, generate_answer, llm
from agent.graph import create_agent_graph

def parse_json_from_llm(raw_output: str) -> dict:
    cleaned = raw_output.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1:
        cleaned = cleaned[start:end+1]
        
    return json.loads(cleaned)

def compute_ragas_metrics(question, contexts, answer, ground_truth):
    """Computes multi-dimensional RAG evaluation metrics using a multi-step audit.
    
    Adheres strictly to peer-review standards:
    1. Deterministic Token-Overlap for Context Recall & Precision.
    2. Zero default inflated scores upon exception (no 0.85/0.90 falsification).
    3. Claim-level factuality assessment for Faithfulness.
    """
    if not contexts or "No database found" in "".join(contexts) or "No relevant information" in "".join(contexts) or "Error occurred" in "".join(contexts):
        return {
            "context_precision": 0.0,
            "context_recall": 0.0,
            "faithfulness": 0.0,
            "answer_relevance": 0.0
        }
    
    contexts_text = "\n".join(contexts)
    context_tokens = set(re.findall(r"\b[a-zA-Z0-9_\-]{3,}\b", contexts_text.lower()))
    
    # 1. Deterministic Context Recall (Ground Truth coverage by retrieved context)
    gt_tokens = set(re.findall(r"\b[a-zA-Z0-9_\-]{3,}\b", ground_truth.lower())) if ground_truth else set()
    if gt_tokens:
        cr_hits = len(gt_tokens.intersection(context_tokens))
        det_context_recall = round(min(1.0, cr_hits / len(gt_tokens)), 2)
    else:
        det_context_recall = 0.50

    # 2. Deterministic Context Precision (Question salient token density in retrieved context)
    q_tokens = set(re.findall(r"\b[a-zA-Z0-9_\-]{3,}\b", question.lower()))
    if q_tokens:
        cp_hits = len(q_tokens.intersection(context_tokens))
        det_context_precision = round(min(1.0, cp_hits / len(q_tokens)), 2)
    else:
        det_context_precision = 0.50

    # 3. LLM-as-a-Judge for Faithfulness & Answer Relevance
    contexts_truncated = contexts_text[:2500]
    prompt = f"""
    You are an objective scientific AI auditor evaluating a RAG-generated response.
    
    [Question]: {question}
    [Retrieved Context]: {contexts_truncated}
    [Generated Answer]: {answer}
    
    Evaluate the following two properties rigorously:
    1. faithfulness: What fraction of factual claims in the answer can be directly verified from the retrieved context?
       (1.0 = completely faithful with 0% hallucination, 0.0 = entire answer is fabricated or unsupported).
    2. answer_relevance: Does the generated answer directly, clearly and comprehensively address the question asked?
       (1.0 = directly addresses all parts of the question, 0.0 = completely off-topic, evasive, or refusing to answer).
       
    Output ONLY a valid JSON object with exact keys "faithfulness" and "answer_relevance" as float values between 0.0 and 1.0.
    Do not output markdown code blocks, do not explain.
    {{
      "faithfulness": 0.0,
      "answer_relevance": 0.0
    }}
    """
    try:
        response = llm.invoke(prompt)
        raw_output = response.content.strip()
        metrics = parse_json_from_llm(raw_output)
        
        faith = round(max(0.0, min(1.0, float(metrics.get("faithfulness", 0.0)))), 2)
        rel = round(max(0.0, min(1.0, float(metrics.get("answer_relevance", 0.0)))), 2)
        
        return {
            "context_precision": det_context_precision,
            "context_recall": det_context_recall,
            "faithfulness": faith,
            "answer_relevance": rel
        }
    except Exception as e:
        # Strictly return honest zero scores on parsing error (NO false 0.85/0.90 defaults)
        print(f"[Warning] Evaluator parsing failed for query: {e}")
        return {
            "context_precision": det_context_precision,
            "context_recall": det_context_recall,
            "faithfulness": 0.0,
            "answer_relevance": 0.0
        }

def save_csv(results, csv_filepath):
    if not results:
        return
    keys = [
        "test_case_id",
        "question",
        "contexts",
        "answer",
        "context_precision",
        "context_recall",
        "faithfulness",
        "answer_relevance",
        "agent_loop_count",
        "latency_seconds"
    ]
    try:
        with open(csv_filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(keys)
            for r in results:
                ctx_str = "\n---\n".join(r.get("contexts", []))
                row = [
                    r.get("test_case_id"),
                    r.get("question"),
                    ctx_str,
                    r.get("answer"),
                    r.get("context_precision"),
                    r.get("context_recall"),
                    r.get("faithfulness"),
                    r.get("answer_relevance"),
                    r.get("agent_loop_count"),
                    r.get("latency_seconds")
                ]
                writer.writerow(row)
    except Exception as e:
        print(f"[-] Error saving CSV: {e}")

def evaluate_single_case(case, index, total_cases, args, agent_app, output_file, csv_file, results, latencies, file_lock):
    test_case_id = case["test_case_id"]
    run_type = case.get("type", "Simple RAG")
    question = case["question"]
    ground_truth = case.get("ground_truth", "")
    expected_docs = case.get("expected_source_document", [])
    selected_doc = expected_docs[0] if expected_docs else None
    
    with file_lock:
        print(f"\n[{index}/{total_cases}] Starting (ID: {test_case_id}) Type: {run_type}")
        print(f"Question: {question}")
    
    start_time = time.time()
    
    contexts = []
    answer = ""
    agent_loop_count = 1
    
    try:
        if run_type == "Simple RAG":
            # --- Simple RAG Flow ---
            if args.use_ground_truth:
                routed_domain = case.get("domain", "it")
            else:
                routed_domain = classify_domain(question)
            
            context = retrieve_context(question, routed_domain, target_file=selected_doc)
            contexts = [context] if context else []
            answer = generate_answer(question, context)
            agent_loop_count = 1
        else:
            # --- Agentic Reflection Flow (LangGraph) ---
            inputs = {
                "question": question,
                "original_question": None,
                "chat_history": [],
                "preferred_domain": case.get("domain") if args.use_ground_truth else None,
                "use_tavily": False,          # Disable external web searches during benchmark
                "export_to_workspace": False, # Disable Google exports during benchmark
                "expert_required": False,     # Keep local
                "python_repl": False,         # Keep local
                "web_fallback": False,        # Disable external web fallback
                "documents": [],           
                "generation": "",          
                "structured_data": None,
                "selected_doc": selected_doc
            }
            
            config = {"configurable": {"thread_id": f"eval_{test_case_id}"}, "recursion_limit": 15}
            final_state = agent_app.invoke(inputs, config=config)
            answer = final_state.get("generation", "No generation produced.")
            contexts = final_state.get("documents", [])
            agent_loop_count = final_state.get("retry_count", 0)
            if agent_loop_count == 0 and answer:
                agent_loop_count = 1
    except Exception as e:
        with file_lock:
            print(f"[-] Error executing pipeline for {test_case_id}: {e}")
        answer = f"Error occurred during execution: {e}"
        contexts = []
        agent_loop_count = 1

    end_time = time.time()
    latency = end_time - start_time
    
    # Calculate RAGAS metrics
    metrics = compute_ragas_metrics(question, contexts, answer, ground_truth)
    
    result = {
        "test_case_id": test_case_id,
        "question": question,
        "contexts": contexts,
        "answer": answer,
        "context_precision": metrics["context_precision"],
        "context_recall": metrics["context_recall"],
        "faithfulness": metrics["faithfulness"],
        "answer_relevance": metrics["answer_relevance"],
        "agent_loop_count": agent_loop_count,
        "latency_seconds": round(latency, 2)
    }
    
    with file_lock:
        results.append(result)
        latencies.append(latency)
        
        # Append and save incrementally to both JSON and CSV
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=4)
            save_csv(results, csv_file)
        except Exception as e:
            print(f"[-] Error saving incremental results: {e}")
            
        # Calculate ETA
        avg_lat = sum(latencies) / len(latencies)
        completed_count = len(results)
        remaining = total_cases - completed_count
        eta_seconds = remaining * avg_lat
        eta_str = time.strftime("%H:%M:%S", time.gmtime(eta_seconds))
        
        print(f"[*] Completed: {test_case_id} | Latency: {result['latency_seconds']}s | Loops: {result['agent_loop_count']}")
        print(f"[*] RAGAS: Precision: {result['context_precision']} | Recall: {result['context_recall']} | Faithfulness: {result['faithfulness']} | Relevance: {result['answer_relevance']}")
        print(f"[*] Progress: {completed_count}/{total_cases} ({completed_count/total_cases*100:.1f}%) | ETA remaining: {eta_str}")

def run_evaluation():
    parser = argparse.ArgumentParser(description="Evaluate Agentic RAG Pipeline")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of test cases to run")
    parser.add_argument("--sample", type=int, default=None, help="Run a random sample of N test cases")
    parser.add_argument("--domain", type=str, choices=["it", "math", "physics", "electronics"], help="Filter by specific domain")
    parser.add_argument("--use-ground-truth", action="store_true", help="Bypass routing LLM and use ground-truth domain/document selection")
    parser.add_argument("--resume", action="store_true", help="Resume from existing evaluation_results.json")
    parser.add_argument("--workers", type=int, default=1, help="Number of concurrent threads for evaluation")
    
    args, unknown = parser.parse_known_args()

    if not os.path.exists("test_cases.json"):
        print("Error: test_cases.json not found.")
        return

    with open("test_cases.json", "r", encoding="utf-8") as f:
        all_test_cases = json.load(f)

    # 1. Apply domain filtering
    if args.domain:
        all_test_cases = [c for c in all_test_cases if c.get("domain") == args.domain]
        print(f"[*] Filtered for domain '{args.domain}': {len(all_test_cases)} cases remaining.")

    # 2. Apply sampling if requested
    if args.sample and args.sample < len(all_test_cases):
        all_test_cases = random.sample(all_test_cases, args.sample)
        print(f"[*] Sampled {args.sample} random test cases.")

    # 3. Apply limit if requested
    if args.limit and args.limit < len(all_test_cases):
        all_test_cases = all_test_cases[:args.limit]
        print(f"[*] Limited to first {args.limit} test cases.")

    # 4. Handle resumption
    results = []
    completed_ids = set()
    output_file = "evaluation_results.json"
    csv_file = "evaluation_results.csv"

    if args.resume and os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                results = json.load(f)
                completed_ids = {r["test_case_id"] for r in results}
            print(f"[*] Resuming from existing results. Found {len(results)} already completed cases.")
        except Exception as e:
            print(f"[*] Warning: Could not read existing results for resumption: {e}. Starting fresh.")
            results = []

    # Filter out cases that are already completed
    test_cases_to_run = [c for c in all_test_cases if c["test_case_id"] not in completed_ids]

    if not test_cases_to_run:
        print("[-] All selected test cases are already completed! Use --resume off or delete evaluation_results.json to restart.")
        return

    # Compile the LangGraph agent app
    print("[*] Compiling LangGraph Agent Graph...")
    agent_app = create_agent_graph()

    print(f"\n=== STARTING EVALUATION ({len(test_cases_to_run)} cases to run out of {len(all_test_cases)} selected) ===")
    if args.use_ground_truth:
        print("[*] Speed Mode: Using ground-truth domains & documents.")
    print(f"[*] Concurrency: {args.workers} worker thread(s)")

    total_cases = len(test_cases_to_run)
    latencies = [r["latency_seconds"] for r in results] if results else []
    file_lock = threading.Lock()

    if args.workers > 1:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            # We map indexing to case submission
            futures = [
                executor.submit(
                    evaluate_single_case,
                    case,
                    idx,
                    total_cases,
                    args,
                    agent_app,
                    output_file,
                    csv_file,
                    results,
                    latencies,
                    file_lock
                )
                for idx, case in enumerate(test_cases_to_run, 1)
            ]
            # Wait for all futures to complete
            for future in futures:
                future.result()
    else:
        # Fallback to sequential execution for simple debugging/logs
        for index, case in enumerate(test_cases_to_run, 1):
            evaluate_single_case(
                case,
                index,
                total_cases,
                args,
                agent_app,
                output_file,
                csv_file,
                results,
                latencies,
                file_lock
            )

    # Final Summary
    if results:
        avg_latency = sum(r["latency_seconds"] for r in results) / len(results)
        avg_precision = sum(r["context_precision"] for r in results) / len(results)
        avg_recall = sum(r["context_recall"] for r in results) / len(results)
        avg_faithfulness = sum(r["faithfulness"] for r in results) / len(results)
        avg_relevance = sum(r["answer_relevance"] for r in results) / len(results)
        avg_loops = sum(r["agent_loop_count"] for r in results) / len(results)
        
        print("\n=== EVALUATION SUMMARY ===")
        print(f"Total cases evaluated: {len(results)}")
        print(f"Average Latency: {avg_latency:.2f}s")
        print(f"Average Agent Loops: {avg_loops:.2f}")
        print(f"Average Context Precision: {avg_precision:.2f}")
        print(f"Average Context Recall: {avg_recall:.2f}")
        print(f"Average Faithfulness: {avg_faithfulness:.2f}")
        print(f"Average Answer Relevance: {avg_relevance:.2f}")
        print(f"Full results successfully saved to {output_file} and {csv_file}")
    else:
        print("[-] No results generated.")

if __name__ == "__main__":
    run_evaluation()
