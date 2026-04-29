from agent.state import GraphState
from tools.web_search import duckduckgo_search
from tools.expert_search import get_expert_answer
from local_rag import classify_domain, retrieve_context, llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def router_node(state: GraphState):
    """Classifies domain and decides initial path."""
    print("--- ROUTER NODE ---")
    question = state["question"]
    domain = classify_domain(question)
    
    print(f"[*] Classified Domain: {domain.upper()}")
    
    use_tavily = state.get("use_tavily", True)
    expert_keywords = ["compare", "latest", "news", "trend", "so sánh", "mới nhất", "xu hướng", "tin tức"]
    expert_required = False
    
    if use_tavily:
        expert_required = any(kw in question.lower() for kw in expert_keywords)
    else:
        print("[*] Tavily trigger is OFF. Forcing Local/Web search track.")
    
    return {"domain": domain, "expert_required": expert_required}

def retrieve_local_node(state: GraphState):
    """Retrieves documents from local ChromaDB."""
    print("--- RETRIEVE LOCAL NODE ---")
    question = state["question"]
    domain = state["domain"]
    
    context = retrieve_context(question, domain)
    if "No database found" in context or "No relevant information" in context:
        docs = []
    else:
        docs = [context]
        
    return {"documents": docs}

def grade_documents_node(state: GraphState):
    """Grades the retrieved documents for relevance."""
    print("--- GRADE DOCUMENTS NODE ---")
    question = state["question"]
    documents = state["documents"]
    
    if not documents:
        print("[*] No local documents found. Falling back to Web Search.")
        return {"web_fallback": True}
        
    prompt = ChatPromptTemplate.from_template(
        "You are a grader assessing relevance of a retrieved document to a user question.\n"
        "Here is the retrieved document: \n\n {document} \n\n"
        "Here is the user question: {question}\n"
        "If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant.\n"
        "Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."
    )
    
    chain = prompt | llm | StrOutputParser()
    
    score = chain.invoke({"question": question, "document": documents[0]}).strip().lower()
    
    if "yes" in score:
        print("[*] Local documents are RELEVANT.")
        return {"web_fallback": False}
    else:
        print("[*] Local documents are NOT relevant. Falling back to Web Search.")
        return {"web_fallback": True}

def web_search_node(state: GraphState):
    """Uses DuckDuckGo to search the web."""
    print("--- WEB SEARCH NODE ---")
    question = state["question"]
    
    results = duckduckgo_search(question)
    print("[*] Web Search completed.")
    
    documents = state.get("documents", [])
    if not documents:
        documents = []
    documents.append(f"--- Web Search Results ---\n{results}")
    
    return {"documents": documents}

def expert_consult_node(state: GraphState):
    """Consults Tavily API for complex questions."""
    print("--- EXPERT CONSULT NODE ---")
    question = state["question"]
    
    print("[*] Consulting Tavily API...")
    answer = get_expert_answer(question)
    
    return {"generation": answer}

def generate_node(state: GraphState):
    """Generates the final answer using Qwen."""
    print("--- GENERATE NODE ---")
    question = state["question"]
    documents = state.get("documents", [])
    
    context = "\n\n".join(documents)
    
    template = """
    You are a professional scientific assistant. Use the following [CONTEXT] to answer the user's [QUESTION].
    
    MANDATORY RULES:
    1. Only use the information provided in the [CONTEXT]. Do not invent external knowledge.
    2. If the [CONTEXT] does not contain enough information to answer, state: "I'm sorry, the provided documents do not contain enough information to answer this question."
    3. Your answer must be clear, structured (use bullet points if necessary), and highly accurate.
    4. Provide citations whenever possible.

    [CONTEXT]:
    {context}

    [QUESTION]:
    {question}

    [ANSWER]:
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    
    response = chain.invoke({"question": question, "context": context})
    return {"generation": response}
