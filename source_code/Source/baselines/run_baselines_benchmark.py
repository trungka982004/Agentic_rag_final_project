"""
Master Benchmark Runner for 5 Baselines vs Proposed Tiered Agentic RAG
Outputs verifiable metrics to CSV/JSON to ensure complete scientific reproducibility.
"""
import os
import sys
import json
import time
import csv
import argparse
from typing import Dict, Any, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluate import compute_ragas_metrics
from baselines.baseline_naive_rag import run_naive_rag
from baselines.baseline_advanced_rag import run_advanced_rag
from baselines.baseline_crag import run_crag
from baselines.baseline_self_rag import run_self_rag
from baselines.baseline_adaptive_rag import run_adaptive_rag
from agent.graph import create_agent_graph

BASELINE_RUNNERS = {
    "naive": run_naive_rag,
    "advanced": run_advanced_rag,
    "crag": run_crag,
    "self_rag": run_self_rag,
    "adaptive": run_adaptive_rag
}

def run_proposed_tiered_rag(question: str, domain: str = None) -> Dict[str, Any]:
    """Runs the Proposed Tiered Self-Corrective Agentic RAG pipeline."""
    start_time = time.time()
    graph = create_agent_graph()
    
    initial_state = {
        "question": question,
        "chat_history": [],
        "preferred_domain": domain,
        "retry_count": 0
    }
    
    result = graph.invoke(initial_state)
    latency = time.time() - start_time
    
    return {
        "answer": result.get("generation", ""),
        "contexts": result.get("documents", []),
        "latency": latency,
        "domain": result.get("domain", domain),
        "baseline": "Proposed_Tiered_Agentic_RAG"
    }

def run_benchmark_slice(baseline_name: str, num_samples: int = 5, output_file: str = None):
    print(f"\n=======================================================")
    print(f"  RUNNING EMPIRICAL BENCHMARK: {baseline_name.upper()}")
    print(f"=======================================================")
    
    test_cases_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test_cases.json")
    with open(test_cases_path, "r", encoding="utf-8") as f:
        all_cases = json.load(f)
        
    stem_cases = [c for c in all_cases if c.get("domain") in ["it", "physics", "math", "electronics"]][:num_samples]
    print(f"Loaded {len(stem_cases)} evaluation cases.")
    
    results = []
    total_faith = 0.0
    total_rel = 0.0
    total_prec = 0.0
    total_rec = 0.0
    total_lat = 0.0
    
    for i, tc in enumerate(stem_cases, 1):
        q = tc["question"]
        gt = tc.get("ground_truth", "")
        d = tc.get("domain", "it")
        tc_id = tc.get("test_case_id", f"TC_{i}")
        
        print(f"[{i}/{len(stem_cases)}] Eval {tc_id} ({d}): '{q[:60]}...'")
        
        if baseline_name == "proposed":
            out = run_proposed_tiered_rag(q, domain=d)
        else:
            runner = BASELINE_RUNNERS[baseline_name]
            out = runner(q, domain=d)
            
        metrics = compute_ragas_metrics(q, out["contexts"], out["answer"], gt)
        row = {
            "test_case_id": tc_id,
            "baseline": out["baseline"],
            "domain": d,
            "latency_sec": round(out["latency"], 2),
            "context_precision": metrics["context_precision"],
            "context_recall": metrics["context_recall"],
            "faithfulness": metrics["faithfulness"],
            "answer_relevance": metrics["answer_relevance"],
            "answer_snippet": out["answer"][:100].replace("\n", " ")
        }
        results.append(row)
        
        total_lat += out["latency"]
        total_faith += metrics["faithfulness"]
        total_rel += metrics["answer_relevance"]
        total_prec += metrics["context_precision"]
        total_rec += metrics["context_recall"]
        
    n = max(1, len(results))
    print(f"\n--- BENCHMARK SUMMARY FOR {baseline_name.upper()} ---")
    print(f"Avg Latency:        {total_lat/n:.2f} s")
    print(f"Avg Faithfulness:   {total_faith/n:.2f}")
    print(f"Avg Answer Rel:     {total_rel/n:.2f}")
    print(f"Avg Context Prec:   {total_prec/n:.2f}")
    print(f"Avg Context Recall: {total_rec/n:.2f}")
    
    if output_file:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
            writer.writeheader()
            writer.writerows(results)
        print(f"Saved results to: {output_file}")
        
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", choices=["naive", "advanced", "crag", "self_rag", "adaptive", "proposed"], default="naive")
    parser.add_argument("--samples", type=int, default=2)
    parser.add_argument("--out", type=str, default=None)
    args = parser.parse_args()
    
    run_benchmark_slice(args.baseline, num_samples=args.samples, output_file=args.out)
