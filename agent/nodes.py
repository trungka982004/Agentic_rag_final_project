from agent.state import GraphState
from tools.web_search import duckduckgo_search
from tools.expert_search import get_expert_answer
from tools.google_workspace import export_to_google_docs, export_to_google_sheets, upload_image_to_drive
from tools.mermaid_renderer import render_mermaid_to_image
from tools.formatter import format_agent_output
import re
import os

from local_rag import classify_domain, retrieve_context, llm, logger
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_experimental.utilities import PythonREPL

# --- CONSTANTS ---
EXPERT_KEYWORDS = ["compare", "latest", "news", "trend", "so sánh", "mới nhất", "xu hướng", "tin tức"]
PYTHON_KEYWORDS = ["python", "code", "tính toán", "calculate", "giải phương trình", "vẽ biểu đồ", "plot"]

def router_node(state: GraphState):
    """Classifies domain and decides initial path."""
    logger.info("--- ROUTER NODE ---")
    question = state["question"]
    domain = classify_domain(question)
    
    logger.info(f"[*] Classified Domain: {domain.upper()}")
    
    use_tavily = state.get("use_tavily", True)
    expert_required = False
    
    if use_tavily:
        expert_required = any(kw in question.lower() for kw in EXPERT_KEYWORDS)
    else:
        logger.info("[*] Tavily trigger is OFF. Forcing Local/Web search track.")
    
    python_repl = any(kw in question.lower() for kw in PYTHON_KEYWORDS)
    
    # Detect export intent
    export_keywords = ["export", "xuất", "lưu", "google docs", "google sheets", "báo cáo"]
    export_to_workspace = any(kw in question.lower() for kw in export_keywords)
    
    return {
        "domain": domain, 
        "expert_required": expert_required, 
        "python_repl": python_repl,
        "export_to_workspace": export_to_workspace
    }

def retrieve_local_node(state: GraphState):
    """Retrieves documents from local ChromaDB."""
    logger.info("--- RETRIEVE LOCAL NODE ---")
    question = state["question"]
    domain = state["domain"]
    
    context = retrieve_context(question, domain)
    
    # Check for failure messages in context
    if any(msg in context for msg in ["No database found", "No relevant information", "Error occurred"]):
        docs = []
    else:
        docs = [context]
        
    return {"documents": docs}

def grade_documents_node(state: GraphState):
    """Grades the retrieved documents for relevance."""
    logger.info("--- GRADE DOCUMENTS NODE ---")
    question = state["question"]
    documents = state.get("documents", [])
    
    if not documents:
        logger.info("[*] No local documents found. Falling back to Web Search.")
        return {"web_fallback": True}
        
    prompt = ChatPromptTemplate.from_template(
        "You are a grader assessing relevance of a retrieved document to a user question.\n"
        "Here is the retrieved document: \n\n {document} \n\n"
        "Here is the user question: {question}\n"
        "If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant.\n"
        "Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."
    )
    
    chain = prompt | llm | StrOutputParser()
    try:
        score = chain.invoke({"question": question, "document": documents[0]}).strip().lower()
        if "yes" in score:
            logger.info("[*] Local documents are RELEVANT.")
            return {"web_fallback": False}
    except Exception as e:
        logger.error(f"Grading failed: {e}")
    
    logger.info("[*] Local documents are NOT relevant. Falling back to Web Search.")
    return {"web_fallback": True}

def web_search_node(state: GraphState):
    """Uses DuckDuckGo to search the web."""
    logger.info("--- WEB SEARCH NODE ---")
    question = state["question"]
    
    results = duckduckgo_search(question)
    logger.info("[*] Web Search completed.")
    
    documents = state.get("documents", [])
    documents.append(f"--- Web Search Results ---\n{results}")
    
    return {"documents": documents}

def expert_consult_node(state: GraphState):
    """Consults Tavily API for complex questions."""
    logger.info("--- EXPERT CONSULT NODE ---")
    question = state["question"]
    
    logger.info("[*] Consulting Tavily API...")
    answer = get_expert_answer(question)
    
    return {"generation": format_agent_output(answer)}

def generate_node(state: GraphState):
    """Generates the final answer using LLM."""
    logger.info("--- GENERATE NODE ---")
    question = state["question"]
    documents = state.get("documents", [])
    
    context = "\n\n".join(documents)
    
    template = """
    You are a professional technical assistant. Answer the [QUESTION] based ONLY on the provided [CONTEXT].
    
    MANDATORY RULES:
    1. BE CONCISE. Do not explain your plan or describe how you will do things. Just provide the final result.
    2. NEVER mention "Google Forms", "API", or "environment details".
    3. If calculation results are present in [CONTEXT], use them as the primary answer.
    4. If the user asked for a diagram, provide EXACTLY ONE Mermaid code block wrapped in ```mermaid.
    5. Do not repeat information.
    6. Return ONLY the final report content.

    [CONTEXT]:
    {context}

    [QUESTION]:
    {question}

    [ANSWER]:
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    
    try:
        response = chain.invoke({"question": question, "context": context})
        return {"generation": format_agent_output(response)}
    except Exception as e:
        logger.error(f"Generation node failed: {e}")
        return {"generation": "Error occurred during generation."}

def python_repl_node(state: GraphState):
    """Executes Python code to answer math/coding queries."""
    logger.info("--- PYTHON REPL NODE ---")
    question = state["question"]
    
    prompt = ChatPromptTemplate.from_template(
        "You are an expert Python programmer. Write Python code to solve the following problem. "
        "Return ONLY the raw python code. Do NOT wrap it in markdown block, do NOT include explanations. "
        "Use print() to output the final answer.\n\n"
        "IMPORTANT: Only use standard libraries or common ones like numpy. "
        "Do NOT attempt to generate diagrams (like Mermaid) or reports (like pyodoc) inside the Python code. "
        "Just output the calculated values.\n\n"
        "Problem: {question}"
    )
    chain = prompt | llm | StrOutputParser()
    
    try:
        code = chain.invoke({"question": question}).replace("```python", "").replace("```", "").strip()
        logger.info(f"[*] Generated Code:\n{code}")
        
        repl = PythonREPL()
        result = repl.run(code).strip()
        
        # Prepare structured data for Sheets
        structured_data = [["Result Type", "Value"]]
        structured_data.append(["Computation Output", result])
        
        answer = f"--- Python Computation Result ---\nCode:\n{code}\nResult:\n{result}"
        docs = state.get("documents", [])
        docs.append(answer)
        
        return {"documents": docs, "structured_data": structured_data}
    except Exception as e:
        logger.error(f"Python REPL execution failed: {e}")
        answer = f"**Failed to execute Python logic.** Error: {e}"
        return {"generation": format_agent_output(answer)}

def export_report_node(state: GraphState):
    """Exports the generated answer to Google Docs and Google Sheets."""
    logger.info("--- EXPORT REPORT NODE ---")
    question = state["question"]
    generation = state.get("generation", "")
    structured_data = state.get("structured_data")

    if not generation:
        return {"generation": "[Export] No content available to export."}

    # 1. Detect and Render UNIQUE Mermaid Diagrams
    image_urls = []
    # Use set to deduplicate identical blocks
    mermaid_blocks = list(set(re.findall(r"```mermaid\s*\n(.*?)\n```", generation, re.DOTALL)))
    
    print(f"[Export Debug] Found {len(mermaid_blocks)} unique mermaid blocks.")
    
    for mmd_code in mermaid_blocks:
        image_path = render_mermaid_to_image(mmd_code.strip())
        if image_path:
            drive_url = upload_image_to_drive(image_path)
            if drive_url:
                image_urls.append(drive_url)
            if os.path.exists(image_path):
                os.remove(image_path)

    # 2. Export to Google Docs
    doc_title = f"RAG Report: {question[:60]}"
    doc_result = export_to_google_docs(title=doc_title, content=generation, image_urls=image_urls)

    # 3. Export to Google Sheets
    sheet_title = f"RAG Data: {question[:50]}"
    sheet_data = structured_data if structured_data else [["Field", "Value"], ["Question", question], ["Status", "Completed"]]
    sheet_result = export_to_google_sheets(title=sheet_title, data=sheet_data)

    export_summary = f"{doc_result}\n{sheet_result}"
    return {"generation": generation + "\n\n---\n**System Note:** " + export_summary}
