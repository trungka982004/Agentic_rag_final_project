from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

def duckduckgo_search(query: str) -> str:
    """Perform a web search using DuckDuckGo."""
    wrapper = DuckDuckGoSearchAPIWrapper(max_results=3)
    search = DuckDuckGoSearchResults(api_wrapper=wrapper)
    try:
        results = search.invoke(query)
        return results
    except Exception as e:
        return f"Error during web search: {e}"
