import os
import sys
import unittest

SOURCE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if SOURCE_ROOT not in sys.path:
    sys.path.insert(0, SOURCE_ROOT)

from backend.database import engine, get_db
from backend.models import DocumentSpan

class TestPDFSpanExtraction(unittest.TestCase):
    """Verifies that extracted PDF spans and bounding boxes in PostgreSQL are valid."""

    @classmethod
    def setUpClass(cls):
        cls.db = next(get_db())

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_spans_stored_and_valid_geometry(self):
        spans = self.db.query(DocumentSpan).limit(50).all()
        self.assertGreater(len(spans), 0, "There must be extracted document spans in the database")

        print(f"\n[Test] Auditing {len(spans)} sample document spans for geometric accuracy...")
        for span in spans:
            # 1. Page number validity
            self.assertGreaterEqual(span.page_number, 1, "Page number must be 1 or higher")

            # 2. Normalized coordinates (0.0 to 1.0)
            self.assertGreaterEqual(span.bbox_x0, 0.0, "bbox_x0 must be >= 0.0")
            self.assertLessEqual(span.bbox_x1, 1.0, "bbox_x1 must be <= 1.0")
            self.assertGreaterEqual(span.bbox_y0, 0.0, "bbox_y0 must be >= 0.0")
            self.assertLessEqual(span.bbox_y1, 1.0, "bbox_y1 must be <= 1.0")

            # 3. Geometry orientation
            self.assertLessEqual(span.bbox_x0, span.bbox_x1, "bbox_x0 must be <= bbox_x1")
            self.assertLessEqual(span.bbox_y0, span.bbox_y1, "bbox_y0 must be <= bbox_y1")

            # 4. Text validity
            self.assertGreaterEqual(len(span.text_content.strip()), 10, "Span text content must be non-trivial")

        sample = spans[0]
        print(f"[Test] Sample span from '{sample.document_name}' (p.{sample.page_number}): bbox=({sample.bbox_x0}, {sample.bbox_y0}, {sample.bbox_x1}, {sample.bbox_y1})")
        print(f"[Test] Sample snippet: {repr(sample.text_content[:80])}...")

if __name__ == "__main__":
    unittest.main()
