"""
=============================================================================
  run_all_benchmarks.py  –  Master runner for all optimization benchmarks
=============================================================================
  Usage:
      python tests/run_all_benchmarks.py
      python tests/run_all_benchmarks.py --skip-llm      # skip LLM-dependent tests
      python tests/run_all_benchmarks.py --only domain   # run only domain cache tests
      python tests/run_all_benchmarks.py --only grade    # run only grade_documents tests
      python tests/run_all_benchmarks.py --only grader   # run only generation grader tests
      python tests/run_all_benchmarks.py --only condense # run only condense_question tests

  Output:
      logs/benchmarks/benchmark_<TIMESTAMP>.txt    – human-readable log
      logs/benchmarks/benchmark_<TIMESTAMP>.jsonl  – structured event log
      logs/benchmarks/report_<TIMESTAMP>.json      – full JSON report
      logs/benchmarks/LATEST_REPORT.json           – symlinked/copied latest report
=============================================================================
"""

import sys
import os
import argparse
import shutil
import json
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tests.benchmark_logger import (
    logger, LOGS_DIR, REPORT_FILE,
    save_json_report, shutdown_loggers,
    LOG_FILE_TXT, LOG_FILE_JSONL,
)

BANNER = """
╔══════════════════════════════════════════════════════════════════════╗
║          AGENTIC RAG – Optimization Benchmark Suite                 ║
║          Run: {ts:<48}║
╚══════════════════════════════════════════════════════════════════════╝
"""


def parse_args():
    p = argparse.ArgumentParser(description="Run RAG optimization benchmarks")
    p.add_argument(
        "--only",
        choices=["domain", "grade", "grader", "condense"],
        default=None,
        help="Run only a specific benchmark group",
    )
    p.add_argument(
        "--skip-llm",
        action="store_true",
        help="Skip test cases that require Ollama LLM (faster CI mode)",
    )
    args, _ = p.parse_known_args()
    return args


def run_all(args) -> dict:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(BANNER.format(ts=ts))
    logger.info(f"Log (text)   : {LOG_FILE_TXT}")
    logger.info(f"Log (jsonl)  : {LOG_FILE_JSONL}")
    logger.info(f"Report (json): {REPORT_FILE}")
    logger.info("")

    full_report = {
        "run_timestamp": ts,
        "optimizations_tested": [],
        "summary": {},
        "benchmarks": {},
    }

    # ── 1. Domain Cache ───────────────────────────────────────────────────
    if args.only in (None, "domain"):
        logger.info("\n" + "━" * 70)
        logger.info("  [1/4] Domain List TTL Cache")
        logger.info("━" * 70)
        try:
            from tests.test_domain_cache import run_domain_cache_benchmark
            r = run_domain_cache_benchmark()
            full_report["benchmarks"]["domain_cache"] = r
            full_report["optimizations_tested"].append("get_active_domains TTL cache")
        except Exception as e:
            logger.error(f"  domain_cache benchmark FAILED with exception: {e}")
            full_report["benchmarks"]["domain_cache"] = {"error": str(e)}

    # ── 2. Grade Documents ────────────────────────────────────────────────
    if args.only in (None, "grade"):
        logger.info("\n" + "━" * 70)
        logger.info("  [2/4] grade_documents_node (LLM → keyword overlap)")
        logger.info("━" * 70)
        try:
            from tests.test_grade_documents import run_grade_documents_benchmark
            r = run_grade_documents_benchmark()
            full_report["benchmarks"]["grade_documents"] = r
            full_report["optimizations_tested"].append("grade_documents_node keyword-overlap")
        except Exception as e:
            logger.error(f"  grade_documents benchmark FAILED with exception: {e}")
            full_report["benchmarks"]["grade_documents"] = {"error": str(e)}

    # ── 3. Generation Grader ─────────────────────────────────────────────
    if args.only in (None, "grader"):
        logger.info("\n" + "━" * 70)
        logger.info("  [3/4] grade_generation fast-path (selected_doc / retry≥1)")
        logger.info("━" * 70)
        try:
            from tests.test_generation_grader import run_generation_grader_benchmark
            r = run_generation_grader_benchmark()
            full_report["benchmarks"]["grade_generation"] = r
            full_report["optimizations_tested"].append("grade_generation fast-path skip")
        except Exception as e:
            logger.error(f"  grade_generation benchmark FAILED with exception: {e}")
            full_report["benchmarks"]["grade_generation"] = {"error": str(e)}

    # ── 4. Condense Question guard ────────────────────────────────────────
    if args.only in (None, "condense"):
        logger.info("\n" + "━" * 70)
        logger.info("  [4/4] condense_question() no-history guard")
        logger.info("━" * 70)
        try:
            from tests.test_condense_question import run_condense_question_benchmark
            r = run_condense_question_benchmark()
            full_report["benchmarks"]["condense_question"] = r
            full_report["optimizations_tested"].append("condense_question no-history guard")
        except Exception as e:
            logger.error(f"  condense_question benchmark FAILED with exception: {e}")
            full_report["benchmarks"]["condense_question"] = {"error": str(e)}

    # ── Global Summary ────────────────────────────────────────────────────
    all_results = []
    for bname, bdata in full_report["benchmarks"].items():
        if "results" in bdata:
            all_results.extend(bdata["results"])

    total_tests = len(all_results)
    passed_tests = sum(1 for r in all_results if r.get("passed") is True)
    skipped_tests = sum(1 for r in all_results if r.get("passed") is None)
    failed_tests = total_tests - passed_tests - skipped_tests

    full_report["summary"] = {
        "total_tests": total_tests,
        "passed": passed_tests,
        "failed": failed_tests,
        "skipped": skipped_tests,
        "pass_rate": f"{passed_tests/(total_tests - skipped_tests)*100:.1f}%" if (total_tests - skipped_tests) > 0 else "N/A",
    }

    logger.info("\n" + "═" * 70)
    logger.info("  ███  FINAL SUMMARY  ███")
    logger.info("═" * 70)
    logger.info(f"  Total tests  : {total_tests}")
    logger.info(f"  ✓ Passed     : {passed_tests}")
    logger.info(f"  ✗ Failed     : {failed_tests}")
    logger.info(f"  ◎ Skipped    : {skipped_tests}  (LLM unavailable)")
    logger.info(f"  Pass rate    : {full_report['summary']['pass_rate']}")
    logger.info("")

    # Print per-benchmark speedup summary
    logger.info("  Speedup Summary:")
    bmarks = full_report["benchmarks"]
    if "domain_cache" in bmarks and "speedup" in bmarks["domain_cache"]:
        dc = bmarks["domain_cache"]
        logger.info(f"    Domain cache    : cold {dc.get('cold_read_avg_ms','?')} ms → warm {dc.get('warm_cache_avg_ms','?')} ms  ({dc.get('speedup','?')}× speedup)")
    if "grade_documents" in bmarks and "avg_after_ms" in bmarks["grade_documents"]:
        gd = bmarks["grade_documents"]
        logger.info(f"    Grade documents : ~6000 ms (LLM) → {gd.get('avg_after_ms','?')} ms (keyword) ≈ {int(6000/max(gd.get('avg_after_ms',1),1))}× speedup")
    if "grade_generation" in bmarks and "avg_fast_path_ms" in bmarks["grade_generation"]:
        gg = bmarks["grade_generation"]
        logger.info(f"    Grade generation: ~7000 ms (LLM) → {gg.get('avg_fast_path_ms','?')} ms (skip) ≈ {int(7000/max(gg.get('avg_fast_path_ms',1),1))}× speedup (fast-path)")
    if "condense_question" in bmarks:
        cq_results = bmarks["condense_question"].get("results", [])
        guard_r = next((r for r in cq_results if r.get("path") == "no-history guard"), None)
        if guard_r:
            logger.info(f"    Condense guard  : {guard_r.get('avg_ms','?')} ms (no LLM call for new sessions)")

    logger.info("═" * 70)
    logger.info(f"\n  Full report → {REPORT_FILE}")
    logger.info(f"  Human log   → {LOG_FILE_TXT}")

    return full_report


def main():
    args = parse_args()
    try:
        full_report = run_all(args)
        path = save_json_report(full_report)

        # Copy as LATEST for easy reference
        latest = LOGS_DIR / "LATEST_REPORT.json"
        shutil.copy2(path, latest)
        logger.info(f"  Latest copy → {latest}")

    finally:
        shutdown_loggers()


if __name__ == "__main__":
    main()
