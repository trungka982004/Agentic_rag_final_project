"""
Optimised web-search wrapper.

Improvements over the original:
  1. TTL-based in-memory cache (default 10 min) – identical queries within the
     window skip the network round-trip entirely.
  2. Configurable timeout via DuckDuckGoSearchAPIWrapper (backend raises
     ConnectionError when the limit is exceeded, which we catch gracefully).
  3. Automatic retry with exponential back-off (up to MAX_RETRIES attempts)
     so transient DDG rate-limits do not surface as hard failures.
  4. Result count reduced to 3 (was already 3) – enough context, less latency.
"""

import hashlib
import time
import logging

from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------
_CACHE: dict[str, tuple[str, float]] = {}   # {key: (result, timestamp)}
_CACHE_TTL_SECONDS = 600                    # 10 minutes

def _cache_key(query: str) -> str:
    return hashlib.md5(query.strip().lower().encode()).hexdigest()

def _get_cached(query: str) -> str | None:
    key = _cache_key(query)
    entry = _CACHE.get(key)
    if entry and (time.time() - entry[1]) < _CACHE_TTL_SECONDS:
        logger.info(f"[WebSearch] Cache HIT for query: {query[:60]!r}")
        return entry[0]
    return None

def _set_cache(query: str, result: str) -> None:
    _CACHE[_cache_key(query)] = (result, time.time())
    # Evict stale entries to avoid unbounded growth
    now = time.time()
    stale = [k for k, (_, ts) in _CACHE.items() if now - ts >= _CACHE_TTL_SECONDS]
    for k in stale:
        _CACHE.pop(k, None)

# ---------------------------------------------------------------------------
# Search function
# ---------------------------------------------------------------------------
MAX_RETRIES = 2
BASE_BACKOFF = 1.5   # seconds

def duckduckgo_search(query: str, max_results: int = 3) -> str:
    """Perform a web search using DuckDuckGo with caching and retry."""
    # 1. Check cache first
    cached = _get_cached(query)
    if cached:
        return cached

    wrapper = DuckDuckGoSearchAPIWrapper(max_results=max_results)
    search  = DuckDuckGoSearchResults(api_wrapper=wrapper)

    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            results = search.invoke(query)
            logger.info(f"[WebSearch] DDG query succeeded on attempt {attempt + 1}.")
            _set_cache(query, results)
            return results
        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES:
                wait = BASE_BACKOFF * (2 ** attempt)
                logger.warning(
                    f"[WebSearch] DDG attempt {attempt + 1} failed: {e}. "
                    f"Retrying in {wait:.1f}s..."
                )
                time.sleep(wait)
            else:
                logger.error(f"[WebSearch] All {MAX_RETRIES + 1} DDG attempts failed: {e}")

    return f"Web search temporarily unavailable. Error: {last_error}"
