"""
=============================================================================
  benchmark_logger.py  –  Centralized structured logging for optimization benchmarks
=============================================================================
  Provides:
    - StructuredLogger  : JSON-lines + human-readable console output
    - BenchmarkTimer    : Context manager to measure wall-clock latency
    - save_json_report  : Persist full JSON benchmark report to disk
=============================================================================
"""

import json
import logging
import os
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = ROOT_DIR / "logs" / "benchmarks"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

_RUN_TS = datetime.now().strftime("%Y%m%d_%H%M%S")

LOG_FILE_JSONL = LOGS_DIR / f"benchmark_{_RUN_TS}.jsonl"
LOG_FILE_TXT   = LOGS_DIR / f"benchmark_{_RUN_TS}.txt"
REPORT_FILE    = LOGS_DIR / f"report_{_RUN_TS}.json"

# ---------------------------------------------------------------------------
# Human-readable console + text-file logger
# ---------------------------------------------------------------------------
_fmt = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S"
)

_txt_handler = logging.FileHandler(LOG_FILE_TXT, encoding="utf-8")
_txt_handler.setFormatter(_fmt)

_con_handler = logging.StreamHandler()
_con_handler.setFormatter(_fmt)

_root = logging.getLogger("rag_bench")
_root.setLevel(logging.DEBUG)
_root.addHandler(_txt_handler)
_root.addHandler(_con_handler)
_root.propagate = False

logger: logging.Logger = _root


# ---------------------------------------------------------------------------
# JSON-lines structured event writer
# ---------------------------------------------------------------------------
class StructuredLogger:
    """Appends one JSON object per line to the JSONL log file."""

    def __init__(self, filepath: Path = LOG_FILE_JSONL):
        self._fh = open(filepath, "a", encoding="utf-8")

    def log(self, event_type: str, data: Dict[str, Any]) -> None:
        record = {
            "ts": datetime.now(tz=timezone.utc).isoformat(),
            "event": event_type,
            **data,
        }
        self._fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        self._fh.flush()

    def close(self) -> None:
        self._fh.close()


_slog = StructuredLogger()


# ---------------------------------------------------------------------------
# Context-manager timer
# ---------------------------------------------------------------------------
class BenchmarkTimer:
    """
    Usage:
        timer = BenchmarkTimer("grade_documents")
        with timer:
            ... do_work ...
        print(timer.elapsed)
    """

    def __init__(self, label: str):
        self.label = label
        self.elapsed: float = 0.0
        self._start: float = 0.0

    def __enter__(self) -> "BenchmarkTimer":
        self._start = time.perf_counter()
        return self

    def __exit__(self, *_) -> None:
        self.elapsed = time.perf_counter() - self._start
        logger.debug(f"[timer] {self.label}: {self.elapsed:.4f}s")


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------
def log_test_result(
    test_name: str,
    scenario: str,
    elapsed: float,
    passed: bool,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """Log one test result to both the human-readable log and the JSONL stream."""
    status = "PASS" if passed else "FAIL"
    logger.info(f"  [{status}] {test_name} | {scenario} | {elapsed:.4f}s")
    _slog.log(
        "test_result",
        {
            "test": test_name,
            "scenario": scenario,
            "elapsed_s": round(elapsed, 6),
            "passed": passed,
            **(details or {}),
        },
    )


def save_json_report(report: Dict[str, Any]) -> Path:
    """Persist the full benchmark report dict as a formatted JSON file."""
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    logger.info(f"  Report saved → {REPORT_FILE}")
    return REPORT_FILE


def shutdown_loggers() -> None:
    _slog.close()


# expose paths for importing modules
__all__ = [
    "logger",
    "LOG_FILE_TXT",
    "LOG_FILE_JSONL",
    "REPORT_FILE",
    "LOGS_DIR",
    "BenchmarkTimer",
    "StructuredLogger",
    "log_test_result",
    "save_json_report",
    "shutdown_loggers",
]
