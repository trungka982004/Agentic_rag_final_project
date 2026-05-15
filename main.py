from agent.graph import create_agent_graph

def main():
    print("=== AGENTIC RAG SYSTEM - PHASE 3 (AGENTIC TIER) ===")
    print("System active. Tier 1: Local Chroma, Tier 2: DuckDuckGo, Tier 3: Tavily")
    print("Type 'exit' to quit.")
    print("Type '/tavily off' to disable Tavily, or '/tavily on' to enable it.\n")
    
    app = create_agent_graph()
    use_tavily = True
    
    while True:
        query = input("\nUser Question: ").strip()
        if query.lower() in ["exit", "quit", "q"]:
            break
            
        if query.lower() == "/tavily off":
            use_tavily = False
            print("[*] Tavily trigger is now OFF.")
            continue
            
        if query.lower() == "/tavily on":
            use_tavily = True
            print("[*] Tavily trigger is now ON.")
            continue
        
        if not query:
            continue
            
        inputs = {"question": query, "use_tavily": use_tavily}
        
        print("\n" + "="*50)
        # Run the LangGraph app
        config = {"configurable": {"thread_id": "1"}}
        final_state = app.invoke(inputs, config=config)
        
        print("\n--- Final Answer ---")
        print(final_state.get("generation", "No answer generated."))
        print("="*50 + "\n")

if __name__ == "__main__":
    main()
