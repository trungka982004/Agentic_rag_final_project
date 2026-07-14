"""
Optimised Tavily expert-search wrapper.

Improvements:
  1. TTL-based in-memory cache (10 min) – avoids re-billing the same query.
  2. Configurable result count (default 3) with 'advanced' depth.
  3. Graceful error handling with structured logging.
"""

import os
import hashlib
import time
import logging
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults

load_dotenv()
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# TTL Cache
# ---------------------------------------------------------------------------
_CACHE: dict[str, tuple[str, float]] = {}
_CACHE_TTL_SECONDS = 600   # 10 minutes


def _cache_key(query: str) -> str:
    return hashlib.md5(query.strip().lower().encode()).hexdigest()


def _get_cached(query: str) -> str | None:
    key = _cache_key(query)
    entry = _CACHE.get(key)
    if entry and (time.time() - entry[1]) < _CACHE_TTL_SECONDS:
        logger.info(f"[ExpertSearch] Cache HIT for query: {query[:60]!r}")
        return entry[0]
    return None


def _set_cache(query: str, result: str) -> None:
    _CACHE[_cache_key(query)] = (result, time.time())
    now = time.time()
    stale = [k for k, (_, ts) in _CACHE.items() if now - ts >= _CACHE_TTL_SECONDS]
    for k in stale:
        _CACHE.pop(k, None)


# ---------------------------------------------------------------------------
# Search function
# ---------------------------------------------------------------------------

def get_expert_answer(query: str, max_results: int = 3) -> str:
    """Uses Tavily API for complex or time-sensitive queries with caching."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key or api_key == "your_tavily_api_key_here":
        return "Tavily API key not configured. Please add it to .env file."

    # Check cache
    cached = _get_cached(query)
    if cached:
        return cached

    search = TavilySearchResults(
        max_results=max_results,
        search_depth="advanced",
    )

    try:
        results = search.invoke(query)
        if isinstance(results, list):
            answer = " ".join([r.get("content", "") for r in results])
        elif isinstance(results, dict):
            raw_answer = results.get("answer", "")
            docs = results.get("results", [])
            docs_content = " ".join([d.get("content", "") for d in docs])
            answer = f"Answer: {raw_answer}\nContext: {docs_content}"
        else:
            answer = str(results)

        _set_cache(query, answer)
        logger.info(f"[ExpertSearch] Tavily query succeeded for: {query[:60]!r}")
        return answer
    except Exception as e:
        logger.error(f"[ExpertSearch] Error communicating with Tavily API: {e}")
        return f"Error communicating with Tavily API: {e}"
