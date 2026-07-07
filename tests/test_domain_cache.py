"""
=============================================================================
  test_domain_cache.py
=============================================================================
  Benchmark: get_active_domains() TTL cache (local_rag.py)

  BEFORE: reads disk every call                → I/O overhead per pipeline step
  AFTER : returns cached list within 30s TTL   → pure dict lookup (<0.001ms)

  Test cases:
    1. Cold-start read (first call)            → hits disk, populates cache
    2. Warm cache (subsequent call < 30s)      → pure memory return
    3. Cache invalidation via clear_rag_caches → next call hits disk again
    4. Concurrent calls return identical list  → thread-safety check
    5. Timing: warm cache must be < 0.001s     → performance gate
=============================================================================
"""

import sys, os, time, threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tests.benchmark_logger import logger, BenchmarkTimer, log_test_result, save_json_report

import local_rag
from local_rag import get_active_domains, clear_rag_caches

WARM_CACHE_MAX_S = 0.001   # 1 ms gate for cached reads
COLD_READ_REPS   = 3
WARM_READ_REPS   = 200     # many iterations to detect overhead


def run_domain_cache_benchmark() -> dict:
    logger.info("=" * 70)
    logger.info("BENCHMARK: get_active_domains()  (BEFORE disk read vs AFTER TTL cache)")
    logger.info("=" * 70)

    results = []

    # ── TC-1: Cold-start – must hit disk ─────────────────────────────────
    logger.info("\n  ── DC-01: Cold-start (cache empty)")
    clear_rag_caches()

    cold_timings = []
    domains_cold = None
    for i in range(COLD_READ_REPS):
        clear_rag_caches()
        t0 = time.perf_counter()
        domains_cold = get_active_domains()
        cold_timings.append(time.perf_counter() - t0)

    avg_cold = sum(cold_timings) / len(cold_timings)
    domains_found = len(domains_cold)
    passed = domains_found > 0
    log_test_result(
        "get_active_domains[cold]", "DC-01 cold-start",
        avg_cold, passed,
        {"domains": domains_cold, "reps": COLD_READ_REPS},
    )
    logger.info(f"    Domains found  : {domains_cold}")
    logger.info(f"    Avg cold time  : {avg_cold*1000:.3f} ms")
    logger.info(f"    Domains > 0    : {'✓ PASS' if passed else '✗ FAIL'}")
    results.append({
        "test_id": "DC-01", "name": "Cold-start read",
        "avg_ms": round(avg_cold * 1000, 3), "domains": domains_cold, "passed": passed,
    })

    # ── TC-2: Warm cache – pure memory return ────────────────────────────
    logger.info("\n  ── DC-02: Warm cache (repeated calls within TTL)")
    warm_timings = []
    for _ in range(WARM_READ_REPS):
        t0 = time.perf_counter()
        domains_warm = get_active_domains()
        warm_timings.append(time.perf_counter() - t0)

    avg_warm = sum(warm_timings) / len(warm_timings)
    max_warm = max(warm_timings)
    speedup = avg_cold / max(avg_warm, 1e-9)
    fast_enough = avg_warm < WARM_CACHE_MAX_S
    domains_match = (domains_warm == domains_cold)
    passed = fast_enough and domains_match

    log_test_result(
        "get_active_domains[warm]", "DC-02 warm-cache",
        avg_warm, passed,
        {
            "reps": WARM_READ_REPS,
            "avg_ms": round(avg_warm * 1000, 6),
            "max_ms": round(max_warm * 1000, 6),
            "speedup": round(speedup, 1),
            "domains_consistent": domains_match,
        },
    )
    logger.info(f"    Avg warm time  : {avg_warm*1000:.6f} ms")
    logger.info(f"    Max warm time  : {max_warm*1000:.6f} ms")
    logger.info(f"    Speedup vs cold: {speedup:.1f}×")
    logger.info(f"    Data consistent: {domains_match}")
    logger.info(f"    < {WARM_CACHE_MAX_S*1000:.0f} ms gate: {'✓ PASS' if fast_enough else '✗ FAIL'}")
    logger.info(f"    Overall        : {'✓ PASS' if passed else '✗ FAIL'}")
    results.append({
        "test_id": "DC-02", "name": "Warm cache read",
        "avg_ms": round(avg_warm * 1000, 6),
        "max_ms": round(max_warm * 1000, 6),
        "speedup_vs_cold": round(speedup, 1),
        "domains_consistent": domains_match,
        "passed": passed,
    })

    # ── TC-3: Cache invalidation ──────────────────────────────────────────
    logger.info("\n  ── DC-03: Cache invalidation via clear_rag_caches()")
    _ = get_active_domains()  # warm up
    assert local_rag._domains_cache, "Cache should be populated before invalidation"

    clear_rag_caches()

    cache_cleared = (local_rag._domains_cache == [])
    # Next call should hit disk again (just measure it, don't gate on timing)
    t0 = time.perf_counter()
    domains_after_clear = get_active_domains()
    post_clear_t = time.perf_counter() - t0

    passed = cache_cleared and (domains_after_clear == domains_cold)
    log_test_result(
        "get_active_domains[invalidate]", "DC-03 cache invalidation",
        post_clear_t, passed,
        {"cache_was_cleared": cache_cleared, "domains_consistent_after": domains_after_clear == domains_cold},
    )
    logger.info(f"    Cache cleared         : {cache_cleared}")
    logger.info(f"    Domains after re-read : {domains_after_clear}")
    logger.info(f"    Consistent with cold  : {domains_after_clear == domains_cold}")
    logger.info(f"    Overall               : {'✓ PASS' if passed else '✗ FAIL'}")
    results.append({
        "test_id": "DC-03", "name": "Cache invalidation",
        "cache_was_cleared": cache_cleared,
        "post_clear_read_ms": round(post_clear_t * 1000, 3),
        "domains_consistent": domains_after_clear == domains_cold,
        "passed": passed,
    })

    # ── TC-4: Thread-safety – concurrent reads return identical lists ─────
    logger.info("\n  ── DC-04: Thread-safety (10 concurrent readers)")
    # Make sure cache is warm
    _ = get_active_domains()

    thread_results = []
    errors = []

    def _reader(tid: int):
        try:
            r = get_active_domains()
            thread_results.append((tid, r))
        except Exception as e:
            errors.append(str(e))

    threads = [threading.Thread(target=_reader, args=(i,)) for i in range(10)]
    t0 = time.perf_counter()
    for th in threads:
        th.start()
    for th in threads:
        th.join()
    concurrent_t = time.perf_counter() - t0

    all_same = all(r == domains_cold for _, r in thread_results)
    no_errors = (len(errors) == 0)
    passed = all_same and no_errors and len(thread_results) == 10

    log_test_result(
        "get_active_domains[concurrent]", "DC-04 thread-safety",
        concurrent_t, passed,
        {"thread_count": 10, "all_same": all_same, "errors": errors},
    )
    logger.info(f"    Threads completed: {len(thread_results)}/10")
    logger.info(f"    All returned same: {all_same}")
    logger.info(f"    Errors           : {errors or 'none'}")
    logger.info(f"    Overall          : {'✓ PASS' if passed else '✗ FAIL'}")
    results.append({
        "test_id": "DC-04", "name": "Thread-safety",
        "threads": 10, "all_consistent": all_same,
        "errors": errors, "passed": passed,
    })

    # ── Summary ──────────────────────────────────────────────────────────
    total = len(results)
    passed_count = sum(1 for r in results if r["passed"])

    logger.info("\n" + "─" * 70)
    logger.info(f"  domain_cache SUMMARY")
    logger.info(f"  Tests passed      : {passed_count}/{total}")
    logger.info(f"  Cold read avg     : {avg_cold*1000:.3f} ms")
    logger.info(f"  Warm cache avg    : {avg_warm*1000:.6f} ms  ({WARM_READ_REPS} reps)")
    logger.info(f"  Speedup           : {avg_cold/max(avg_warm,1e-9):.0f}×")
    logger.info("─" * 70)

    return {
        "benchmark": "get_active_domains_cache",
        "passed": passed_count,
        "total": total,
        "cold_read_avg_ms": round(avg_cold * 1000, 3),
        "warm_cache_avg_ms": round(avg_warm * 1000, 6),
        "speedup": round(avg_cold / max(avg_warm, 1e-9), 0),
        "results": results,
    }


if __name__ == "__main__":
    report = run_domain_cache_benchmark()
    save_json_report({"domain_cache": report})
