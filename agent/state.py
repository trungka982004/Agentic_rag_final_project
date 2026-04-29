from typing import TypedDict, List, Optional

class GraphState(TypedDict):
    question: str                # User query
    domain: str                  # Classified domain
    documents: List[str]         # Context documents retrieved
    web_fallback: bool           # Flag for web search
    expert_required: bool        # Flag for expert consultation
    generation: str              # Generated answer
    use_tavily: bool             # Flag to enable/disable Tavily search
