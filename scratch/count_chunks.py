from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
import os

DB_BASE_PATH = "db/vector_stores"
embeddings = OllamaEmbeddings(model="nomic-embed-text")

domains = [d.replace("_index", "") for d in os.listdir(DB_BASE_PATH) if os.path.isdir(os.path.join(DB_BASE_PATH, d))]

print("--- Chunk Count per Domain ---")
for domain in domains:
    db_path = os.path.join(DB_BASE_PATH, f"{domain}_index")
    try:
        vectorstore = Chroma(
            persist_directory=db_path,
            embedding_function=embeddings,
            collection_name=f"{domain}_collection"
        )
        # Using ._collection.count() for efficiency
        count = vectorstore._collection.count()
        print(f" - {domain.upper()}: {count} chunks")
    except Exception as e:
        print(f" x Error reading {domain}: {e}")
