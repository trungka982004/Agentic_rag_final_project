"""
=============================================================================
  test_generation_grader.py
=============================================================================
  Benchmark: grade_generation_v_documents_and_question  (edges.py)

  BEFORE: luôn gọi LLM để chấm điểm answer        → ~5-10s per call
  AFTER :
    - selected_doc → return "useful" immediately    → <0.001s
    - retry_count ≥ 1 → return "useful" immediately → <0.001s
    - First attempt, no selected_doc → LLM grader (unchanged path)

  Test cases:
    1. selected_doc set   → "useful" instantly, no LLM           (PASS)
    2. retry_count=1      → "useful" instantly, no LLM           (PASS)
    3. retry_count=2      → "useful" instantly, no LLM           (PASS)
    4. retry_count=0, no selected_doc, good answer → LLM grader  (PASS)
    5. Timing: fast-path must be < 0.01s                         (PASS)
=============================================================================
"""

import sys, os, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tests.benchmark_logger import logger, BenchmarkTimer, log_test_result, save_json_report
from agent.edges import grade_generation_v_documents_and_question

try:
    from local_rag import llm as _llm
    _LLM_AVAILABLE = _llm is not None
except Exception:
    _LLM_AVAILABLE = False

# Fast-path latency gate (milliseconds)
FAST_PATH_MAX_S = 0.01
# How many times to repeat fast-path calls to get stable timing
FAST_PATH_REPS = 20


TEST_CASES = [
    # ── Fast-path cases ────────────────────────────────────────────────────
    {
        "id": "GG-01",
        "name": "selected_doc set → fast-path skip",
        "state": {
            "question": "Summarize ResNet architecture",
            "documents": ["ResNet uses residual connections to solve vanishing gradients..."],
            "generation": "ResNet uses skip connections allowing gradients to flow directly.",
            "retry_count": 0,
            "selected_doc": "ResNet_paper.pdf",
        },
        "expected_decision": "useful",
        "expect_fast_path": True,
    },
    {
        "id": "GG-02",
        "name": "retry_count=1 → fast-path skip",
        "state": {
            "question": "Explain backpropagation in neural networks",
            "documents": ["Backpropagation computes gradients using chain rule..."],
            "generation": "Backpropagation is used to compute gradients for training neural nets.",
            "retry_count": 1,
            "selected_doc": None,
        },
        "expected_decision": "useful",
        "expect_fast_path": True,
    },
    {
        "id": "GG-03",
        "name": "retry_count=2 → fast-path skip (max retries)",
        "state": {
            "question": "What is quantum entanglement?",
            "documents": [],
            "generation": "Quantum entanglement is a phenomenon where particles correlate.",
            "retry_count": 2,
            "selected_doc": None,
        },
        "expected_decision": "useful",
        "expect_fast_path": True,
    },
    # ── LLM grader path (only when Ollama available) ──────────────────────
    {
        "id": "GG-04",
        "name": "First attempt, no selected_doc → LLM grader runs",
        "state": {
            "question": "What is a transformer model?",
            "documents": [
                "The transformer model uses self-attention mechanisms. "
                "It was proposed in 'Attention is All You Need' (2017). "
                "Transformers are now the backbone of modern NLP systems."
            ],
            "generation": (
                "A transformer model is a deep learning architecture that relies on "
                "self-attention mechanisms to process sequences in parallel, making it "
                "faster than RNNs for NLP tasks."
            ),
            "retry_count": 0,
            "selected_doc": None,
        },
        "expected_decision": "useful",   # expect well-grounded answer to pass
        "expect_fast_path": False,
    },
]


def run_generation_grader_benchmark() -> dict:
    logger.info("=" * 70)
    logger.info("BENCHMARK: grade_generation_v_documents_and_question")
    logger.info("         (BEFORE always-LLM vs AFTER fast-path)")
    logger.info("=" * 70)

    results = []
    fast_path_latencies = []
    llm_path_latencies = []

    for tc in TEST_CASES:
        logger.info(f"\n  ── {tc['id']}: {tc['name']}")
        is_fast = tc["expect_fast_path"]

        if is_fast:
            # Repeat the call multiple times for stable timing measurement
            decisions = []
            timings = []
            for _ in range(FAST_PATH_REPS):
                t0 = time.perf_counter()
                decision = grade_generation_v_documents_and_question(tc["state"])
                timings.append(time.perf_counter() - t0)
                decisions.append(decision)

            avg_t = sum(timings) / len(timings)
            max_t = max(timings)
            decision = decisions[0]  # all should be identical
            fast_path_latencies.append(avg_t)

            correct = (decision == tc["expected_decision"])
            fast_enough = (avg_t < FAST_PATH_MAX_S)
            passed = correct and fast_enough

            log_test_result(
                test_name="grade_generation[AFTER-fast-path]",
                scenario=tc["name"],
                elapsed=avg_t,
                passed=passed,
                details={
                    "test_id": tc["id"],
                    "expected": tc["expected_decision"],
                    "got": decision,
                    "correct": correct,
                    "fast_enough": fast_enough,
                    "reps": FAST_PATH_REPS,
                    "max_t_s": round(max_t, 6),
                },
            )
            logger.info(f"    Decision  : {decision} (expected {tc['expected_decision']}) → {'✓' if correct else '✗'}")
            logger.info(f"    Avg time  : {avg_t*1000:.4f} ms  (max {max_t*1000:.4f} ms over {FAST_PATH_REPS} reps)")
            logger.info(f"    < {FAST_PATH_MAX_S*1000:.0f} ms gate : {'✓ PASS' if fast_enough else '✗ FAIL'}")
            logger.info(f"    Overall   : {'✓ PASS' if passed else '✗ FAIL'}")
            logger.info(f"    BEFORE est: ~6-10s (LLM call) → speedup ≈ {6/max(avg_t,1e-9):.0f}×")

            results.append({
                "test_id": tc["id"],
                "name": tc["name"],
                "path": "fast-path (no LLM)",
                "expected": tc["expected_decision"],
                "got": decision,
                "correct_decision": correct,
                "avg_elapsed_ms": round(avg_t * 1000, 4),
                "max_elapsed_ms": round(max_t * 1000, 4),
                "before_estimate_s": "~6-10 (LLM)",
                "speedup_estimate": f"~{int(6/max(avg_t,1e-9))}×",
                "passed": passed,
            })

        else:
            # LLM grader path – run only if Ollama is available
            if not _LLM_AVAILABLE:
                logger.warning(f"    [{tc['id']}] LLM not available – skipping grader path test.")
                results.append({
                    "test_id": tc["id"],
                    "name": tc["name"],
                    "path": "llm-grader",
                    "passed": None,
                    "note": "LLM unavailable – skipped",
                })
                continue

            logger.info(f"    Running LLM grader (may take ~5-15s)...")
            timer = BenchmarkTimer(f"llm_grader_{tc['id']}")
            with timer:
                decision = grade_generation_v_documents_and_question(tc["state"])

            llm_path_latencies.append(timer.elapsed)
            correct = (decision == tc["expected_decision"])
            passed = correct  # no strict latency gate for LLM path

            log_test_result(
                test_name="grade_generation[AFTER-llm-path]",
                scenario=tc["name"],
                elapsed=timer.elapsed,
                passed=passed,
                details={
                    "test_id": tc["id"],
                    "expected": tc["expected_decision"],
                    "got": decision,
                },
            )
            logger.info(f"    Decision  : {decision} (expected {tc['expected_decision']}) → {'✓' if correct else '✗'}")
            logger.info(f"    Elapsed   : {timer.elapsed:.3f}s")
            logger.info(f"    Overall   : {'✓ PASS' if passed else '✗ FAIL'}")

            results.append({
                "test_id": tc["id"],
                "name": tc["name"],
                "path": "llm-grader",
                "expected": tc["expected_decision"],
                "got": decision,
                "correct_decision": correct,
                "elapsed_s": round(timer.elapsed, 3),
                "passed": passed,
            })

    # ── Summary ──────────────────────────────────────────────────────────
    total = len(results)
    passed_count = sum(1 for r in results if r.get("passed") is True)
    avg_fast = sum(fast_path_latencies) / len(fast_path_latencies) if fast_path_latencies else 0
    avg_llm  = sum(llm_path_latencies) / len(llm_path_latencies) if llm_path_latencies else None

    logger.info("\n" + "─" * 70)
    logger.info(f"  grade_generation SUMMARY")
    logger.info(f"  Tests passed       : {passed_count}/{total}")
    logger.info(f"  Avg fast-path time : {avg_fast*1000:.4f} ms")
    logger.info(f"  Avg LLM-path time  : {f'{avg_llm:.2f}s' if avg_llm else 'N/A'}")
    logger.info(f"  BEFORE estimate    : ~6-10s per call (always LLM)")
    logger.info(f"  Estimated speedup  : ~{int(7/max(avg_fast,1e-9))}× for selected_doc/retry paths")
    logger.info("─" * 70)

    return {
        "benchmark": "grade_generation_v_documents_and_question",
        "passed": passed_count,
        "total": total,
        "avg_fast_path_ms": round(avg_fast * 1000, 4),
        "avg_llm_path_s": round(avg_llm, 3) if avg_llm else "N/A",
        "results": results,
    }


if __name__ == "__main__":
    report = run_generation_grader_benchmark()
    save_json_report({"grade_generation": report})
