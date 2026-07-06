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
        
    return json.loads(cleaned)

# --- CONSTANTS ---
EXPERT_KEYWORDS = ["compare", "latest", "news", "trend", "so sánh", "mới nhất", "xu hướng", "tin tức"]
PYTHON_KEYWORDS = ["python", "code", "tính toán", "calculate", "giải phương trình", "vẽ biểu đồ", "plot"]

def condense_question(question: str, chat_history: list) -> str:
    """Condenses an ambiguous question using chat history to make it standalone."""
    if not chat_history:
        return question
        
    logger.info("[*] Chat history detected. Condensing follow-up question...")
    
    # Form chat history string
    history_str = ""
    for turn in chat_history:
        usr = turn.get("user", "")
        agt = turn.get("agent", "")
        # Clean agt if it has mermaid or is too long to save context
        clean_agt = re.sub(r"```mermaid\s*(.*?)\s*```", "[Diagram]", agt, flags=re.DOTALL)
        if len(clean_agt) > 200:
            clean_agt = clean_agt[:200] + "..."
        history_str += f"User: {usr}\nAgent: {clean_agt}\n\n"
        
    prompt = ChatPromptTemplate.from_template(
        "Read the following chat history and the latest user question.\n"
        "If the latest user question references the previous conversation (e.g. using 'it', 'above', 'that', 'them', 'nó', 'đó', 'trên', 'này' or implicit references), "
        "write a fully standalone, search-friendly version of the question in the same language.\n"
        "If it is already standalone, keep it exactly as-is.\n\n"
        "Rules:\n"
        "1. Do NOT answer the question.\n"
        "2. Output ONLY the raw condensed question, no commentary, no quotes, no markdown wrappers.\n\n"
        "[CHAT HISTORY]:\n"
        "{history_str}\n"
        "[LATEST USER QUESTION]: {question}\n\n"
        "[STANDALONE QUESTION]:"
    )
    
    chain = prompt | llm | StrOutputParser()
    try:
        condensed = chain.invoke({"history_str": history_str, "question": question}).strip().strip('"').strip("'")
        logger.info(f"[*] Original Question: '{question}' -> Condensed Standalone Question: '{condensed}'")
        return condensed
    except Exception as e:
        logger.error(f"Failed to condense question: {e}")
        return question

def router_node(state: GraphState):
    """Classifies domain and decides initial path."""
    logger.info("--- ROUTER NODE ---")
    question = state["question"]
    chat_history = state.get("chat_history", [])
    preferred_domain = state.get("preferred_domain")
    
    # Condense the question using conversation history
    question = condense_question(question, chat_history)
    
    if preferred_domain and preferred_domain != 'all':
        domain = preferred_domain.strip().lower()
        logger.info(f"[*] Bypassing classification. Using user preferred domain: {domain.upper()}")
    else:
        domain = classify_domain(question)
        logger.info(f"[*] Classified Domain: {domain.upper()}")
    
    # Keyword-based configurations (All default to ON)
    expert_required = True
    python_repl = True
    web_fallback = True
    export_to_workspace = True
    
    export_keywords = ["export", "xuất", "lưu", "google docs", "google sheets", "báo cáo", "report", "document", "doc", "sheet", "excel"]
    
    # Switch to OFF if keywords are not present in the user question
    if not any(kw in question.lower() for kw in EXPERT_KEYWORDS):
        expert_required = False
        
    if not any(kw in question.lower() for kw in PYTHON_KEYWORDS):
        python_repl = False
        
    if not any(kw in question.lower() for kw in export_keywords):
        export_to_workspace = False
        
    logger.info(f"[*] Decided Flags -> expert_required: {expert_required}, python_repl: {python_repl}, web_fallback: {web_fallback}, export_to_workspace: {export_to_workspace}")
        
    return {
        "question": question,
        "domain": domain, 
        "expert_required": expert_required, 
        "python_repl": python_repl,
        "web_fallback": web_fallback,
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
    
    documents = state.get("documents", [])
    documents.append(f"--- Expert Search Results ---\n{answer}")
    
    return {"documents": documents}

def generate_node(state: GraphState):
    """Generates the final answer using LLM."""
    logger.info("--- GENERATE NODE ---")
    question = state["question"]
    documents = state.get("documents", [])
    retry_count = state.get("retry_count", 0)
    chat_history = state.get("chat_history", [])
    
    context = "\n\n".join(documents)
    
    # Format chat history to inject into prompt context
    history_str = ""
    if chat_history:
        history_str = "--- CONVERSATION HISTORY ---\n"
        for turn in chat_history:
            usr = turn.get("user", "")
            agt = turn.get("agent", "")
            # Strip out raw Mermaid blocks to avoid massive token bloat
            clean_agt = re.sub(r"```mermaid\s*(.*?)\s*```", "[Diagram]", agt, flags=re.DOTALL)
            history_str += f"User: {usr}\nAgent: {clean_agt}\n\n"
        history_str += "-------------------------\n\n"
        
    template = """
    You are a professional technical assistant. Answer the [QUESTION] based on the provided [CONTEXT] and the past [CONVERSATION HISTORY] (if any).
    
    MANDATORY RULES:
    1. BE CONCISE. Do not explain your plan or describe how you will do things. Just provide the final result.
    2. NEVER mention "Google Forms", "API", or "environment details".
    3. If calculation results are present in [CONTEXT], use them as the primary answer.
    4. If a Python code execution result is present in [CONTEXT], focus on explaining the result and output. DO NOT repeat or rewrite the raw Python code block (```python ... ```) in your answer.
    5. If the user asked for a diagram, you MUST provide BOTH a detailed, well-structured textual report/explanation answering the question first, and then append EXACTLY ONE Mermaid code block wrapped in ```mermaid at the very end of your answer. Do not output only the diagram.
    6. Do not repeat information.
    7. NEVER explain the rules, reference your system instructions, or mention any prompt constraints to the user. Do not output any meta-commentary or reflection notes. Just output the clean final answer.
    8. Return ONLY the final report content.
 
    [CONVERSATION HISTORY]:
    {history}

    [CONTEXT]:
    {context}
 
    [QUESTION]:
    {question}
 
    [ANSWER]:
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    
    try:
        response = chain.invoke({"question": question, "context": context, "history": history_str})
        formatted_response = format_agent_output(response)
        
        # Automatically extract markdown tables to populate structured_data for Sheets
        from tools.formatter import parse_markdown_table
        structured_data = parse_markdown_table(formatted_response)
        if structured_data:
            logger.info(f"[*] Automatically parsed comparison table for Sheets: {len(structured_data)} rows.")
            
        return {
            "generation": formatted_response,
            "structured_data": structured_data,
            "retry_count": retry_count + 1
        }
    except Exception as e:
        logger.error(f"Generation node failed: {e}")
        return {"generation": "Error occurred during generation.", "retry_count": retry_count + 1}

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

def generate_short_title(question: str, doc_type: str) -> str:
    """Generates a highly concise, clear, and professional title (max 8 words) for exported files."""
    if not llm:
        words = question.split()
        prefix = "Doc: " if doc_type == "docs" else "Sheet: "
        core_title = " ".join(words[:5])
        return f"{prefix}{core_title}"
        
    prompt = ChatPromptTemplate.from_template(
        "You are an expert technical editor. Create a highly concise, professional, "
        "and clear title (in the same language as the question, usually Vietnamese or English) "
        "for an exported Google {doc_type} file answering this question:\n"
        "Question: '{question}'\n\n"
        "Rules:\n"
        "1. The title MUST be extremely concise and clear.\n"
        "2. The entire title (including any prefix) MUST NOT exceed 8 words.\n"
        "3. Output ONLY the raw title without any quotes, punctuation, or markdown formatting.\n"
        "4. Avoid generic filler. It should directly represent the core topic (e.g., 'SRAM vs DRAM Comparison', 'ResNet Algorithm Analysis').\n"
        "5. Prepend a brief type prefix (e.g., 'Doc: ' for documents, 'Sheet: ' for spreadsheets) so it is clear."
    )
    chain = prompt | llm | StrOutputParser()
    try:
        title = chain.invoke({"question": question, "doc_type": "Doc" if doc_type == "docs" else "Spreadsheet"}).strip().strip('"').strip("'").strip()
        title = re.sub(r"^#+\s*", "", title)
        # Ensure under 8 words limit
        words = title.split()
        if len(words) > 8:
            title = " ".join(words[:8])
        return title
    except Exception as e:
        logger.error(f"Failed to generate short title: {e}")
        words = question.split()
        prefix = "Doc: " if doc_type == "docs" else "Sheet: "
        core_title = " ".join(words[:5])
        return f"{prefix}{core_title}"


def export_report_node(state: GraphState):
    """Exports the generated answer to Google Docs and Google Sheets based on user intent."""
    logger.info("--- EXPORT REPORT NODE ---")
    question = state["question"]
    generation = state.get("generation", "")
    structured_data = state.get("structured_data")

    if not generation:
        return {"generation": "[Export] No content available to export."}

    # Detect specific export formats requested by user
    question_lower = question.lower()
    has_docs_intent = any(kw in question_lower for kw in ["docs", "doc", "document", "văn bản", "tài liệu", "word"])
    has_sheets_intent = any(kw in question_lower for kw in ["sheets", "sheet", "bảng", "trang tính", "excel"])

    # Default is to export to both formats
    export_docs = True
    export_sheets = True

    # If the user explicitly specified formats, override the defaults
    if has_docs_intent or has_sheets_intent:
        export_docs = has_docs_intent
        export_sheets = has_sheets_intent

    logger.info(f"[*] Export Targets -> Docs: {export_docs}, Sheets: {export_sheets}")

    # 1. Detect and Render UNIQUE Mermaid Diagrams
    image_urls = []
    # Use set to deduplicate identical blocks
    mermaid_blocks = list(set(re.findall(r"```mermaid\s*(.*?)\s*```", generation, re.DOTALL)))
    
    print(f"[Export Debug] Found {len(mermaid_blocks)} unique mermaid blocks.")
    
    for mmd_code in mermaid_blocks:
        image_path = render_mermaid_to_image(mmd_code.strip())
        if image_path:
            drive_url = upload_image_to_drive(image_path)
            if drive_url:
                image_urls.append(drive_url)
            if os.path.exists(image_path):
                os.remove(image_path)

    import concurrent.futures

    export_summary_parts = []
    export_links = {"docs": None, "sheets": None}

    def run_docs_export():
        doc_title = generate_short_title(question, "docs")
        # Strip out raw Mermaid blocks completely so only the LLM's text and explanation remain in the body
        clean_content = re.sub(
            r"```mermaid\s*(.*?)\s*```", 
            "", 
            generation, 
            flags=re.DOTALL
        ).strip()
        
        # Build beautifully formatted document content including both the Question and the Answer
        doc_content = f"QUESTION:\n{question}\n\n"
        if clean_content:
            doc_content += f"ANSWER:\n{clean_content}\n"
        else:
            doc_content += "ANSWER:\n(Please refer to the diagram below)\n"
            
        return export_to_google_docs(title=doc_title, content=doc_content, image_urls=image_urls)

    def run_sheets_export():
        sheet_title = generate_short_title(question, "sheets")
        
        # For Sheets, we clean up any raw mermaid blocks from the text to make it more readable
        clean_generation = re.sub(
            r"```mermaid\s*(.*?)\s*```", 
            "[Diagram Rendered in Doc]", 
            generation, 
            flags=re.DOTALL
        ).strip()
        
        sheet_data = structured_data if structured_data else [
            ["Field", "Value"],
            ["Question", question],
            ["Answer", clean_generation],
            ["Status", "Completed"]
        ]
        return export_to_google_sheets(title=sheet_title, data=sheet_data)

    # Execute Google Docs and Google Sheets exports in parallel using ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {}
        if export_docs:
            futures["docs"] = executor.submit(run_docs_export)
        else:
            logger.info("[*] Google Docs export bypassed as per query instructions.")

        if export_sheets:
            futures["sheets"] = executor.submit(run_sheets_export)
        else:
            logger.info("[*] Google Sheets export bypassed as per query instructions.")

        # Wait for all exports to finish and extract links
        if "docs" in futures:
            try:
                doc_result = futures["docs"].result()
                export_summary_parts.append(doc_result)
                match = re.search(r"https?://\S+", doc_result)
                if match:
                    export_links["docs"] = match.group(0).rstrip(".")
            except Exception as e:
                logger.error(f"Google Docs export failed: {e}")
                export_summary_parts.append(f"[Export Error] Google Docs: {e}")

        if "sheets" in futures:
            try:
                sheet_result = futures["sheets"].result()
                export_summary_parts.append(sheet_result)
                match = re.search(r"https?://\S+", sheet_result)
                if match:
                    export_links["sheets"] = match.group(0).rstrip(".")
            except Exception as e:
                logger.error(f"Google Sheets export failed: {e}")
                export_summary_parts.append(f"[Export Error] Google Sheets: {e}")

    # Return clean generation and structured export links separately
    return {"generation": generation, "export_links": export_links}
