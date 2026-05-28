import sys
# Force sys.stdout and sys.stdin to use UTF-8 to prevent cp1252/cp437 encoding errors on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stdin.reconfigure(encoding='utf-8')
except AttributeError:
    pass

from agent.graph import create_agent_graph

def main():
    print("=== AGENTIC RAG SYSTEM - PHASE 3 (AGENTIC TIER) ===")
    print("System active. Tier 1: Local Chroma, Tier 2: DuckDuckGo, Tier 3: Tavily")
    print("Type 'exit' to quit.\n")

    app = create_agent_graph()

    while True:
        query = input("\nUser Question: ").strip()
        if query.lower() in ["exit", "quit", "q"]:
            break

        if not query:
            continue

        import uuid
        # Đồng loạt các flag đều khởi tạo là ON (True)
        inputs = {
            "question": query,
            "use_tavily": True,
            "export_to_workspace": True,
            "expert_required": True,
            "python_repl": True,
            "web_fallback": True,
            "documents": [],           # Reset thread documents state to avoid duplicates
            "generation": "",          # Reset thread generation state to avoid duplicates
            "structured_data": None    # Reset thread structured data state to avoid duplicates
        }

        print("\n" + "="*50)
        # Run the LangGraph app with a fresh unique thread ID to prevent state accumulation
        config = {"configurable": {"thread_id": str(uuid.uuid4())}, "recursion_limit": 10}
        final_state = app.invoke(inputs, config=config)

        # In báo cáo kết quả phân tích và phán đoán các flag
        print("\n--- Flag Selection Report ---")
        print(f"🚩 Trạng thái Flag cuối cùng được chọn cho truy vấn này:")
        print(f"   - expert_required (Tavily Expert Search) : {'🟢 ON (Cần thiết)' if final_state.get('expert_required') else '🔴 OFF (Đã tắt)'}")
        print(f"   - python_repl (Thực thi tính toán Python) : {'🟢 ON (Cần thiết)' if final_state.get('python_repl') else '🔴 OFF (Đã tắt)'}")
        print(f"   - web_fallback (Dự phòng tìm kiếm Web)    : {'🟢 ON (Cần thiết)' if final_state.get('web_fallback') else '🔴 OFF (Đã tắt)'}")
        print(f"   - export_to_workspace (Xuất Workspace)    : {'🟢 ON (Cần thiết)' if final_state.get('export_to_workspace') else '🔴 OFF (Đã tắt)'}")
        print("-" * 30)

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
