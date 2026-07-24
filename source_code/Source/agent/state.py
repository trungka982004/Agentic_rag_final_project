from typing import TypedDict, List, Optional, Dict, Any

class GraphState(TypedDict):
    """Represents the shared state of the LangGraph execution workflow.

    Attributes:
        question: The user query, which may be normalized/corrected for search friendliness.
        original_question: The raw user input before any normalization or spelling corrections.
        chat_history: The list of prior conversational turns: [{"user": "...", "agent": "..."}].
        preferred_domain: User preferred domain (e.g., 'it', 'math'), bypassing classification.
        domain: The inferred category/domain (e.g., 'it', 'math', 'physics', 'electronics').
        documents: A list of retrieved context documents from local DB or external search.
        web_fallback: Flag indicating whether local DB grading failed and web search is required.
        expert_required: Flag indicating if query requires advanced search (Tavily).
        generation: The generated text response from the LLM.
        use_tavily: Boolean flag to enable or disable Tavily search capabilities.
        python_repl: Flag indicating whether the query involves complex math/code execution.
        export_to_workspace: Flag indicating if the user intends to export results to Workspace.
        structured_data: Extracted tabular data ready to be exported to Google Sheets.
        retry_count: Loop counter for self-correction retries during answer generation.
        export_links: Dictionary mapping document types to cloud URLs (e.g., {"docs": "...", "sheets": "..."}).
        selected_doc: Explicit target PDF filename requested by the user.
    """
    question: str
    original_question: Optional[str]
    chat_history: List[dict]
    preferred_domain: Optional[str]
    domain: str
    documents: List[str]
    web_fallback: bool
    expert_required: bool
    generation: str
    use_tavily: bool
    python_repl: bool
    export_to_workspace: bool
    structured_data: Optional[List[List[Any]]]
    retry_count: int
    export_links: Optional[Dict[str, Optional[str]]]
    selected_doc: Optional[str]
