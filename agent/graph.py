from langgraph.graph import END, StateGraph, START
from agent.state import GraphState
from agent.nodes import (
    router_node,
    retrieve_local_node,
    grade_documents_node,
    web_search_node,
    expert_consult_node,
    generate_node
)
from agent.edges import route_question, decide_to_generate, grade_generation_v_documents_and_question
from langgraph.checkpoint.memory import MemorySaver

def create_agent_graph():
    workflow = StateGraph(GraphState)

    # Define the nodes
    workflow.add_node("router", router_node)
    workflow.add_node("retrieve_local", retrieve_local_node)
    workflow.add_node("grade_documents", grade_documents_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("expert_consult", expert_consult_node)
    workflow.add_node("generate", generate_node)

    # Build graph
    workflow.add_edge(START, "router")
    
    workflow.add_conditional_edges(
        "router",
        route_question,
        {
            "retrieve_local": "retrieve_local",
            "expert_consult": "expert_consult",
        }
    )
    
    workflow.add_edge("retrieve_local", "grade_documents")
    
    workflow.add_conditional_edges(
        "grade_documents",
        decide_to_generate,
        {
            "web_search": "web_search",
            "generate": "generate",
        }
    )
    
    workflow.add_edge("web_search", "generate")
    workflow.add_edge("expert_consult", END)
    
    workflow.add_conditional_edges(
        "generate",
        grade_generation_v_documents_and_question,
        {
            "not supported": "generate",
            "useful": END,
            "not useful": "web_search",
        }
    )

    # Compile with checkpointer for state management
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    return app
