"""
Baseline 2: Advanced RAG
Architecture:
- Static Hybrid Retrieval: Combines Dense Vector Search (BGE-M3) and Sparse BM25 via Weighted Reciprocal Rank Fusion (RRF).
- Fixed static weights (0.5 BM25, 0.5 Dense) with k=60.
- Context deduplication before generation.
- No dynamic query routing, no multi-tier fallback.
"""
import time
from typing import Dict, Any, List
from local_rag import get_vector_db, get_bm25_retriever, generate_answer, classify_domain
# Optional LangChain EnsembleRetriever with standalone RRF fallback
try:
    from langchain.retrievers import EnsembleRetriever
except Exception:
    EnsembleRetriever = None

def compute_weighted_rrf(doc_lists: List[List[Any]], weights: List[float], k: int = 60) -> List[Any]:
    """Computes exact Reciprocal Rank Fusion (Cormack et al., SIGIR 2009)."""
    scores = {}
    doc_map = {}
    for docs, weight in zip(doc_lists, weights):
        for rank, doc in enumerate(docs):
            key = doc.page_content.strip()[:150]
            doc_map[key] = doc
            scores[key] = scores.get(key, 0.0) + weight / (k + rank + 1)
    sorted_keys = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    return [doc_map[k] for k in sorted_keys]

def run_advanced_rag(question: str, domain: str = None, k: int = 5) -> Dict[str, Any]:
    start_time = time.time()
    
    if not domain:
        domain = classify_domain(question)
        
    db = get_vector_db(domain)
    if not db:
        return {
            "answer": "No vector database found.",
            "contexts": [],
            "latency": time.time() - start_time,
            "domain": domain,
            "baseline": "Advanced_RAG"
        }
        
    vector_retriever = db.as_retriever(search_kwargs={"k": k})
    bm25_retriever = get_bm25_retriever(db, domain=domain, k=k)
    
    # Static 50-50 Weighted RRF
    v_docs = vector_retriever.invoke(question)
    if bm25_retriever:
        b_docs = bm25_retriever.invoke(question)
        docs = compute_weighted_rrf([b_docs, v_docs], weights=[0.5, 0.5], k=60)
    else:
        docs = v_docs
        
    # Deduplicate
    seen = set()
    unique_docs = []
    for d in docs:
        snip = d.page_content.strip()[:150]
        if snip not in seen:
            seen.add(snip)
            unique_docs.append(d)
            
    contexts = [d.page_content for d in unique_docs[:k]]
    context_text = "\n\n".join(contexts)
    
    answer = generate_answer(question, context_text)
    latency = time.time() - start_time
    
    return {
        "answer": answer,
        "contexts": contexts,
        "latency": latency,
        "domain": domain,
        "retrieved_count": len(contexts),
        "baseline": "Advanced_RAG"
    }

if __name__ == "__main__":
    res = run_advanced_rag("How does convolution work in deep networks?", domain="it")
    print(f"Latency: {res['latency']:.2f}s | Contexts: {len(res['contexts'])}")
