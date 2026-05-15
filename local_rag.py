import os
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_core.documents import Document

# --- CONFIGURATION ---
DB_BASE_PATH = "db/vector_stores"
EMBEDDING_MODEL = "bge-m3"
LLM_MODEL = "qwen2.5:7b"  # Optimized version
DOMAINS = ["it", "math", "physics", "electronics"]

# Initialize shared components
embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
llm = ChatOllama(
    model=LLM_MODEL, 
    temperature=0,
    num_ctx=4096  # Optimized for processing multiple long chunks
)

def get_vector_db(domain):
    """Loads the specific ChromaDB for a domain."""
    db_path = os.path.join(DB_BASE_PATH, f"{domain}_index")
    if not os.path.exists(db_path):
        return None
    
    return Chroma(
        persist_directory=db_path,
        embedding_function=embeddings,
        collection_name=f"{domain}_collection"
    )

def classify_domain(query):
    """Classifies the user query into one of the 4 domains using LLM."""
    prompt = ChatPromptTemplate.from_template("""
    You are a professional router. Classify the following question into one of these 4 categories: 
    'it', 'math', 'physics', 'electronics'.
    If it doesn't fit any, choose the closest one.
    Answer ONLY with the category name in lowercase.
    
    Question: {query}
    Category:""")
    
    chain = prompt | llm | StrOutputParser()
    domain = chain.invoke({"query": query}).strip().lower()
    
    # Validation
    if domain not in DOMAINS:
        # Fallback to physics or first available if LLM hallucinates the category name
        return "physics" 
    return domain

def get_bm25_retriever(db, k=5):
    docs_data = db.get()
    documents = []
    if not docs_data or not docs_data.get('documents'):
        return None
        
    for i in range(len(docs_data['documents'])):
        doc = Document(
            page_content=docs_data['documents'][i],
            metadata=docs_data['metadatas'][i] if docs_data.get('metadatas') else {}
        )
        documents.append(doc)
    if not documents:
        return None
    retriever = BM25Retriever.from_documents(documents)
    retriever.k = k
    return retriever

def retrieve_context(query, domain, k=5, score_threshold=0.3):
    """Retrieves relevant chunks from the domain-specific vector DB using Hybrid Search (BM25 + Vector)."""
    db = get_vector_db(domain)
    if not db:
        return "No database found for this domain."
    
    vector_retriever = db.as_retriever(search_kwargs={"k": k})
    bm25_retriever = get_bm25_retriever(db, k=k)
    
    if bm25_retriever:
        ensemble_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, vector_retriever], weights=[0.5, 0.5]
        )
        filtered_docs = ensemble_retriever.invoke(query)
    else:
        filtered_docs = vector_retriever.invoke(query)
    
    if not filtered_docs:
        return "No relevant information found in the database."

    context = "\n\n".join([
        f"--- Source: {d.metadata.get('source', 'Unknown')} (Page {d.metadata.get('page', '?')}) ---\n{d.page_content}" 
        for d in filtered_docs
    ])
    return context

def generate_answer(query, context):
    """Generates an answer using the Strict Scientific Prompt."""
    template = """
    You are a professional scientific assistant. Use the following [CONTEXT] to answer the user's [QUESTION].
    
    MANDATORY RULES:
    1. Only use the information provided in the [CONTEXT]. Do not invent external knowledge.
    2. If the [CONTEXT] does not contain enough information to answer, state: "I'm sorry, the provided documents do not contain enough information to answer this question."
    3. Your answer must be clear, structured (use bullet points if necessary), and highly accurate.
    4. Provide citations (filename and page number) whenever possible.

    [CONTEXT]:
    {context}

    [QUESTION]:
    {query}

    [ANSWER]:
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    
    # Using stream for better UX
    print("\n--- AI Response ---")
    full_response = ""
    for chunk in chain.stream({"query": query, "context": context}):
        print(chunk, end="", flush=True)
        full_response += chunk
    print("\n-------------------\n")
    return full_response

