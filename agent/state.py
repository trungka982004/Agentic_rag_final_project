from typing import TypedDict, List, Optional

class GraphState(TypedDict):
    question: str                # User query
    domain: str                  # Classified domain
    documents: List[str]         # Context documents retrieved
    web_fallback: bool           # Flag for web search
    expert_required: bool        # Flag for expert consultation
    generation: str              # Generated answer
    use_tavily: bool             # Flag to enable/disable Tavily search
    python_repl: bool            # Flag for Python REPL execution
    export_to_workspace: bool    # Flag to export result to Google Workspace
    structured_data: Optional[List[List]] # Data for Google Sheets
    retry_count: int             # Number of retries for generation loops
