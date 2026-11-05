import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from agent.state import GraphState
from agent.studio_nodes import (
    literature_matrix_node,
    citation_suggest_node,
    tone_polish_node,
    reviewer2_audit_node
)

logger = logging.getLogger(__name__)

def route_studio_task(state: GraphState) -> str:
    """Routes execution based on requested academic studio action mode."""
    task_mode = state.get("selected_doc") or "matrix" # re-use or parse query mode
    query = state.get("question", "").lower()
    
    if "audit" in query or "reviewer" in query or task_mode == "audit":
        return "reviewer2_audit"
    elif "polish" in query or "tone" in query or "grammar" in query or task_mode == "polish":
        return "tone_polish"
    elif "cite" in query or "citation" in query or "bibtex" in query or task_mode == "citation":
        return "citation_suggest"
    else:
        return "literature_matrix"

def create_studio_agent_graph():
    """Builds and compiles the specialized Academic Studio LangGraph agent."""
    workflow = StateGraph(GraphState)

    workflow.add_node("literature_matrix", literature_matrix_node)
    workflow.add_node("citation_suggest", citation_suggest_node)
    workflow.add_node("tone_polish", tone_polish_node)
    workflow.add_node("reviewer2_audit", reviewer2_audit_node)

    # Route at entrypoint
    workflow.add_conditional_edges(
        START,
        route_studio_task,
        {
            "literature_matrix": "literature_matrix",
            "citation_suggest": "citation_suggest",
            "tone_polish": "tone_polish",
            "reviewer2_audit": "reviewer2_audit",
        }
    )

    workflow.add_edge("literature_matrix", END)
    workflow.add_edge("citation_suggest", END)
    workflow.add_edge("tone_polish", END)
    workflow.add_edge("reviewer2_audit", END)

    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    return app
