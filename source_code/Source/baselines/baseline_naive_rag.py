"""
Baseline 1: Naive RAG
Architecture:
- Single-turn dense passage retrieval via ChromaDB (BGE-M3 embeddings, cosine similarity)
- Direct single-prompt generation using Qwen2.5-7B
- No reranking, no fallback, no self-correction.
"""
import time
from typing import Dict, Any, List
from local_rag import get_vector_db, generate_answer, classify_domain, llm

def run_naive_rag(question: str, domain: str = None, k: int = 5) -> Dict[str, Any]:
    start_time = time.time()
    
    # 1. Domain acquisition
    if not domain:
        domain = classify_domain(question)
        
    db = get_vector_db(domain)
    if not db:
        return {
            "answer": "No vector database found for domain.",
            "contexts": [],
            "latency": time.time() - start_time,
            "domain": domain,
            "baseline": "Naive_RAG"
        }
        
    # 2. Dense retrieval only (top-k)
    retriever = db.as_retriever(search_kwargs={"k": k})
    docs = retriever.invoke(question)
    
    contexts = [d.page_content for d in docs]
    context_text = "\n\n".join(contexts)
    
    # 3. Direct generation
    ttft_start = time.time()
    answer = generate_answer(question, context_text)
    latency = time.time() - start_time
    
    return {
        "answer": answer,
        "contexts": contexts,
        "latency": latency,
        "domain": domain,
        "retrieved_count": len(docs),
        "baseline": "Naive_RAG"
    }

if __name__ == "__main__":
    res = run_naive_rag("What is attention mechanism in transformer models?", domain="it")
    print(f"Latency: {res['latency']:.2f}s | Contexts: {len(res['contexts'])}")
    print(f"Answer:\n{res['answer'][:200]}...")

