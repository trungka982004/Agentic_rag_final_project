from typing import TypedDict, List, Optional

class GraphState(TypedDict):
    question: str                # User query (may be normalized/corrected)
    original_question: Optional[str] # Raw user input before normalization (None if unchanged)
    chat_history: List[dict]     # Conversation history: [{"user": "...", "agent": "..."}]
    preferred_domain: Optional[str] # Preferred domain sent by user
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
    export_links: Optional[dict] # URLs of exported documents (e.g. docs, sheets)
    selected_doc: Optional[str]  # Explicitly selected target PDF filename
