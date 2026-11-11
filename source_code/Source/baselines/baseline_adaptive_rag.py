"""
Baseline 5: Adaptive-RAG
Architecture (Jeong et al., NAACL-HLT 2024):
- Dynamically adapts retrieval strategy based on Question Complexity:
    1. 'Simple' Complexity: Non-retrieval direct generation for basic factual/conceptual questions.
    2. 'Moderate' Complexity: Single-step hybrid retrieval against domain corpus.
    3. 'Complex' Complexity: Multi-hop / comparative synthesis with web search fallback.
"""
import time
from typing import Dict, Any, List
from local_rag import get_vector_db, generate_answer, classify_domain, llm
from tools.web_search import duckduckgo_search

def classify_query_complexity(question: str) -> str:
    """Classifies query complexity into Simple, Moderate, or Complex."""
    prompt = f"""
    Classify the following query into one of three complexity tiers:
    - SIMPLE: Basic general concept, standard definition, or conversational greeting.
    - MODERATE: Specific domain inquiry answerable from a single academic paper.
    - COMPLEX: Multi-step comparison, historical trend, or synthesis requiring external web search.
    
    [Query]: {question}
    
    Output ONLY: SIMPLE, MODERATE, or COMPLEX.
    """
    try:
        res = llm.invoke(prompt).content.strip().upper()
        if "COMPLEX" in res:
            return "COMPLEX"
        elif "SIMPLE" in res:
            return "SIMPLE"
        return "MODERATE"
    except Exception:
        # Heuristic fallback
        if any(w in question.lower() for w in ["compare", "versus", "vs", "trend", "evolution", "difference"]):
            return "COMPLEX"
        elif len(question.split()) < 6:
            return "SIMPLE"
        return "MODERATE"

def run_adaptive_rag(question: str, domain: str = None, k: int = 5) -> Dict[str, Any]:
    start_time = time.time()
    
    complexity = classify_query_complexity(question)
    contexts = []
    
    if complexity == "SIMPLE":
        # Direct generation without retrieval
        context_text = "No retrieval necessary for simple query."
    elif complexity == "MODERATE":
        # Single-step local retrieval
        if not domain:
            domain = classify_domain(question)
        db = get_vector_db(domain)
        if db:
            docs = db.as_retriever(search_kwargs={"k": k}).invoke(question)
            contexts = [d.page_content for d in docs]
        context_text = "\n\n".join(contexts) if contexts else "No relevant local context found."
    else: # COMPLEX
        # External web search + local retrieval
        if not domain:
            domain = classify_domain(question)
        db = get_vector_db(domain)
        if db:
            docs = db.as_retriever(search_kwargs={"k": k}).invoke(question)
            contexts = [d.page_content for d in docs]
            
        web_res = duckduckgo_search(question)
        contexts.append(f"--- Adaptive Web Synthesis ---\n{web_res}")
        context_text = "\n\n".join(contexts)
        
    answer = generate_answer(question, context_text)
    latency = time.time() - start_time
    
    return {
        "answer": answer,
        "contexts": contexts,
        "latency": latency,
        "domain": domain,
        "complexity": complexity,
        "baseline": "Adaptive_RAG"
    }

if __name__ == "__main__":
    res = run_adaptive_rag("Compare Transformer and RNN architectures", domain="it")
    print(f"Complexity: {res['complexity']} | Contexts: {len(res['contexts'])} | Latency: {res['latency']:.2f}s")

