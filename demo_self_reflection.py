import os
import sys
import time

# Force UTF-8 encoding on standard streams if possible
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

# Create a class to write to both stdout and a log file without encoding crashes
class TeeLogger(object):
    def __init__(self, filepath):
        self.terminal = sys.stdout
        self.log = open(filepath, "w", encoding="utf-8")
        
    def write(self, message):
        try:
            self.terminal.write(message)
        except UnicodeEncodeError:
            # Replace characters that console cannot print on Windows cp1252
            safe_msg = message.encode('ascii', errors='replace').decode('ascii')
            self.terminal.write(safe_msg)
        self.log.write(message)
        self.terminal.flush()
        self.log.flush()
        
    def flush(self):
        self.terminal.flush()
        self.log.flush()

# Set up the logger before other imports to capture their prints/logs
log_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "self_reflection_demo.log")
logger_tee = TeeLogger(log_filepath)
sys.stdout = logger_tee
sys.stderr = logger_tee

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Let's import local_rag and ChatOllama class
import local_rag
from langchain_ollama import ChatOllama
from agent.graph import create_agent_graph
from langchain_core.messages import AIMessage

# Save original invoke method from the class
original_llm_invoke = ChatOllama.invoke

# Counter to count grader calls
grader_calls = 0

def mock_llm_invoke(self, prompt, *args, **kwargs):
    global grader_calls
    # Convert prompt to string
    prompt_str = str(prompt)
    if "grounded" in prompt_str and "useful" in prompt_str:
        grader_calls += 1
        print(f"\n[DEMO INTERCEPT] Joint Grader called (Attempt #{grader_calls})")
        if grader_calls == 1:
            print("[DEMO INTERCEPT] Simulating Hallucination Detected (grounded: no, useful: yes)")
            return AIMessage(content='{"grounded": "no", "useful": "yes"}')
        else:
            print("[DEMO INTERCEPT] Simulating Corrected Answer (grounded: yes, useful: yes)")
            return AIMessage(content='{"grounded": "yes", "useful": "yes"}')
    
    # Otherwise, call original Qwen LLM
    return original_llm_invoke(self, prompt, *args, **kwargs)

# Apply the class-level monkey patch
ChatOllama.invoke = mock_llm_invoke

def main():
    print("=" * 80)
    print("DEMONSTRATION OF AGENTIC RAG SELF-REFLECTION LOOP (LANGGRAPH)")
    print("=" * 80)
    
    # Initialize the compiled LangGraph Agent Graph
    print("[*] Compiling LangGraph Agent Graph...")
    app = create_agent_graph()
    
    # Setup inputs for an agentic reflection case
    question = "So sánh hiệu năng sai số MSE giữa mô hình Transformer và LSTM tại Chương 4."
    inputs = {
        "question": question,
        "original_question": None,
        "chat_history": [],
        "preferred_domain": "it",
        "use_tavily": False,
        "export_to_workspace": False,
        "expert_required": False,
        "python_repl": False,
        "web_fallback": False,
        "documents": [
            "--- Source: Ket_Qua_Thuc_Nghiem.pdf (Page 22) ---\nMô hình Transformer đạt chỉ số MSE là 0.012 sau 50 epochs huấn luyện."
        ],
        "generation": "",
        "structured_data": None,
        "selected_doc": None  # Set to None so it does NOT skip the Joint Grader
    }
    
    config = {"configurable": {"thread_id": "demo_reflection_thread"}, "recursion_limit": 10}
    
    print(f"\n[*] User Question: {question}")
    print("[*] Initial Context provided: Ket_Qua_Thuc_Nghiem.pdf (Page 22)")
    print("\n--- Starting LangGraph Invocation ---")
    
    start_time = time.time()
    try:
        final_state = app.invoke(inputs, config=config)
        end_time = time.time()
        print("\n--- LangGraph Invocation Completed ---")
        print(f"[*] Elapsed Time: {end_time - start_time:.2f}s")
        print(f"[*] Final Retry Count (Loops): {final_state.get('retry_count', 0)}")
        print("\n[Final Answer]:")
        print(final_state.get("generation"))
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n[-] Execution failed: {e}")
        
    print("=" * 80)

if __name__ == "__main__":
    main()
