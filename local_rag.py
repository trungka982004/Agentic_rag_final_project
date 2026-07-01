import os
import sys
import logging
import re
from typing import List, Optional

from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

# Handle EnsembleRetriever location based on installed langchain version
try:
    from langchain.retrievers import EnsembleRetriever
except (ImportError, ModuleNotFoundError):
    try:
        from langchain_classic.retrievers import EnsembleRetriever
    except (ImportError, ModuleNotFoundError):
        # Fallback if both fail, will error at runtime if used
        EnsembleRetriever = None

# --- CONFIGURATION ---
class Config:
    DB_BASE_PATH = "db/vector_stores"
    EMBEDDING_MODEL = "bge-m3"
    LLM_MODEL = "qwen2.5:7b"
    DOMAINS = ["it", "math", "physics", "electronics"]
    TEMPERATURE = 0
    CONTEXT_WINDOW = 4096
    MAX_TOKENS = 1024
    KEEP_ALIVE = "5m"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize shared components
try:
    embeddings = OllamaEmbeddings(model=Config.EMBEDDING_MODEL)
    llm = ChatOllama(
        model=Config.LLM_MODEL, 
        temperature=Config.TEMPERATURE,
        num_ctx=Config.CONTEXT_WINDOW,
        num_predict=Config.MAX_TOKENS,
        keep_alive=Config.KEEP_ALIVE
    )
except Exception as e:
    logger.error(f"Failed to initialize Ollama components: {e}")
    embeddings = None
    llm = None

_db_cache = {}
_bm25_cache = {}

def clear_rag_caches():
    """Clears the DB cache and BM25 cache to force reloading from disk."""
    global _db_cache, _bm25_cache
    _db_cache.clear()
    _bm25_cache.clear()
    logger.info("[*] All RAG caches have been successfully invalidated.")

def get_vector_db(domain: str) -> Optional[Chroma]:
    """Loads the specific ChromaDB for a given domain, using a memory cache to prevent recreation."""
    if domain in _db_cache:
        return _db_cache[domain]

    db_path = os.path.join(Config.DB_BASE_PATH, f"{domain}_index")
    if not os.path.exists(db_path):
        logger.warning(f"Database path not found: {db_path}")
        return None
    
    db = Chroma(
        persist_directory=db_path,
        embedding_function=embeddings,
        collection_name=f"{domain}_collection"
    )
    _db_cache[domain] = db
    return db

def classify_domain(query: str) -> str:
    """Classifies the user query into one of the pre-defined domains using fast routing and LLM fallback."""
    query_lower = query.lower()
    
    # Fast Keyword Routing
    if any(kw in query_lower for kw in ["it", "network", "code", "python", "programming", "algorithm", "software", "computer", "deep learning", "machine learning", "resnet", "bert", "mapreduce", "transformer"]):
        return "it"
    if any(kw in query_lower for kw in ["math", "integral", "derivative", "equation", "riemann", "prime", "theorem", "entropy", "algebra"]):
        return "math"
    if any(kw in query_lower for kw in ["physics", "quantum", "gravity", "gravitational", "black hole", "relativity", "mechanics", "cosmological", "inflation"]):
        return "physics"
    if any(kw in query_lower for kw in ["electronics", "circuit", "transistor", "neuromorphic", "hardware", "sensor", "voltage", "neuronal"]):
        return "electronics"

    if not llm:
        return "physics" # Fallback

    prompt = ChatPromptTemplate.from_template("""
    You are a professional router. Classify the following question into one of these 4 categories: 
    'it', 'math', 'physics', 'electronics'.
    If it doesn't fit any, choose the closest one.
    Answer ONLY with the category name in lowercase.
    
    Question: {query}
    Category:""")
    
    chain = prompt | llm | StrOutputParser()
    try:
        domain = chain.invoke({"query": query}).strip().lower()
        if domain not in Config.DOMAINS:
            logger.info(f"LLM returned unknown domain '{domain}'. Falling back to 'physics'.")
            return "physics"
        return domain
    except Exception as e:
        logger.error(f"Domain classification failed: {e}")
        return "physics"

def get_bm25_retriever(db: Chroma, domain: str, k: int = 5) -> Optional[BM25Retriever]:
    """Creates a BM25 retriever from the documents stored in a ChromaDB instance, utilizing caching."""
    if domain in _bm25_cache:
        retriever = _bm25_cache[domain]
        retriever.k = k
        return retriever

    try:
        logger.info(f"Building BM25 retriever cache for domain '{domain}'...")
        docs_data = db.get()
        if not docs_data or not docs_data.get('documents'):
            return None
            
        documents = [
            Document(
                page_content=content,
                metadata=docs_data['metadatas'][i] if docs_data.get('metadatas') else {}
            )
            for i, content in enumerate(docs_data['documents'])
        ]
        
        if not documents:
            return None
            
        retriever = BM25Retriever.from_documents(documents)
        retriever.k = k
        _bm25_cache[domain] = retriever
        logger.info(f"Successfully cached BM25 retriever for domain '{domain}'.")
        return retriever
    except Exception as e:
        logger.error(f"Failed to create BM25 retriever: {e}")
        return None

def retrieve_context(query: str, domain: str, k: int = 5) -> str:
    """Retrieves context using Hybrid Search (BM25 + Vector) with dynamic weights and deduplication."""
    # Detect target PDF filename in query to override domain routing
    pdf_matches = re.findall(r"[\w\d_.-]+\.pdf", query, re.IGNORECASE)
    if pdf_matches:
        target_pdf = pdf_matches[0]
        # Look for this PDF in raw data subfolders to find the actual domain it was ingested into
        for d in Config.DOMAINS:
            if os.path.exists(os.path.join("data/raw", d, target_pdf)):
                logger.info(f"[*] Found target PDF '{target_pdf}' in domain '{d}' on disk. Overriding retrieval domain from '{domain}' to '{d}'.")
                domain = d
                break

    db = get_vector_db(domain)
    if not db:
        return "No database found for this domain."
    
    vector_retriever = db.as_retriever(search_kwargs={"k": k})
    bm25_retriever = get_bm25_retriever(db, domain=domain, k=k)
    
    try:
        if bm25_retriever and EnsembleRetriever:
            # Dynamic weights calculation based on query characteristics
            query_lower = query.lower()
            semantic_indicators = ["giải thích", "tại sao", "như thế nào", "ý nghĩa", "khái niệm", "what is", "why", "how", "explain", "describe", "mô tả"]
            is_semantic = any(ind in query_lower for ind in semantic_indicators)
            
            if is_semantic:
                logger.info("[*] Semantic query detected. Using dense-heavy weights [0.3 BM25, 0.7 Vector].")
                weights = [0.3, 0.7]
            else:
                logger.info("[*] Keyword-precise query detected. Using sparse-heavy weights [0.6 BM25, 0.4 Vector].")
                weights = [0.6, 0.4]
                
            ensemble_retriever = EnsembleRetriever(
                retrievers=[bm25_retriever, vector_retriever], 
                weights=weights
            )
            filtered_docs = ensemble_retriever.invoke(query)
        else:
            filtered_docs = vector_retriever.invoke(query)
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        return "Error occurred during information retrieval."
    
    if not filtered_docs:
        return "No relevant information found in the database."

    # Deduplicate retrieved documents based on page content snippets to save tokens and prevent context clutter
    seen_contents = set()
    unique_docs = []
    for d in filtered_docs:
        snippet = d.page_content.strip()[:150]
        if snippet not in seen_contents:
            seen_contents.add(snippet)
            unique_docs.append(d)
            
    final_docs = unique_docs[:k]
    logger.info(f"[*] Retrieved {len(final_docs)} unique documents after deduplication.")

    return "\n\n".join([
        f"--- Source: {d.metadata.get('source', 'Unknown')} (Page {d.metadata.get('page', '?')}) ---\n{d.page_content}" 
        for d in final_docs
    ])

def generate_answer(query: str, context: str) -> str:
    """Generates an answer using the LLM with a specialized academic prompt."""
    if not llm:
        return "LLM not initialized."

    template = """
    You are a professional scientific assistant. Use the following [CONTEXT] to answer the user's [QUESTION].
    
    MANDATORY RULES:
    1. Only use the information provided in the [CONTEXT]. Do not invent external knowledge.
    2. If the [CONTEXT] does not contain enough information, state: "I'm sorry, the provided documents do not contain enough information to answer this question."
    3. Your answer must be clear, structured, and highly accurate.
    4. Provide citations (filename and page number) whenever possible.

    [CONTEXT]:
    {context}

    [QUESTION]:
    {query}

    [ANSWER]:
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    
    print("\n--- AI Response ---")
    full_response = ""
    try:
        for chunk in chain.stream({"query": query, "context": context}):
            print(chunk, end="", flush=True)
            full_response += chunk
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        return f"Error during generation: {e}"
        
    print("\n-------------------\n")
    return full_response

