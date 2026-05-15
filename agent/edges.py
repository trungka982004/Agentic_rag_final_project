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

def grade_generation_v_documents_and_question(state: GraphState):
    """
    Determines whether the generation is grounded in the document and answers question.
    """
    print("--- CHECK HALLUCINATIONS ---")
    question = state["question"]
    documents = state.get("documents", [])
    generation = state["generation"]

    if not documents:
        # If no documents, we can't check for hallucination against context
        # But we can still check answer relevance
        pass

    # 1. Hallucination Grader
    hallucination_prompt = ChatPromptTemplate.from_template(
        "You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts. \n"
        "Here are the facts:\n"
        "-------\n"
        "{documents}\n"
        "-------\n"
        "Here is the LLM generation: {generation}\n"
        "Give a binary score 'yes' or 'no'. 'yes' means that the answer is grounded in / supported by the facts."
    )
    hallucination_chain = hallucination_prompt | llm | StrOutputParser()
    
    context = "\n\n".join(documents) if documents else "No documents."
    score = hallucination_chain.invoke({"documents": context, "generation": generation})
    grade = score.strip().lower()

    if "yes" in grade:
        print("[*] Decision: Generation is grounded in documents.")
        
        # 2. Answer Grader
        print("--- GRADE GENERATION vs QUESTION ---")
        answer_prompt = ChatPromptTemplate.from_template(
            "You are a grader assessing whether an answer addresses / resolves a question. \n"
            "Here is the question:\n"
            "-------\n"
            "{question}\n"
            "-------\n"
            "Here is the answer:\n"
            "-------\n"
            "{generation}\n"
            "-------\n"
            "Give a binary score 'yes' or 'no'. 'yes' means that the answer resolves the question."
        )
        answer_chain = answer_prompt | llm | StrOutputParser()
        score = answer_chain.invoke({"question": question, "generation": generation})
        grade = score.strip().lower()
        
        if "yes" in grade:
            print("[*] Decision: Generation addresses question.")
            return "useful"
        else:
            print("[*] Decision: Generation does not address question.")
            return "not useful"
    else:
        print("[*] Decision: Generation is not grounded in documents, retry.")
        return "not supported"

def decide_to_export(state: GraphState):
    """Decides whether to export the result to Google Workspace."""
    if state.get("export_to_workspace"):
        print("[*] Export flag is ON. Routing to Export Report node.")
        return "export"
    print("[*] Export flag is OFF. Ending.")
    return "end"
