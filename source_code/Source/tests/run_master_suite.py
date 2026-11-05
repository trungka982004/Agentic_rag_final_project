import unittest
import sys
import os
import time

# Set UTF-8 encoding
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_bm25_cache import TestBM25BatchCache
from tests.test_academic_models import TestAcademicModels
from tests.test_pdf_spans import TestPDFSpanExtraction
from tests.test_export_service import TestExportService

def run_master_audit_suite():
    print("\n" + "="*70)
    print("      ACADEMIC STUDIO: COMPLETE 5-PHASE MASTER SYSTEM AUDIT")
    print("="*70)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Phase 1: Core DB & Retrieval
    suite.addTests(loader.loadTestsFromTestCase(TestBM25BatchCache))
    suite.addTests(loader.loadTestsFromTestCase(TestAcademicModels))
    suite.addTests(loader.loadTestsFromTestCase(TestPDFSpanExtraction))

    # Phase 5: Compiler & Export Engine
    suite.addTests(loader.loadTestsFromTestCase(TestExportService))

    runner = unittest.TextTestRunner(verbosity=2)
    start_time = time.time()
    result = runner.run(suite)
    duration = time.time() - start_time

    print("\n" + "="*70)
    print(f"MASTER AUDIT COMPLETE: Ran {result.testsRun} tests in {duration:.2f}s")
    if result.wasSuccessful():
        print("ALL ARCHITECTURAL UPGRADE TESTS PASSED WITH 100% SUCCESS!")
    else:
        print(f"FAILED: {len(result.failures)} failures, {len(result.errors)} errors")
    print("="*70 + "\n")
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_master_audit_suite()
    sys.exit(0 if success else 1)
