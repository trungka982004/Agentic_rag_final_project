import re
import os
import json
import logging
import concurrent.futures
from typing import List, Dict, Any, Optional, Tuple

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_experimental.utilities import PythonREPL

from agent.state import GraphState
from tools.web_search import duckduckgo_search
from tools.expert_search import get_expert_answer
from tools.google_workspace import export_to_google_docs, export_to_google_sheets, upload_image_to_drive
from tools.mermaid_renderer import render_mermaid_to_image
from tools.formatter import format_agent_output, parse_markdown_table
from tools.query_normalizer import normalize_query
from langchain_ollama import ChatOllama
from local_rag import classify_domain, retrieve_context, llm, logger, Config

# Constants for query routing heuristics
EXPERT_KEYWORDS = ["compare", "latest", "news", "trend", "so sánh", "mới nhất", "xu hướng", "tin tức"]
PYTHON_KEYWORDS = ["python code", "chạy python", "tính toán python", "vẽ biểu đồ python", "run python"]
EXPORT_KEYWORDS = ["export to google", "xuất sang google", "xuất google docs", "xuất google sheets", "xuất file docs", "xuất file sheets", "lưu vào google docs", "lưu vào google sheets", "export docs", "export sheets"]


def parse_json_from_llm(raw_output: str) -> Dict[str, Any]:
    """Parses a raw LLM output string to extract a valid JSON object.

    Args:
        raw_output: Raw text output from the language model.

    Returns:
        A dictionary containing parsed JSON data.
    """
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
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON content from LLM response: {e}")
        return {}


def condense_question(question: str, chat_history: List[Dict[str, Any]]) -> str:
    """Condenses a follow-up question by resolving context references using chat history.

    Args:
        question: The current follow-up question.
        chat_history: List of previous conversation turns.

    Returns:
        A standalone search-friendly question.
    """
    if not chat_history:
        return question
        
    logger.info("Chat history detected. Condensing follow-up question...")
    
    # Form chat history string for context injection
    history_str = ""
    for turn in chat_history:
        usr = turn.get("user", "")
        agt = turn.get("agent", "")
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
        logger.info(f"Original Question: '{question}' -> Standalone Question: '{condensed}'")
        return condensed
    except Exception as e:
        logger.error(f"Failed to condense question: {e}")
        return question


def router_node(state: GraphState) -> Dict[str, Any]:
    """Normalizes the query, domains and routes the pipeline state.

    Args:
        state: The current GraphState.

    Returns:
        State updates containing domain and routing flag classifications.
    """
    logger.info("--- ROUTER NODE ---")
    question = state["question"]
    chat_history = state.get("chat_history", [])
    preferred_domain = state.get("preferred_domain")

    # Spell-check, normalization and intent optimization
    original_question = None
    normalized_q, was_corrected = normalize_query(question, llm)
    if was_corrected:
        original_question = question
        question = normalized_q
        logger.info(f"Query corrected: '{original_question}' -> '{question}'")

    question = condense_question(question, chat_history)
    
    if preferred_domain and preferred_domain != 'all':
        domain = preferred_domain.strip().lower()
        logger.info(f"Bypassing classification. Using user preferred domain: {domain.upper()}")
    else:
        domain = classify_domain(question)
        logger.info(f"Classified Domain: {domain.upper()}")
    
    q_lower = question.lower()
    expert_required = any(kw in q_lower for kw in EXPERT_KEYWORDS)
    python_repl = any(kw in q_lower for kw in PYTHON_KEYWORDS)
    web_fallback = True
    export_to_workspace = any(kw in q_lower for kw in EXPORT_KEYWORDS)
    
    logger.info(f"Routing flags -> expert_required: {expert_required}, python_repl: {python_repl}, web_fallback: {web_fallback}, export_to_workspace: {export_to_workspace}")
        
    return {
        "question": question,
        "original_question": original_question,
        "domain": domain, 
        "expert_required": expert_required, 
        "python_repl": python_repl,
        "web_fallback": web_fallback,
        "export_to_workspace": export_to_workspace
    }


def retrieve_local_node(state: GraphState) -> Dict[str, Any]:
    """Retrieves document chunks from the local ChromaDB vector store.

    Args:
        state: The current GraphState.

    Returns:
        State updates containing retrieved document contexts.
    """
    logger.info("--- RETRIEVE LOCAL NODE ---")
    question = state["question"]
    domain = state["domain"]
    selected_doc = state.get("selected_doc")
    
    context = retrieve_context(question, domain, target_file=selected_doc)
    
    # Filter out error or missing database responses
    if any(msg in context for msg in ["No database found", "No relevant information", "Error occurred"]):
        docs = []
    else:
        docs = [context]
        
    return {"documents": docs}


def grade_documents_node(state: GraphState) -> Dict[str, Any]:
    """Performs keyword overlap matching to check relevance, skipping LLM grader if possible.

    Args:
        state: The current GraphState.

    Returns:
        State updates containing the updated web_fallback flag.
    """
    logger.info("--- GRADE DOCUMENTS NODE ---")
    question = state["question"]
    documents = state.get("documents", [])
    selected_doc = state.get("selected_doc")

    if not documents:
        logger.info("No local documents found. Triggering Web Search.")
        return {"web_fallback": True}

    if selected_doc:
        logger.info(f"Explicit target PDF specified ('{selected_doc}'). Skipping relevance grader.")
        return {"web_fallback": False}

    # Fast token set intersection with stopword filtering (Mathematical Eq. 7 alignment)
    STOPWORDS = {
        "what", "which", "where", "when", "why", "how", "this", "that", "these", "those",
        "with", "from", "have", "has", "had", "been", "were", "will", "would", "should",
        "could", "about", "above", "after", "again", "also", "into", "just", "more", "most",
        "other", "some", "such", "than", "then", "their", "there", "them", "they", "does",
        "described", "paper", "article", "study", "analysis", "system", "method", "using",
        "nhung", "cac", "cua", "trong", "tren", "duoc", "bang", "cho", "voi", "nay", "kia"
    }
    context_text = documents[0].lower()
    question_tokens = set(
        t for t in re.findall(r"\b[a-zA-Z0-9_\-]{3,}\b", question.lower())
        if t not in STOPWORDS
    )
    context_tokens = set(re.findall(r"\b[a-zA-Z0-9_\-]{3,}\b", context_text))

    if question_tokens:
        intersection = question_tokens.intersection(context_tokens)
        overlap_ratio = len(intersection) / len(question_tokens)
        is_relevant = overlap_ratio >= 0.25
        logger.info(
            f"Token set intersection: {len(intersection)}/{len(question_tokens)} unique tokens matched "
            f"(ratio={overlap_ratio:.2f}, hits={list(intersection)[:5]}). Relevant={is_relevant}"
        )
        if is_relevant:
            return {"web_fallback": False}
    else:
        logger.info("No meaningful non-stopword tokens in question. Trusting retrieved documents.")
        return {"web_fallback": False}

    logger.info("Low keyword overlap. Triggering Web Search.")
    return {"web_fallback": True}


def web_search_node(state: GraphState) -> Dict[str, Any]:
    """Queries DuckDuckGo search to retrieve updated context.

    Args:
        state: The current GraphState.

    Returns:
        State updates containing web search results.
    """
    logger.info("--- WEB SEARCH NODE ---")
    question = state["question"]
    
    results = duckduckgo_search(question)
    logger.info("Web Search completed.")
    
    documents = state.get("documents", [])
    documents.append(f"--- Web Search Results ---\n{results}")
    
    return {"documents": documents}


def expert_consult_node(state: GraphState) -> Dict[str, Any]:
    """Queries the Tavily Search API for expert synthesis.

    Args:
        state: The current GraphState.

    Returns:
        State updates containing expert search answers.
    """
    logger.info("--- EXPERT CONSULT NODE ---")
    question = state["question"]
    
    logger.info("Consulting Tavily API...")
    answer = get_expert_answer(question)
    
    documents = state.get("documents", [])
    documents.append(f"--- Expert Search Results ---\n{answer}")
    
    return {"documents": documents}


def generate_node(state: GraphState) -> Dict[str, Any]:
    """Synthesizes the final response using Qwen2.5 based on retrieved contexts.

    Args:
        state: The current GraphState.

    Returns:
        State updates containing the generated text and parsed structured data tables.
    """
    logger.info("--- GENERATE NODE ---")
    question = state["question"]
    documents = state.get("documents", [])
    retry_count = state.get("retry_count", 0)
    chat_history = state.get("chat_history", [])
    
    context = "\n\n".join(documents)
    
    history_str = ""
    if chat_history:
        history_str = "--- CONVERSATION HISTORY ---\n"
        for turn in chat_history:
            usr = turn.get("user", "")
            agt = turn.get("agent", "")
            clean_agt = re.sub(r"```mermaid\s*(.*?)\s*```", "[Diagram]", agt, flags=re.DOTALL)
            history_str += f"User: {usr}\nAgent: {clean_agt}\n\n"
        history_str += "-------------------------\n\n"
        
    template = """
    You are a professional technical assistant. Answer the [QUESTION] based on the provided [CONTEXT] and the past [CONVERSATION HISTORY] (if any).
    
    MANDATORY RULES:
    1. BE DETAILED AND COMPREHENSIVE. You MUST provide a long, fully developed, and rich textual explanation answering the question in detail first. Do not just give a brief summary.
    2. NEVER mention "Google Forms", "API", or "environment details".
    3. If calculation results are present in [CONTEXT], use them as the primary answer.
    4. If a Python code execution result is present in [CONTEXT], focus on explaining the result and output. DO NOT repeat or rewrite the raw Python code block (```python ... ```) in your answer.
    5. You MUST ALWAYS provide the detailed textual report first. If a diagram is requested or appropriate, append EXACTLY ONE Mermaid code block wrapped in ```mermaid at the very end of your answer. The Mermaid diagram MUST act ONLY as a visual summary of the detailed text you already provided above. ALWAYS enclose node label text in double quotes inside brackets (e.g. A["Label text (with details)"] --> B["Other label"]) to ensure valid Mermaid syntax. Do not rely on the diagram to convey new information.
    6. ABSOLUTELY NO TEXT OR EXPLANATION should be generated after the Mermaid code block. The Mermaid block MUST be the absolute final element of your response.
    7. Do not repeat information redundantly, but ensure the topic is thoroughly explained.
    8. NEVER explain the rules, reference your system instructions, or mention any prompt constraints to the user. Do not output any meta-commentary or reflection notes. Just output the clean final answer.
    9. Return ONLY the final report content.
 
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
    except Exception as e:
        logger.warning(f"Primary LLM generation failed: {e}. Retrying with CPU fallback LLM (num_gpu=0)...")
        try:
            fallback_llm = ChatOllama(
                model=Config.LLM_MODEL,
                temperature=Config.TEMPERATURE,
                num_ctx=Config.CONTEXT_WINDOW,
                num_predict=Config.MAX_TOKENS,
                keep_alive=Config.KEEP_ALIVE,
                num_gpu=0
            )
            fallback_chain = prompt | fallback_llm | StrOutputParser()
            response = fallback_chain.invoke({"question": question, "context": context, "history": history_str})
            logger.info("CPU fallback LLM generation succeeded.")
        except Exception as retry_err:
            logger.error(f"Fallback generation also failed: {retry_err}")
            return {"generation": "Error occurred during generation.", "retry_count": retry_count + 1}

    formatted_response = format_agent_output(response)
    
    # Populate structured_data from tables
    structured_data = parse_markdown_table(formatted_response)
    if structured_data:
        logger.info(f"Automatically parsed comparison table for Sheets: {len(structured_data)} rows.")
        
    return {
        "generation": formatted_response,
        "structured_data": structured_data,
        "retry_count": retry_count + 1
    }


def python_repl_node(state: GraphState) -> Dict[str, Any]:
    """Generates and executes Python code inside a secure REPL environment for computation.

    Args:
        state: The current GraphState.

    Returns:
        State updates containing REPL execution logs.
    """
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
        logger.info(f"Generated Python Code:\n{code}")
        
        repl = PythonREPL()
        result = repl.run(code).strip()
        
        structured_data = [["Result Type", "Value"], ["Computation Output", result]]
        answer = f"--- Python Computation Result ---\nCode:\n{code}\nResult:\n{result}"
        
        docs = state.get("documents", [])
        docs.append(answer)
        
        return {"documents": docs, "structured_data": structured_data}
    except Exception as e:
        logger.error(f"Python REPL execution failed: {e}")
        err_msg = f"Failed to execute Python logic. Error: {e}"
        return {"generation": format_agent_output(err_msg)}


def generate_short_title(question: str, doc_type: str) -> str:
    """Generates a concise and professional document title under 8 words.

    Args:
        question: User query text.
        doc_type: File target type ('docs' or 'sheets').

    Returns:
        A concise formatted title.
    """
    if not llm:
        words = question.split()
        prefix = "Doc: " if doc_type == "docs" else "Sheet: "
        return f"{prefix}{' '.join(words[:5])}"
        
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
        words = title.split()
        if len(words) > 8:
            title = " ".join(words[:8])
        return title
    except Exception as e:
        logger.error(f"Failed to generate short title: {e}")
        words = question.split()
        prefix = "Doc: " if doc_type == "docs" else "Sheet: "
        return f"{prefix}{' '.join(words[:5])}"


def export_report_node(state: GraphState) -> Dict[str, Any]:
    """Compiles results, renders diagrams, and uploads files to Google Drive/Docs/Sheets in parallel.

    Args:
        state: The current GraphState.

    Returns:
        State updates containing Google Workspace URLs.
    """
    logger.info("--- EXPORT REPORT NODE ---")
    question = state["question"]
    generation = state.get("generation", "")
    structured_data = state.get("structured_data")

    if not generation:
        return {"generation": "[Export] No content available to export."}

    question_lower = question.lower()
    has_docs_intent = any(kw in question_lower for kw in ["docs", "doc", "document", "văn bản", "tài liệu", "word"])
    has_sheets_intent = any(kw in question_lower for kw in ["sheets", "sheet", "bảng", "trang tính", "excel"])

    export_docs = True
    export_sheets = True

    if has_docs_intent or has_sheets_intent:
        export_docs = has_docs_intent
        export_sheets = has_sheets_intent

    logger.info(f"Export Targets -> Docs: {export_docs}, Sheets: {export_sheets}")

    # Process and upload Mermaid diagrams
    image_urls = []
    mermaid_blocks = list(set(re.findall(r"```mermaid\s*(.*?)\s*```", generation, re.DOTALL)))
    logger.info(f"Found {len(mermaid_blocks)} unique mermaid diagrams to render.")
    
    for mmd_code in mermaid_blocks:
        image_path = render_mermaid_to_image(mmd_code.strip())
        if image_path:
            drive_url = upload_image_to_drive(image_path)
            if drive_url:
                image_urls.append(drive_url)
            if os.path.exists(image_path):
                os.remove(image_path)

    export_summary_parts = []
    export_links = {"docs": None, "sheets": None}

    def run_docs_export() -> str:
        doc_title = generate_short_title(question, "docs")
        clean_content = re.sub(r"```mermaid\s*(.*?)\s*```", "", generation, flags=re.DOTALL).strip()
        doc_content = f"QUESTION:\n{question}\n\n"
        if clean_content:
            doc_content += f"ANSWER:\n{clean_content}\n"
        else:
            doc_content += "ANSWER:\n(Please refer to the diagram below)\n"
        return export_to_google_docs(title=doc_title, content=doc_content, image_urls=image_urls)

    def run_sheets_export() -> str:
        sheet_title = generate_short_title(question, "sheets")
        clean_generation = re.sub(r"```mermaid\s*(.*?)\s*```", "[Diagram Rendered in Doc]", generation, flags=re.DOTALL).strip()
        sheet_data = structured_data if structured_data else [
            ["Field", "Value"],
            ["Question", question],
            ["Answer", clean_generation],
            ["Status", "Completed"]
        ]
        return export_to_google_sheets(title=sheet_title, data=sheet_data)

    # Run exports in parallel to minimize latency
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {}
        if export_docs:
            futures["docs"] = executor.submit(run_docs_export)
        if export_sheets:
            futures["sheets"] = executor.submit(run_sheets_export)

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

    return {"generation": generation, "export_links": export_links}
