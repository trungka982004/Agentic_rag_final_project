import os
import shutil
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma 

# 1. Path configuration according to new structure
RAW_DATA_PATH = "data/raw"
DB_BASE_PATH = "db/vector_stores"

def ingest_docs():
    # Initialize Embedding model (bge-m3) - Much faster and optimized for search
    embeddings = OllamaEmbeddings(model="bge-m3")

    # Check root folder
    if not os.path.exists(RAW_DATA_PATH):
        print(f"Directory not found: {RAW_DATA_PATH}", flush=True)
        return

    # Iterate through each domain folder (it, math, physics, electronics)
    domains = [d for d in os.listdir(RAW_DATA_PATH) if os.path.isdir(os.path.join(RAW_DATA_PATH, d))]
    
    for domain in domains:
        domain_input_path = os.path.join(RAW_DATA_PATH, domain)
        domain_db_path = os.path.join(DB_BASE_PATH, f"{domain}_index")
        
        print(f"\n--- Processing domain: {domain.upper()} ---", flush=True)

        pdf_files = [f for f in os.listdir(domain_input_path) if f.endswith(".pdf")]
        
        if not pdf_files:
            print(f"No PDF files in {domain}. Skipping...", flush=True)
            continue

        # Save to separate ChromaDB for each domain
        # Delete old DB to refresh with new embedding model
        if os.path.exists(domain_db_path):
            print(f"Clearing old index: {domain_db_path}", flush=True)
            shutil.rmtree(domain_db_path)

        # Initialize Chroma for the domain
        vectorstore = Chroma(
            persist_directory=domain_db_path,
            embedding_function=embeddings,
            collection_name=f"{domain}_collection"
        )

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512, 
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", " ", ""]
        )

        print(f"Found {len(pdf_files)} files. Starting streaming ingestion...", flush=True)
        total_chunks = 0

        for file in pdf_files:
            file_path = os.path.join(domain_input_path, file)
            print(f"  -> Processing {file}...", flush=True)
            loader = PyPDFLoader(file_path)
            loaded_docs = loader.load()
            
            for doc in loaded_docs:
                doc.metadata["domain"] = domain  # Assign domain label to each page
            
            splits = text_splitter.split_documents(loaded_docs)
            total_chunks += len(splits)
            
            batch_size = 50
            for i in range(0, len(splits), batch_size):
                batch = splits[i : i + batch_size]
                vectorstore.add_documents(batch)
            
            # Clear references to free memory explicitly
            del loaded_docs
            del splits
            
        print(f"Completed storage for domain {domain}! Total {total_chunks} chunks saved.", flush=True)

if __name__ == "__main__":
    # Ensure DB folder exists
    if not os.path.exists(DB_BASE_PATH): 
        os.makedirs(DB_BASE_PATH)
    
    ingest_docs()
    print("\n\nALL DOMAINS HAVE BEEN SUCCESSFULLY VECTORIZED!", flush=True)