from agent.state import GraphState

def route_question(state: GraphState):
    """Route question to web search, expert consult, or local RAG."""
    print("--- ROUTE QUESTION ---")
    if state.get("expert_required"):
        print("[*] Routing to Expert Consultant (Tavily).")
        return "expert_consult"
    else:
        print("[*] Routing to Local VectorDB.")
        return "retrieve_local"

def decide_to_generate(state: GraphState):
    """Determines whether to generate an answer, or fall back to web search."""
    print("--- DECIDE TO GENERATE ---")
    if state.get("web_fallback"):
        print("[*] Decision: Fallback to Web Search.")
        return "web_search"
    else:
        print("[*] Decision: Generate Answer.")
        return "generate"
