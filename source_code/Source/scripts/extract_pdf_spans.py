import os
import sys
import argparse
import logging
import pymupdf as fitz
from typing import List, Dict, Any

# Ensure source root is in sys.path
SOURCE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if SOURCE_ROOT not in sys.path:
    sys.path.insert(0, SOURCE_ROOT)

from backend.database import engine, Base, get_db
from backend.models import DocumentSpan

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

RAW_DATA_PATH = os.path.join(SOURCE_ROOT, "data", "raw")

def extract_spans_from_pdf(pdf_path: str, domain: str, doc_name: str) -> List[Dict[str, Any]]:
    """Extracts text blocks and normalized bounding boxes [x0, y0, x1, y1] from a PDF."""
    spans = []
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        logger.warning(f"Could not open PDF '{doc_name}': {e}")
        return spans

    try:
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            page_rect = page.rect
            if page_rect.width <= 0 or page_rect.height <= 0:
                continue

            # (x0, y0, x1, y1, text, block_no, block_type)
            blocks = page.get_text("blocks")
            for b in blocks:
                # b[6] == 0 indicates a text block (1 is image)
                if len(b) > 6 and b[6] != 0:
                    continue

                text = b[4].strip()
                # Ignore noise, short headers/footers, or single page numbers
                if len(text) < 25:
                    continue

                spans.append({
                    "domain": domain,
                    "document_name": doc_name,
                    "page_number": page_idx + 1,
                    "bbox_x0": round(max(0.0, min(1.0, b[0] / page_rect.width)), 4),
                    "bbox_y0": round(max(0.0, min(1.0, b[1] / page_rect.height)), 4),
                    "bbox_x1": round(max(0.0, min(1.0, b[2] / page_rect.width)), 4),
                    "bbox_y1": round(max(0.0, min(1.0, b[3] / page_rect.height)), 4),
                    "text_content": text,
                    "chunk_id": f"{domain}::{doc_name}::p{page_idx + 1}::b{b[5] if len(b) > 5 else 0}"
                })
    except Exception as e:
        logger.warning(f"Error parsing pages in '{doc_name}': {e}")
    finally:
        doc.close()

    return spans

def run_extraction(target_domain: str = None, limit_files: int = None, batch_size: int = 500):
    """Processes raw PDFs across domains and saves spans into PostgreSQL document_spans."""
    Base.metadata.create_all(bind=engine)
    db = next(get_db())

    if not os.path.exists(RAW_DATA_PATH):
        logger.error(f"Raw data path not found: {RAW_DATA_PATH}")
        return

    domains = [target_domain] if target_domain else [
        d for d in os.listdir(RAW_DATA_PATH)
        if os.path.isdir(os.path.join(RAW_DATA_PATH, d)) and not d.startswith(".")
    ]

    total_extracted_spans = 0
    total_processed_files = 0

    for domain in sorted(domains):
        domain_dir = os.path.join(RAW_DATA_PATH, domain)
        if not os.path.exists(domain_dir):
            continue

        pdf_files = [f for f in os.listdir(domain_dir) if f.lower().endswith(".pdf")]
        if limit_files:
            pdf_files = pdf_files[:limit_files]

        logger.info(f"[*] Processing domain '{domain}': {len(pdf_files)} PDF files...")

        # Check existing documents in DB for this domain to avoid redundant extraction
        existing_docs = set(
            row[0] for row in db.query(DocumentSpan.document_name)
            .filter(DocumentSpan.domain == domain)
            .distinct()
            .all()
        )

        pending_spans: List[Dict[str, Any]] = []

        for pdf_name in pdf_files:
            if pdf_name in existing_docs:
                continue

            pdf_path = os.path.join(domain_dir, pdf_name)
            file_spans = extract_spans_from_pdf(pdf_path, domain, pdf_name)

            if file_spans:
                pending_spans.extend(file_spans)
                total_extracted_spans += len(file_spans)
                total_processed_files += 1

            # Commit in batches to keep memory and transaction log small
            if len(pending_spans) >= batch_size:
                db.bulk_insert_mappings(DocumentSpan, pending_spans)
                db.commit()
                logger.info(f"  -> Committed batch of {len(pending_spans)} spans into PostgreSQL.")
                pending_spans = []

        if pending_spans:
            db.bulk_insert_mappings(DocumentSpan, pending_spans)
            db.commit()
            logger.info(f"  -> Committed final batch of {len(pending_spans)} spans for domain '{domain}'.")

    db.close()
    logger.info("==================================================")
    logger.info(f"EXTRACTION COMPLETE: {total_processed_files} new PDFs processed, {total_extracted_spans} spans stored.")
    logger.info("==================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract bounding box text spans from academic PDFs.")
    parser.add_argument("--domain", type=str, default=None, help="Specific domain to process (e.g. it, math)")
    parser.add_argument("--limit-files", type=int, default=None, help="Limit number of PDF files to process per domain")
    parser.add_argument("--batch-size", type=int, default=500, help="DB insert batch size")
    args = parser.parse_args()

    run_extraction(target_domain=args.domain, limit_files=args.limit_files, batch_size=args.batch_size)
