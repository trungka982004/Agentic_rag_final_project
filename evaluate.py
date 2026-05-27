import json
import time
import os
import argparse
import random
from local_rag import classify_domain, retrieve_context, generate_answer

def run_evaluation():
    parser = argparse.ArgumentParser(description="Evaluate Agentic RAG Pipeline")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of test cases to run")
    parser.add_argument("--sample", type=int, default=None, help="Run a random sample of N test cases")
    parser.add_argument("--domain", type=str, choices=["it", "math", "physics", "electronics"], help="Filter by specific domain")
    parser.add_argument("--use-ground-truth", action="store_true", help="Bypass routing LLM and use ground-truth domain")
    parser.add_argument("--resume", action="store_true", help="Resume from existing evaluation_results.json")
    
    # Allow running in interactive environments (like notebooks or IDEs) without failing on unknown args
    args, unknown = parser.parse_known_args()

    if not os.path.exists("test_cases.json"):
        print("Error: test_cases.json not found.")
        return

    with open("test_cases.json", "r", encoding="utf-8") as f:
        all_test_cases = json.load(f)

    # 1. Apply domain filtering
    if args.domain:
        all_test_cases = [c for c in all_test_cases if c["domain"] == args.domain]
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

    if args.resume and os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                results = json.load(f)
                completed_ids = {r["id"] for r in results}
            print(f"[*] Resuming from existing results. Found {len(results)} already completed cases.")
        except Exception as e:
            print(f"[*] Warning: Could not read existing results for resumption: {e}. Starting fresh.")
            results = []

    # Filter out cases that are already completed
    test_cases_to_run = [c for c in all_test_cases if c["id"] not in completed_ids]

    if not test_cases_to_run:
        print("[-] All selected test cases are already completed! Use --resume off or delete evaluation_results.json to restart.")
        return

    print(f"\n=== STARTING EVALUATION ({len(test_cases_to_run)} cases to run out of {len(all_test_cases)} selected) ===")
    if args.use_ground_truth:
        print("[*] Speed Mode: Using ground-truth domains (bypassing router LLM calls).")

    total_cases = len(test_cases_to_run)
    latencies = [r["latency"] for r in results] if results else []

    for index, case in enumerate(test_cases_to_run, 1):
        print(f"\n[{index}/{total_cases}] (ID: {case['id']}) Question: {case['question']}")
        
        start_time = time.time()
        
        # 1. Domain Classification (Routing)
        if args.use_ground_truth:
            routed_domain = case["domain"]
            print(f"[*] Routing (Ground-Truth): {routed_domain.upper()}")
        else:
            routed_domain = classify_domain(case["question"])
            print(f"[*] Routing (LLM/Keyword): {routed_domain.upper()}")
        
        # 2. Context Retrieval
        print("[*] Retrieving context...")
        context = retrieve_context(case["question"], routed_domain)
        
        # 3. Answer Generation
        print("[*] Generating answer...")
        answer = generate_answer(case["question"], context)
        
        end_time = time.time()
        latency = end_time - start_time
        latencies.append(latency)
        
        result = {
            "id": case["id"],
            "domain_expected": case["domain"],
            "domain_routed": routed_domain,
            "question": case["question"],
            "answer": answer,
            "latency": round(latency, 2),
            "status": "Success" if "No database found" not in context and "No relevant information" not in context else "No Context Found"
        }
        
        # Append and save incrementally
        results.append(result)
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"[-] Error saving incremental results: {e}")
            
        # Calculate ETA
        avg_lat = sum(latencies) / len(latencies)
        remaining = total_cases - index
        eta_seconds = remaining * avg_lat
        eta_str = time.strftime("%H:%M:%S", time.gmtime(eta_seconds))
        
        print(f"[*] Latency: {result['latency']}s | Status: {result['status']}")
        print(f"[*] Progress: {index}/{total_cases} ({index/total_cases*100:.1f}%) | ETA remaining: {eta_str}")

    # Final Summary
    avg_latency = sum(r["latency"] for r in results) / len(results)
    print("\n=== EVALUATION SUMMARY ===")
    print(f"Total cases evaluated: {len(results)}")
    print(f"Average Latency: {avg_latency:.2f}s")
    print(f"Full results successfully saved to {output_file}")

if __name__ == "__main__":
    run_evaluation()
