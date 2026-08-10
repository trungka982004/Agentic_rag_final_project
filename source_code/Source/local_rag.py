import os
import sys
import logging
import re
import time
from typing import List, Optional, Dict, Any, Union

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
        EnsembleRetriever = None

class Config:
    """System-wide configuration parameters."""
    DB_BASE_PATH: str = "db/vector_stores"
    EMBEDDING_MODEL: str = "bge-m3"
    LLM_MODEL: str = "qwen2.5:7b"
    TEMPERATURE: float = 0.0
    CONTEXT_WINDOW: int = 4096
    MAX_TOKENS: int = 1024
    KEEP_ALIVE: str = "5m"

# Configure standard logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize LLM and Embedding components
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

# Global caches for optimization
_db_cache: Dict[str, Chroma] = {}
_bm25_cache: Dict[str, BM25Retriever] = {}
_domains_cache: List[str] = []
_domains_cache_ts: float = 0.0
_DOMAINS_TTL: float = 30.0


def get_active_domains() -> List[str]:
    """Retrieves list of active domains from disk with TTL caching.

    Returns:
        A list of domain names.
    """
    global _domains_cache, _domains_cache_ts
    now = time.monotonic()
    if _domains_cache and (now - _domains_cache_ts) < _DOMAINS_TTL:
        return _domains_cache

    raw_path = "data/raw"
    defaults = ["it", "math", "physics", "electronics", "economics", "law", "medicine", "agriculture", "construction"]
    if not os.path.exists(raw_path):
        _domains_cache = defaults
        _domains_cache_ts = now
        return defaults
    try:
        domains = [d for d in os.listdir(raw_path) if os.path.isdir(os.path.join(raw_path, d)) and not d.startswith(".")]
        for d in defaults:
            if d not in domains:
                domains.append(d)
        _domains_cache = domains
        _domains_cache_ts = now
        return domains
    except Exception as e:
        logger.warning(f"Error reading domains from disk: {e}. Using defaults.")
        return defaults


def clear_rag_caches() -> None:
    """Invalidates all runtime RAG cache structures."""
    global _db_cache, _bm25_cache, _domains_cache, _domains_cache_ts
    _db_cache.clear()
    _bm25_cache.clear()
    _domains_cache = []
    _domains_cache_ts = 0.0
    logger.info("All RAG caches have been successfully invalidated.")


def get_vector_db(domain: str) -> Optional[Chroma]:
    """Retrieves or instantiates the Chroma vector store for a domain.

    Args:
        domain: Domain target string.

    Returns:
        The cached Chroma instance or None if not found.
    """
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
    """Classifies query topic into one of the active domains.

    Args:
        query: User input query.

    Returns:
        The matched domain name.
    """
    query_lower = query.lower()
    active_domains = get_active_domains()

    # Heuristics based fast-routing
    if any(kw in query_lower for kw in ["it", "network", "code", "python", "programming", "algorithm", "software", "computer", "deep learning", "machine learning", "resnet", "bert", "mapreduce", "transformer"]):
        return "it"
    if any(kw in query_lower for kw in ["math", "integral", "derivative", "equation", "riemann", "prime", "theorem", "entropy", "algebra"]):
        return "math"
    if any(kw in query_lower for kw in ["physics", "quantum", "gravity", "gravitational", "black hole", "relativity", "mechanics", "cosmological", "inflation"]):
        return "physics"
    if any(kw in query_lower for kw in ["electronics", "circuit", "transistor", "neuromorphic", "hardware", "sensor", "voltage", "neuronal"]):
        return "electronics"
    if any(kw in query_lower for kw in ["economic", "economics", "kinh tế", "finance", "lãi suất", "tài chính", "ngân hàng", "gdp", "lạm phát", "thị trường"]):
        return "economics"
    if any(kw in query_lower for kw in ["law", "pháp luật", "luật", "bộ luật", "pháp lý", "hợp đồng", "tố tụng", "hiến pháp", "quy định", "nghị định"]):
        return "law"
    if any(kw in query_lower for kw in ["medicine", "medical", "y học", "y tế", "dược", "bệnh học", "chẩn đoán", "điều trị", "lâm sàng", "bệnh nhân", "thuốc"]):
        return "medicine"
    if any(kw in query_lower for kw in ["agriculture", "agricultural", "nông nghiệp", "cây trồng", "nông sản", "đất đai", "phân bón", "sâu bệnh", "trồng trọt", "chăn nuôi"]):
        return "agriculture"
    if any(kw in query_lower for kw in ["construction", "xây dựng", "kết cấu", "bê tông", "kiến trúc", "công trình", "thi công", "vật liệu xây dựng", "bim"]):
        return "construction"

    for d in active_domains:
        if d in query_lower or d.replace("_", " ") in query_lower or d.replace("-", " ") in query_lower:
            return d

    if not llm:
        return active_domains[0] if active_domains else "it"

    categories_str = ", ".join(f"'{d}'" for d in active_domains)
    prompt = ChatPromptTemplate.from_template(f"""
    You are a professional router. Classify the following question into one of these categories: 
    {categories_str}.
    If it doesn't fit any, choose the closest one.
    Answer ONLY with the category name in lowercase.
    
    Question: {{query}}
    Category:""")

    chain = prompt | llm | StrOutputParser()
    try:
        domain = chain.invoke({"query": query}).strip().lower()
        if domain not in active_domains:
            logger.info(f"LLM returned unknown domain '{domain}'. Defaulting to 'physics'.")
            return "physics"
        return domain
    except Exception as e:
        logger.error(f"Domain classification failed: {e}")
        return "physics"


def find_exact_source_path(db: Chroma, target_file: str) -> Optional[str]:
    """Resolves the absolute source path of a document inside Chroma DB metadata.

    Args:
        db: Active ChromaDB instance.
        target_file: Document base filename.

    Returns:
        The resolved source path or None.
    """
    try:
        db_data = db.get()
        if db_data and db_data.get('metadatas'):
            for meta in db_data['metadatas']:
                if meta and 'source' in meta:
                    source_val = meta['source']
                    if os.path.basename(source_val).lower() == target_file.lower():
                        return source_val
    except Exception as e:
        logger.error(f"Error finding exact source path: {e}")
    return None


def get_bm25_retriever(db: Chroma, domain: str, k: int = 5, target_file: str = None) -> Optional[BM25Retriever]:
    """Generates a cached BM25 sparse retriever from documents in the ChromaDB.

    Args:
        db: Active ChromaDB instance.
        domain: Domain target string.
        k: Chunk return limit.
        target_file: Restricting filter source path.

    Returns:
        BM25Retriever instance or None.
    """
    cache_key = f"{domain}_{target_file}" if target_file else domain
    if cache_key in _bm25_cache:
        retriever = _bm25_cache[cache_key]
        retriever.k = k
        return retriever

    try:
        logger.info(f"Building BM25 retriever cache for key '{cache_key}'...")
        if target_file:
            target_path = find_exact_source_path(db, target_file) or os.path.join("data/raw", domain, target_file)
            docs_data = db.get(where={"source": target_path})
        else:
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
        _bm25_cache[cache_key] = retriever
        logger.info(f"Successfully cached BM25 retriever for key '{cache_key}'.")
        return retriever
    except Exception as e:
        logger.error(f"Failed to create BM25 retriever: {e}")
        return None


def retrieve_context(query: str, domain: str, k: int = 5, target_file: Optional[str] = None) -> str:
    """Executes Hybrid Search combining BM25 and Vector retrievals.

    Args:
        query: User search query.
        domain: Target document domain.
        k: Target retrieval limit.
        target_file: Explicit target filename if specified.

    Returns:
        Formatted context string containing sources.
    """
    query_lower = query.lower()

    if target_file:
        found_domain = None
        for d in get_active_domains():
            domain_path = os.path.join("data/raw", d)
            if os.path.exists(domain_path) and target_file in os.listdir(domain_path):
                found_domain = d
                break
        if found_domain:
            domain = found_domain
            logger.info(f"Explicitly targeting PDF '{target_file}' in domain '{domain}'.")
        else:
            logger.warning(f"Explicit target PDF '{target_file}' not found in raw data directories.")
    else:
        found_override = False
        for d in get_active_domains():
            domain_path = os.path.join("data/raw", d)
            if os.path.exists(domain_path):
                for file in os.listdir(domain_path):
                    if file.lower().endswith(".pdf"):
                        name_without_ext = file[:-4]
                        if file.lower() in query_lower or (len(name_without_ext) > 5 and name_without_ext.lower() in query_lower):
                            logger.info(f"Found target PDF '{file}' in domain '{d}' on disk. Overriding domain to '{d}'.")
                            domain = d
                            target_file = file
                            found_override = True
                            break
                if found_override:
                    break

    db = get_vector_db(domain)
    if not db:
        return "No database found for this domain."

    search_kwargs: Dict[str, Any] = {"k": k}
    if target_file:
        target_path = find_exact_source_path(db, target_file) or os.path.join("data/raw", domain, target_file)
        search_kwargs["filter"] = {"source": target_path}
        logger.info(f"Restricting ChromaDB search to target PDF: {target_path}")

        summary_keywords = ["tóm tắt", "tóm lược", "sơ lược", "giới thiệu", "khái quát", "summarize", "summary", "overview", "introduction", "intro"]
        is_summary_req = any(kw in query_lower for kw in summary_keywords)

        if is_summary_req:
            logger.info("Summary request detected for target PDF. Retrieving sorted pages directly.")
            all_chunks_data = db.get(where={"source": target_path})
            if all_chunks_data and all_chunks_data.get('documents'):
                all_docs = [
                    Document(
                        page_content=content,
                        metadata=all_chunks_data['metadatas'][i] if all_chunks_data.get('metadatas') else {}
                    )
                    for i, content in enumerate(all_chunks_data['documents'])
                ]
                all_docs.sort(key=lambda d: d.metadata.get('page', 0))

                selected_docs = all_docs if len(all_docs) <= 15 else all_docs[:k]
                formatted_chunks = []
                for doc in selected_docs:
                    src = doc.metadata.get('source', 'Unknown Source')
                    page = doc.metadata.get('page', 'Unknown Page')
                    formatted_chunks.append(f"--- Source: {src} (Page {page}) ---\n{doc.page_content}")

                logger.info(f"Direct page retrieval selected {len(selected_docs)} chunks from target PDF.")
                return "\n\n".join(formatted_chunks)

    vector_retriever = db.as_retriever(search_kwargs=search_kwargs)
    bm25_retriever = get_bm25_retriever(db, domain=domain, k=k, target_file=target_file)

    try:
        if bm25_retriever and EnsembleRetriever:
            semantic_indicators = ["giải thích", "tại sao", "như thế nào", "ý nghĩa", "khái niệm", "what is", "why", "how", "explain", "describe", "mô tả"]
            is_semantic = any(ind in query_lower for ind in semantic_indicators)

            if is_semantic:
                logger.info("Semantic query detected. Using dense-heavy weights [0.3 BM25, 0.7 Vector].")
                weights = [0.3, 0.7]
            else:
                logger.info("Keyword-precise query detected. Using sparse-heavy weights [0.6 BM25, 0.4 Vector].")
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

    # Deduplicate overlapping context chunks
    seen_contents = set()
    unique_docs = []
    for d in filtered_docs:
        snippet = d.page_content.strip()[:150]
        if snippet not in seen_contents:
            seen_contents.add(snippet)
            unique_docs.append(d)

    final_docs = unique_docs[:k]
    logger.info(f"Retrieved {len(final_docs)} unique documents after deduplication.")

    return "\n\n".join([
        f"--- Source: {d.metadata.get('source', 'Unknown')} (Page {d.metadata.get('page', '?')}) ---\n{d.page_content}"
        for d in final_docs
    ])


def generate_answer(query: str, context: str) -> str:
    """Generates structured answer using LLM from provided context.

    Args:
        query: User input query.
        context: Context facts text.

    Returns:
        Response string from the LLM.
    """
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
