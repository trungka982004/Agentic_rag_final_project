import os
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv

load_dotenv()

def get_expert_answer(query: str) -> str:
    """Uses Tavily API for complex or time-sensitive queries."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key or api_key == "your_tavily_api_key_here":
        return "Tavily API key not configured. Please add it to .env file."

    # Using Tavily for advanced deep search
    search = TavilySearchResults(
        max_results=3,
        search_depth="advanced"
    )
    
    try:
        results = search.invoke(query)
        if isinstance(results, list):
            return " ".join([r.get("content", "") for r in results])
        elif isinstance(results, dict):
            answer = results.get("answer", "")
            docs = results.get("results", [])
            docs_content = " ".join([d.get("content", "") for d in docs])
            return f"Answer: {answer}\nContext: {docs_content}"
        else:
            return str(results)
    except Exception as e:
        return f"Error communicating with Tavily API: {e}"
