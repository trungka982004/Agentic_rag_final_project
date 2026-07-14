"""
=============================================================================
  test_condense_question.py
=============================================================================
  Benchmark: condense_question()  (nodes.py)

  Existing optimization: guard `if not chat_history: return question`
  This test VERIFIES the guard works correctly and measures its impact.

  Test cases:
    1. No history  → returns question unchanged, sub-millisecond   (PASS)
    2. Short history reference ("it", "nó", "đó") → LLM condensed (PASS / SKIP if no LLM)
    3. Non-referential follow-up → returned as-is by LLM           (PASS / SKIP)
    4. Guard timing: no-history path must be < 0.5ms               (PASS)
=============================================================================
"""

import sys, os, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tests.benchmark_logger import logger, BenchmarkTimer, log_test_result, save_json_report
from agent.nodes import condense_question

try:
    from local_rag import llm as _llm
    _LLM_AVAILABLE = _llm is not None
except Exception:
    _LLM_AVAILABLE = False

NO_HISTORY_MAX_S = 0.0005  # 0.5 ms gate for empty-history guard
REPS = 100


TEST_CASES = [
    {
        "id": "CQ-01",
        "name": "No chat history – guard short-circuit",
        "question": "What is a transformer model?",
        "chat_history": [],
        "expected_output": "What is a transformer model?",  # exact return
        "expect_fast_path": True,
    },
    {
        "id": "CQ-02",
        "name": "History present, referential question ('it')",
        "question": "How does it handle long sequences?",
        "chat_history": [
            {"user": "What is a transformer?",
             "agent": "A transformer uses self-attention to process sequences in parallel."}
        ],
        "expected_output": None,  # any condensed form is acceptable
        "expect_fast_path": False,
    },
    {
        "id": "CQ-03",
        "name": "History present, standalone question – LLM should keep as-is",
        "question": "What is backpropagation?",
        "chat_history": [
            {"user": "Explain ResNet.", "agent": "ResNet uses residual connections."}
        ],
        "expected_output": None,
        "expect_fast_path": False,
    },
]


def run_condense_question_benchmark() -> dict:
    logger.info("=" * 70)
    logger.info("BENCHMARK: condense_question()  (no-history guard verification)")
    logger.info("=" * 70)

    results = []

    for tc in TEST_CASES:
        logger.info(f"\n  ── {tc['id']}: {tc['name']}")

        if tc["expect_fast_path"]:
            # Repeat many times for stable timing
            timings = []
            outputs = []
            for _ in range(REPS):
                t0 = time.perf_counter()
                out = condense_question(tc["question"], tc["chat_history"])
                timings.append(time.perf_counter() - t0)
                outputs.append(out)

            avg_t = sum(timings) / len(timings)
            max_t = max(timings)
            correct = all(o == tc["expected_output"] for o in outputs)
            fast_enough = avg_t < NO_HISTORY_MAX_S
            passed = correct and fast_enough

            log_test_result(
                "condense_question[guard]", tc["name"],
                avg_t, passed,
                {
                    "test_id": tc["id"],
                    "avg_ms": round(avg_t * 1000, 6),
                    "max_ms": round(max_t * 1000, 6),
                    "correct": correct,
                    "reps": REPS,
                },
            )
            logger.info(f"    Avg time   : {avg_t*1000:.6f} ms  (max {max_t*1000:.6f} ms)")
            logger.info(f"    < {NO_HISTORY_MAX_S*1000:.1f}ms gate: {'✓ PASS' if fast_enough else '✗ FAIL'}")
            logger.info(f"    Exact match: {'✓' if correct else '✗'}")
            logger.info(f"    Overall    : {'✓ PASS' if passed else '✗ FAIL'}")

            results.append({
                "test_id": tc["id"],
                "name": tc["name"],
                "path": "no-history guard",
                "avg_ms": round(avg_t * 1000, 6),
                "max_ms": round(max_t * 1000, 6),
                "correct_output": correct,
                "passed": passed,
            })

        else:
            if not _LLM_AVAILABLE:
                logger.warning(f"    [{tc['id']}] LLM unavailable – skipping LLM-path test.")
                results.append({
                    "test_id": tc["id"],
                    "name": tc["name"],
                    "path": "llm-condense",
                    "passed": None,
                    "note": "LLM unavailable – skipped",
                })
                continue

            logger.info(f"    Running LLM condense (may take ~3-8s)...")
            timer = BenchmarkTimer(f"condense_{tc['id']}")
            with timer:
                out = condense_question(tc["question"], tc["chat_history"])

            # For LLM path: just verify output is a non-empty string
            passed = isinstance(out, str) and len(out) > 0
            log_test_result(
                "condense_question[llm]", tc["name"],
                timer.elapsed, passed,
                {"test_id": tc["id"], "original": tc["question"], "condensed": out},
            )
            logger.info(f"    Original  : {tc['question']}")
            logger.info(f"    Condensed : {out}")
            logger.info(f"    Elapsed   : {timer.elapsed:.3f}s")
            logger.info(f"    Overall   : {'✓ PASS' if passed else '✗ FAIL'}")

            results.append({
                "test_id": tc["id"],
                "name": tc["name"],
                "path": "llm-condense",
                "original": tc["question"],
                "condensed": out,
                "elapsed_s": round(timer.elapsed, 3),
                "passed": passed,
            })

    total = len(results)
    passed_count = sum(1 for r in results if r.get("passed") is True)

    logger.info("\n" + "─" * 70)
    logger.info(f"  condense_question SUMMARY")
    logger.info(f"  Tests passed : {passed_count}/{total}")
    logger.info("─" * 70)

    return {
        "benchmark": "condense_question",
        "passed": passed_count,
        "total": total,
        "results": results,
    }


if __name__ == "__main__":
    report = run_condense_question_benchmark()
    save_json_report({"condense_question": report})
