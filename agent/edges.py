from agent.state import GraphState

def route_question(state: GraphState):
    """Route question to web search, expert consult, local RAG, or Python REPL."""
    print("--- ROUTE QUESTION ---")
    if state.get("python_repl"):
        print("[*] Routing to Python REPL.")
        return "python_repl"
    elif state.get("expert_required"):
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

from local_rag import llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import json

def parse_json_from_llm(raw_output: str) -> dict:
    cleaned = raw_output.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1:
        cleaned = cleaned[start:end+1]
        
    try:
        return json.loads(cleaned)
    except Exception:
        # Robust fallback parser if json.loads fails
        res = {}
        cleaned_lower = cleaned.lower()
        if "grounded" in cleaned_lower:
            res["grounded"] = "no" if "grounded" in cleaned_lower and '"no"' in cleaned_lower or "'no'" in cleaned_lower else "yes"
        if "useful" in cleaned_lower:
            res["useful"] = "no" if "useful" in cleaned_lower and '"no"' in cleaned_lower or "'no'" in cleaned_lower else "yes"
        return res

def grade_generation_v_documents_and_question(state: GraphState):
    """
    Determines whether the generation is grounded in the document and answers question
    using a unified Joint Grader to minimize latency (saving 1 LLM call).
    """
    print("--- JOINT EVALUATION (HALLUCINATION & RELEVANCE GRADER) ---")
    question = state["question"]
    documents = state.get("documents", [])
    generation = state["generation"]
    retry_count = state.get("retry_count", 0)
    max_retries = 2

    # 1. Joint Grader Prompt
    joint_grader_prompt = ChatPromptTemplate.from_template(
        "You are an expert evaluator assessing the quality of an assistant's answer.\n"
        "Here is the retrieved context/facts:\n"
        "-------\n"
        "{documents}\n"
        "-------\n"
        "Here is the user's question:\n"
        "-------\n"
        "{question}\n"
        "-------\n"
        "Here is the assistant's generated answer:\n"
        "-------\n"
        "{generation}\n"
        "-------\n"
        "Perform a strict analysis on two criteria:\n"
        "1. Groundedness (Is the answer supported by and grounded in the retrieved facts? If the facts are empty, answer 'yes' for this criterion. Answer 'yes' or 'no').\n"
        "2. Usefulness (Does the answer resolve and fully address the user's question? Answer 'yes' or 'no').\n\n"
        "Respond ONLY in raw JSON format with the following keys and values, and do not include any markdown code blocks or explanations:\n"
        "{{\n"
        "  \"grounded\": \"yes\"/\"no\",\n"
        "  \"useful\": \"yes\"/\"no\"\n"
        "}}\n"
        "Do not include any explanation or extra text."
    )
    
    joint_chain = joint_grader_prompt | llm | StrOutputParser()
    context = "\n\n".join(documents) if documents else "No documents."
    
    try:
        print("[*] Calling Joint Grader...")
        raw_res = joint_chain.invoke({
            "documents": context,
            "question": question,
            "generation": generation
        })
        print(f"[*] Joint Grader raw response: {repr(raw_res.strip())}")
        decision = parse_json_from_llm(raw_res)
        grounded = decision.get("grounded", "yes").strip().lower()
        useful = decision.get("useful", "yes").strip().lower()
    except Exception as e:
        print(f"[*] Joint grading failed: {e}. Defaulting to safe values.")
        grounded = "yes"
        useful = "yes"

    print(f"[*] Evaluation result -> Grounded: {grounded.upper()}, Useful: {useful.upper()}")

    if "yes" in grounded:
        if "yes" in useful:
            print("[*] Decision: Generation is grounded and answers the question.")
            return "useful"
        else:
            if retry_count >= max_retries:
                print(f"[*] Max retries ({max_retries}) reached. Accepting useful fallback to prevent loop.")
                return "useful"
            print("[*] Decision: Generation does not address the question.")
            return "not useful"
    else:
        if retry_count >= max_retries:
            print(f"[*] Max retries ({max_retries}) reached. Accepting grounded fallback to prevent loop.")
            return "useful"
        print("[*] Decision: Generation is not grounded (hallucination suspicion), retry.")
        return "not supported"

def decide_to_export(state: GraphState):
    """Decides whether to export the result to Google Workspace."""
    print(f"[Export Debug] decide_to_export state: keys={list(state.keys())}, export_to_workspace={state.get('export_to_workspace')}")
    if state.get("export_to_workspace"):
        print("[*] Export flag is ON. Routing to Export Report node.")
        return "export"
    print("[*] Export flag is OFF. Ending.")
    return "end"
