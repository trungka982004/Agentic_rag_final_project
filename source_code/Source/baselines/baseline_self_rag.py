"""
Baseline 4: Self-RAG (Prompting & Reflection Mode)
Architecture (Asai et al., ICLR 2024):
- Employs self-reflection tokens adapted for general-purpose LLMs (Self-RAG Prompting):
    1. [Retrieve]: Decides whether external retrieval is necessary.
    2. [IsRel]: Critiques whether retrieved passages are relevant.
    3. [IsSup]: Critiques whether each generated statement is grounded in context.
    4. [IsUse]: Evaluates overall response utility.
- Allows iterative refinement when critique detects unsupported statements.
"""
import time
from typing import Dict, Any, List
from local_rag import get_vector_db, generate_answer, classify_domain, llm

def self_rag_retrieve_decision(question: str) -> bool:
    """Evaluates the [Retrieve] reflection token."""
    prompt = f"""
    Evaluate whether the following question requires retrieving external scientific literature or can be answered directly:
    [Question]: {question}
    
    Output ONLY '[Retrieve]' if retrieval is needed, or '[NoRetrieve]' if general knowledge suffices.
    """
    try:
        res = llm.invoke(prompt).content.strip()
        return "[Retrieve]" in res or "Retrieve" in res
    except Exception:
        return True

def self_rag_critique_relevance(question: str, context: str) -> bool:
    """Evaluates the [IsRel] reflection token."""
    prompt = f"""
    Evaluate if this passage is relevant to the question:
    [Question]: {question}
    [Passage]: {context[:1200]}
    
    Output ONLY '[Relevant]' or '[Irrelevant]'.
    """
    try:
        res = llm.invoke(prompt).content.strip()
        return "[Relevant]" in res or "Relevant" in res
    except Exception:
        return True

def self_rag_critique_support(answer: str, context: str) -> bool:
    """Evaluates the [IsSup] reflection token."""
    prompt = f"""
    Does the passage support the statements made in the answer?
    [Passage]: {context[:1500]}
    [Answer]: {answer}
    
    Output ONLY '[FullySupported]', '[PartiallySupported]', or '[NoSupport]'.
    """
    try:
        res = llm.invoke(prompt).content.strip()
        return "[FullySupported]" in res or "[PartiallySupported]" in res or "Support" in res
    except Exception:
        return True

def run_self_rag(question: str, domain: str = None, k: int = 5, max_reflection_loops: int = 2) -> Dict[str, Any]:
    start_time = time.time()
    
    if not domain:
        domain = classify_domain(question)
        
    need_retrieve = self_rag_retrieve_decision(question)
    
    contexts = []
    if need_retrieve:
        db = get_vector_db(domain)
        if db:
            retriever = db.as_retriever(search_kwargs={"k": k})
            raw_docs = retriever.invoke(question)
            
            # [IsRel] filtering
            for d in raw_docs:
                if self_rag_critique_relevance(question, d.page_content):
                    contexts.append(d.page_content)
            if not contexts and raw_docs:
                contexts = [raw_docs[0].page_content]
                
    context_text = "\n\n".join(contexts) if contexts else "No retrieval required."
    
    # Generation with [IsSup] loop
    loops = 0
    answer = ""
    is_supported = False
    
    while loops < max_reflection_loops:
        loops += 1
        answer = generate_answer(question, context_text)
        if not contexts:
            is_supported = True
            break
        is_supported = self_rag_critique_support(answer, context_text)
        if is_supported:
            break
            
    latency = time.time() - start_time
    
    return {
        "answer": answer,
        "contexts": contexts,
        "latency": latency,
        "domain": domain,
        "need_retrieve": need_retrieve,
        "reflection_loops": loops,
        "is_supported": is_supported,
        "baseline": "Self_RAG"
    }

if __name__ == "__main__":
    res = run_self_rag("Explain residual connections in ResNet", domain="it")
    print(f"Loops: {res['reflection_loops']} | Supported: {res['is_supported']} | Latency: {res['latency']:.2f}s")
