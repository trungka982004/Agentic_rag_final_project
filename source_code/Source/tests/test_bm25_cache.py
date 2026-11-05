import os
import sys
import time
import unittest

# Ensure source root is in sys.path
SOURCE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if SOURCE_ROOT not in sys.path:
    sys.path.insert(0, SOURCE_ROOT)

from local_rag import get_vector_db, get_bm25_retriever, clear_rag_caches, Config

class TestBM25BatchCache(unittest.TestCase):
    """Unit test for batched extraction and disk caching of BM25 retriever."""

    def setUp(self):
        # Clear in-memory caches before test
        clear_rag_caches(clear_disk_bm25=False)

    def test_bm25_batch_build_and_disk_cache(self):
        db = get_vector_db("it")
        self.assertIsNotNone(db, "IT vector store must exist")

        total_chunks = db._collection.count()
        print(f"\n[Test] Total chunks in 'it' domain: {total_chunks}")
        self.assertGreater(total_chunks, 1000, "IT domain should have large chunk count exceeding SQLite 999 limit")

        # 1. First build (or load from disk if already cached)
        start_time = time.monotonic()
        retriever = get_bm25_retriever(db, "it", k=3)
        duration_1 = time.monotonic() - start_time
        print(f"[Test] First retrieval acquisition took: {duration_1:.2f}s")

        self.assertIsNotNone(retriever, "BM25Retriever must be created successfully without SQLite error")

        # Check that cache file exists on disk
        expected_cache_file = os.path.join(Config.BM25_CACHE_PATH, "it_bm25.pkl")
        self.assertTrue(os.path.exists(expected_cache_file), f"Cache file {expected_cache_file} must exist on disk")

        # 2. Test in-memory cache
        start_mem = time.monotonic()
        mem_retriever = get_bm25_retriever(db, "it", k=3)
        duration_mem = time.monotonic() - start_mem
        print(f"[Test] In-memory retrieval took: {duration_mem * 1000:.2f}ms")
        self.assertLess(duration_mem, 0.05, "In-memory retrieval must take less than 50ms")

        # 3. Test disk cache reload (clear in-memory first)
        clear_rag_caches(clear_disk_bm25=False)
        start_disk = time.monotonic()
        disk_retriever = get_bm25_retriever(db, "it", k=3)
        duration_disk = time.monotonic() - start_disk
        print(f"[Test] Disk-cache reload took: {duration_disk:.2f}s")
        self.assertIsNotNone(disk_retriever, "Disk cache must reload valid retriever")
        self.assertLess(duration_disk, 2.5, "Disk cache reload must take less than 2.5s")

        # 4. Test actual search invocation
        query = "Convolutional neural network ResNet deep learning architecture"
        results = disk_retriever.invoke(query)
        print(f"[Test] Query '{query}' returned {len(results)} chunks")
        self.assertEqual(len(results), 3, "Retriever must return top-k=3 documents")
        self.assertTrue(any("resnet" in r.page_content.lower() or "neural" in r.page_content.lower() or "learning" in r.page_content.lower() for r in results), "Results must contain relevant terms")

if __name__ == "__main__":
    unittest.main()

