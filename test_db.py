from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

# Configuration must match ingestion.py
# Example: Testing the 'physics' domain
DOMAIN = "physics" 
DB_PATH = f"db/vector_stores/{DOMAIN}_index"

print(f"🔍 Testing Vector DB for domain: {DOMAIN.upper()}...")

# 1. Initialize Embeddings (must be the same as ingestion)
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# 2. Load the vector store
vectorstore = Chroma(
    persist_directory=DB_PATH, 
    embedding_function=embeddings,
    collection_name=f"{DOMAIN}_collection"
)

# 3. Perform a test query
query = "What are the fundamental laws of physics mentioned in the documents?"
print(f"❓ Query: {query}")

docs = vectorstore.similarity_search(query, k=3)

print(f"\n✅ Found {len(docs)} relevant chunks:")
for i, doc in enumerate(docs):
    print(f"\n--- Chunk {i+1} (Source: {doc.metadata.get('source', 'Unknown')}) ---")
    print(f"{doc.page_content[:300]}...")