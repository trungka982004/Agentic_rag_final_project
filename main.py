from agent.graph import create_agent_graph

def main():
    print("=== AGENTIC RAG SYSTEM - PHASE 3 (AGENTIC TIER) ===")
    print("System active. Tier 1: Local Chroma, Tier 2: DuckDuckGo, Tier 3: Tavily")
    print("Type 'exit' to quit.")
    print("Commands:")
    print("  /tavily on|off   - Enable/disable Tavily expert search")
    print("  /export on|off   - Enable/disable Google Workspace export\n")

    app = create_agent_graph()
    use_tavily = True
    export_to_workspace = False

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

        if query.lower() == "/export off":
            export_to_workspace = False
            print("[*] Google Workspace export is now OFF.")
            continue

        if query.lower() == "/export on":
            export_to_workspace = True
            print("[*] Google Workspace export is now ON. Results will be saved to Google Docs & Sheets.")
            continue

        if not query:
            continue

        import uuid
        inputs = {
            "question": query,
            "use_tavily": use_tavily,
            "export_to_workspace": export_to_workspace,
            "documents": [],           # Reset thread documents state to avoid duplicates
            "generation": "",          # Reset thread generation state to avoid duplicates
            "structured_data": None    # Reset thread structured data state to avoid duplicates
        }

        print("\n" + "="*50)
        # Run the LangGraph app with a fresh unique thread ID to prevent state accumulation
        config = {"configurable": {"thread_id": str(uuid.uuid4())}, "recursion_limit": 10}
        final_state = app.invoke(inputs, config=config)

        print("\n--- Final Answer ---")
        print(final_state.get("generation", "No answer generated."))
        
        # Display clean structured export links in the CLI if present
        export_links = final_state.get("export_links")
        if export_links:
            links_summary = []
            if export_links.get("docs"):
                links_summary.append(f"📄 Google Docs: {export_links['docs']}")
            if export_links.get("sheets"):
                links_summary.append(f"📊 Google Sheets: {export_links['sheets']}")
            if links_summary:
                print("\n" + "-"*30)
                print("✅ Exported Documents:")
                print("\n".join(links_summary))

        print("="*50 + "\n")

if __name__ == "__main__":
    main()
