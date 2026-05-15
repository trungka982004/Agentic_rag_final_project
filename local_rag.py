import os
import sys
import logging
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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize shared components
try:
    embeddings = OllamaEmbeddings(model=Config.EMBEDDING_MODEL)
    llm = ChatOllama(
        model=Config.LLM_MODEL, 
        temperature=Config.TEMPERATURE,
        num_ctx=Config.CONTEXT_WINDOW
    )
except Exception as e:
    logger.error(f"Failed to initialize Ollama components: {e}")
    embeddings = None
    llm = None

def get_vector_db(domain: str) -> Optional[Chroma]:
    """Loads the specific ChromaDB for a given domain."""
    db_path = os.path.join(Config.DB_BASE_PATH, f"{domain}_index")
    if not os.path.exists(db_path):
        logger.warning(f"Database path not found: {db_path}")
        return None
    
    return Chroma(
        persist_directory=db_path,
        embedding_function=embeddings,
        collection_name=f"{domain}_collection"
    )

def classify_domain(query: str) -> str:
    """Classifies the user query into one of the pre-defined domains."""
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

def get_bm25_retriever(db: Chroma, k: int = 5) -> Optional[BM25Retriever]:
    """Creates a BM25 retriever from the documents stored in a ChromaDB instance."""
    try:
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
        return retriever
    except Exception as e:
        logger.error(f"Failed to create BM25 retriever: {e}")
        return None

def retrieve_context(query: str, domain: str, k: int = 5) -> str:
    """Retrieves context using Hybrid Search (BM25 + Vector)."""
    db = get_vector_db(domain)
    if not db:
        return "No database found for this domain."
    
    vector_retriever = db.as_retriever(search_kwargs={"k": k})
    bm25_retriever = get_bm25_retriever(db, k=k)
    
    try:
        if bm25_retriever and EnsembleRetriever:
            ensemble_retriever = EnsembleRetriever(
                retrievers=[bm25_retriever, vector_retriever], 
                weights=[0.5, 0.5]
            )
            filtered_docs = ensemble_retriever.invoke(query)
        else:
            filtered_docs = vector_retriever.invoke(query)
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        return "Error occurred during information retrieval."
    
    if not filtered_docs:
        return "No relevant information found in the database."

    return "\n\n".join([
        f"--- Source: {d.metadata.get('source', 'Unknown')} (Page {d.metadata.get('page', '?')}) ---\n{d.page_content}" 
        for d in filtered_docs
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

