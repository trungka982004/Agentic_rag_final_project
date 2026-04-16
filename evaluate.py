import json
import time
import os
from main import classify_domain, retrieve_context, generate_answer

def run_evaluation():
    if not os.path.exists("test_cases.json"):
        print("Error: test_cases.json not found.")
        return

    with open("test_cases.json", "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    results = []
    print(f"=== STARTING EVALUATION ({len(test_cases)} cases) ===")

    for case in test_cases:
        print(f"\n[{case['id']}] Question: {case['question']}")
        
        start_time = time.time()
        
        # 1. Routing
        routed_domain = classify_domain(case["question"])
        
        # 2. Retrieval
        context = retrieve_context(case["question"], routed_domain)
        
        # 3. Generation (modified to not print stream for cleaner log if needed, but we use the existing function)
        # Note: generate_answer prints to console by default.
        answer = generate_answer(case["question"], context)
        
        end_time = time.time()
        latency = end_time - start_time
        
        result = {
            "id": case["id"],
            "domain_expected": case["domain"],
            "domain_routed": routed_domain,
            "question": case["question"],
            "answer": answer,
            "latency": round(latency, 2),
            "status": "Success" if "Không tìm thấy" not in context else "No Context Found"
        }
        results.append(result)
        print(f"[*] Latency: {result['latency']}s | Status: {result['status']}")

    # Save results
    with open("evaluation_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    # Summary
    avg_latency = sum(r["latency"] for r in results) / len(results)
    print("\n=== EVALUATION SUMMARY ===")
    print(f"Total cases: {len(results)}")
    print(f"Average Latency: {avg_latency:.2f}s")
    print("Full results saved to evaluation_results.json")

if __name__ == "__main__":
    run_evaluation()
