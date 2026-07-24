import json
import logging
from typing import Dict, Any
from agent.state import GraphState
from local_rag import llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

logger = logging.getLogger(__name__)

def route_question(state: GraphState) -> str:
    """Routes the user question to Python REPL, Expert Consultant, or Local VectorDB.

    Args:
        state: The current state of the LangGraph execution graph.

    Returns:
        The name of the next node to execute ("python_repl", "expert_consult", or "retrieve_local").
    """
    logger.info("--- ROUTING QUESTION ---")
    if state.get("python_repl"):
        logger.info("[Router Edge] Routing to Python REPL.")
        return "python_repl"
    elif state.get("expert_required"):
        logger.info("[Router Edge] Routing to Expert Consultant (Tavily).")
        return "expert_consult"
    else:
        logger.info("[Router Edge] Routing to Local VectorDB.")
        return "retrieve_local"


def decide_to_generate(state: GraphState) -> str:
    """Determines whether to proceed to answer generation or fallback to web search.

    Args:
        state: The current state of the LangGraph execution graph.

    Returns:
        The name of the next node to execute ("web_search" or "generate").
    """
    logger.info("--- DECIDING TO GENERATE ---")
    if state.get("web_fallback"):
        logger.info("[Grader Edge] Decision: Fallback to Web Search.")
        return "web_search"
    else:
        logger.info("[Grader Edge] Decision: Generate Answer.")
        return "generate"


def parse_json_from_llm(raw_output: str) -> dict:
    """Parses JSON content returned by the LLM, with fallback parsing for robustness.

    Args:
        raw_output: The raw string response from the LLM.

    Returns:
        A dictionary containing the parsed metrics or decisions.
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
    except Exception as e:
        logger.warning(f"[JSON Parser] Failed to parse JSON via json.loads: {e}. Attempting regex fallback.")
        res = {}
        cleaned_lower = cleaned.lower()
        if "grounded" in cleaned_lower:
            res["grounded"] = "no" if "grounded" in cleaned_lower and ('"no"' in cleaned_lower or "'no'" in cleaned_lower) else "yes"
        if "useful" in cleaned_lower:
            res["useful"] = "no" if "useful" in cleaned_lower and ('"no"' in cleaned_lower or "'no'" in cleaned_lower) else "yes"
        return res


def grade_generation_v_documents_and_question(state: GraphState) -> str:
    """Evaluates if the generation is grounded in facts and answers the user query.

    Uses a unified Joint Grader. Skips LLM evaluation on retry >= 1 or when an explicit
    document was selected (context is trusted) to minimize inference latency.

    Args:
        state: The current state of the LangGraph execution graph.

    Returns:
        The next path to take ("useful", "not useful", or "not supported").
    """
    logger.info("--- JOINT EVALUATION (HALLUCINATION & RELEVANCE GRADER) ---")
    question = state["question"]
    documents = state.get("documents", [])
    generation = state["generation"]
    retry_count = state.get("retry_count", 0)
    selected_doc = state.get("selected_doc")
    max_retries = 2

    # Fast-path: trust generation under specific constraints to save LLM calls
    if selected_doc:
        logger.info("[Joint Grader] Selected-doc mode: trusting generation without LLM grading.")
        return "useful"

    if retry_count > max_retries:
        logger.info(f"[Joint Grader] retry_count={retry_count}: accepting generation to avoid infinite loops.")
        return "useful"

    # Joint Grader Prompt (only executed on the first attempt, no selected_doc)
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
        logger.info("[Joint Grader] Invoking Joint Grader LLM...")
        raw_res = joint_chain.invoke({
            "documents": context,
            "question": question,
            "generation": generation
        })
        logger.info(f"[Joint Grader] Raw response: {repr(raw_res.strip())}")
        decision = parse_json_from_llm(raw_res)
        grounded = decision.get("grounded", "yes").strip().lower()
        useful = decision.get("useful", "yes").strip().lower()
    except Exception as e:
        logger.error(f"[Joint Grader] Joint grading failed: {e}. Defaulting to safe fallback (useful).")
        grounded = "yes"
        useful = "yes"

    logger.info(f"[Joint Grader] Evaluation Results -> Grounded: {grounded.upper()}, Useful: {useful.upper()}")

    if "yes" in grounded:
        if "yes" in useful:
            logger.info("[Joint Grader] Decision: Generation is grounded and answers the question.")
            return "useful"
        else:
            if retry_count >= max_retries:
                logger.info(f"[Joint Grader] Max retries ({max_retries}) reached. Accepting useful fallback.")
                return "useful"
            logger.info("[Joint Grader] Decision: Generation does not address the question.")
            return "not useful"
    else:
        if retry_count >= max_retries:
            logger.info(f"[Joint Grader] Max retries ({max_retries}) reached. Accepting grounded fallback.")
            return "useful"
        logger.info("[Joint Grader] Decision: Generation is not grounded. Retrying generation.")
        return "not supported"


def decide_to_export(state: GraphState) -> str:
    """Decides whether to export the result to Google Workspace.

    Args:
        state: The current state of the LangGraph execution graph.

    Returns:
        The next node to execute ("export" or "end").
    """
    logger.info(f"[Export Edge] Deciding export. export_to_workspace={state.get('export_to_workspace')}")
    if state.get("export_to_workspace"):
        logger.info("[Export Edge] Routing to Export Report node.")
        return "export"
    logger.info("[Export Edge] Bypassing export. Ending workflow.")
    return "end"
