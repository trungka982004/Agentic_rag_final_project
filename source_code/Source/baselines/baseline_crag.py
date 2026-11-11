"""
Baseline 3: Corrective RAG (CRAG)
Architecture (Yan et al., ACL 2024):
- Evaluates retrieved documents using a confidence evaluator.
- Tri-grade decision:
    1. Correct: confidence > threshold -> internal knowledge refinement.
    2. Incorrect: confidence < low_threshold -> triggers web search fallback.
    3. Ambiguous: intermediate confidence -> combines local + web context.
- Generates answer based on corrective context.
"""
import time
import re
from typing import Dict, Any, List
from local_rag import get_vector_db, generate_answer, classify_domain, llm
from tools.web_search import duckduckgo_search

def evaluate_retrieval_confidence(question: str, context_text: str) -> str:
    """Evaluates document relevance into Correct, Ambiguous, or Incorrect."""
    prompt = f"""
    You are an evaluator in a Corrective RAG pipeline.
    Evaluate the relevance of the retrieved document to the user question:
    [Question]: {question}
    [Document Excerpt]: {context_text[:1500]}
    
    Choose exactly one verdict:
    - CORRECT: The document contains sufficient, directly relevant information to answer the question.
    - AMBIGUOUS: The document is somewhat related but lacks complete specific details.
    - INCORRECT: The document is completely irrelevant or off-topic.
    
    Output ONLY one word: CORRECT, AMBIGUOUS, or INCORRECT.
    """
    try:
        res = llm.invoke(prompt).content.strip().upper()
        if "CORRECT" in res:
            return "CORRECT"
        elif "AMBIGUOUS" in res:
            return "AMBIGUOUS"
        else:
            return "INCORRECT"
    except Exception:
        # Fallback to token overlap heuristic
        q_toks = set(re.findall(r"\b[a-zA-Z0-9_\-]{3,}\b", question.lower()))
        c_toks = set(re.findall(r"\b[a-zA-Z0-9_\-]{3,}\b", context_text.lower()))
        ratio = len(q_toks.intersection(c_toks)) / max(1, len(q_toks))
        if ratio >= 0.4:
            return "CORRECT"
        elif ratio >= 0.15:
            return "AMBIGUOUS"
        return "INCORRECT"

def run_crag(question: str, domain: str = None, k: int = 5) -> Dict[str, Any]:
    start_time = time.time()
    web_triggered = False
    
    if not domain:
        domain = classify_domain(question)
        
    db = get_vector_db(domain)
    local_docs = []
    if db:
        retriever = db.as_retriever(search_kwargs={"k": k})
        local_docs = retriever.invoke(question)
        
    contexts = [d.page_content for d in local_docs]
    combined_local = "\n\n".join(contexts)
    
    # CRAG Evaluation Step
    verdict = evaluate_retrieval_confidence(question, combined_local) if contexts else "INCORRECT"
    
    final_contexts = []
    if verdict == "CORRECT":
        # Internal refinement
        final_contexts = contexts
    elif verdict == "INCORRECT":
        # Web search fallback
        web_triggered = True
        web_res = duckduckgo_search(question)
        final_contexts = [f"--- Web Search (CRAG Fallback) ---\n{web_res}"]
    else:  # AMBIGUOUS
        # Combine local + web
        web_triggered = True
        web_res = duckduckgo_search(question)
        final_contexts = contexts + [f"--- Supplementary Web Search ---\n{web_res}"]
        
    context_text = "\n\n".join(final_contexts)
    answer = generate_answer(question, context_text)
    latency = time.time() - start_time
    
    return {
        "answer": answer,
        "contexts": final_contexts,
        "latency": latency,
        "domain": domain,
        "crag_verdict": verdict,
        "web_triggered": web_triggered,
        "baseline": "CRAG"
    }

if __name__ == "__main__":
    res = run_crag("What is transformer model?", domain="it")
    print(f"Verdict: {res['crag_verdict']} | Web: {res['web_triggered']} | Latency: {res['latency']:.2f}s")
