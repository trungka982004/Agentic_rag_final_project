"""
Master test runner for Phase 1 Core Engine & Database Foundation.
Executes all unit tests verifying BM25 disk caching, PostgreSQL entities, and PDF span geometry.
"""

import os
import sys
import unittest
import time

SOURCE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if SOURCE_ROOT not in sys.path:
    sys.path.insert(0, SOURCE_ROOT)

from tests.test_bm25_cache import TestBM25BatchCache
from tests.test_academic_models import TestAcademicModels
from tests.test_pdf_spans import TestPDFSpanExtraction

def run_suite():
    print("=" * 70)
    print("      ACADEMIC STUDIO: PHASE 1 CORE ENGINE & DB TEST SUITE")
    print("=" * 70)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestBM25BatchCache))
    suite.addTests(loader.loadTestsFromTestCase(TestAcademicModels))
    suite.addTests(loader.loadTestsFromTestCase(TestPDFSpanExtraction))

    start_time = time.monotonic()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    elapsed = time.monotonic() - start_time

    print("\n" + "=" * 70)
    print(f"TEST SUITE SUMMARY: Ran {result.testsRun} tests in {elapsed:.2f}s")
    if result.wasSuccessful():
        print("ALL PHASE 1 CORE UNIT TESTS PASSED SUCCESSFULLY! (100% OK)")
    else:
        print(f"FAILED: Failures={len(result.failures)}, Errors={len(result.errors)}")
    print("=" * 70)

    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_suite())

