from agent.state import GraphState
from tools.web_search import duckduckgo_search
from tools.expert_search import get_expert_answer
from tools.google_workspace import export_to_google_docs, export_to_google_sheets
from tools.formatter import format_agent_output
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
    
    return {"domain": domain, "expert_required": expert_required, "python_repl": python_repl}

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
    You are a professional scientific assistant. Use the following [CONTEXT] to answer the user's [QUESTION].
    
    MANDATORY RULES:
    1. Only use the information provided in the [CONTEXT]. Do not invent external knowledge.
    2. If the [CONTEXT] does not contain enough information, state: "I'm sorry, the provided documents do not contain enough information to answer this question."
    3. Your answer must be clear, structured, and highly accurate.
    4. Provide citations whenever possible.

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
        "Use print() to output the final answer.\n\nProblem: {question}"
    )
    chain = prompt | llm | StrOutputParser()
    
    try:
        code = chain.invoke({"question": question}).replace("```python", "").replace("```", "").strip()
        logger.info(f"[*] Generated Code:\n{code}")
        
        repl = PythonREPL()
        result = repl.run(code)
        answer = f"**Executed Python Code:**\n```python\n{code}\n```\n**Result:**\n{result}"
    except Exception as e:
        logger.error(f"Python REPL execution failed: {e}")
        answer = f"**Failed to execute Python logic.** Error: {e}"

    return {"generation": format_agent_output(answer)}

def export_report_node(state: GraphState):
    """Exports the generated answer to Google Docs and Google Sheets."""
    logger.info("--- EXPORT REPORT NODE ---")
    question = state["question"]
    generation = state.get("generation", "")

    if not generation:
        return {"generation": "[Export] No content available to export."}

    # Export to Google Docs
    doc_title = f"RAG Report: {question[:60]}"
    doc_result = export_to_google_docs(title=doc_title, content=generation)

    # Export summary to Google Sheets
    sheet_title = f"RAG Summary: {question[:50]}"
    sheet_data = [
        ["Field", "Value"],
        ["Question", question],
        ["Report Excerpt", generation[:1000] + "..."],
        ["Status", "Generated & Exported"]
    ]
    sheet_result = export_to_google_sheets(title=sheet_title, data=sheet_data)

    export_summary = f"{doc_result}\n{sheet_result}"
    return {"generation": generation + "\n\n---\n**System Note:** " + export_summary}
