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
    # Initialize Embedding model (nomic-embed-text) - Much faster and optimized for search
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    # Check root folder
    if not os.path.exists(RAW_DATA_PATH):
        print(f"❌ Directory not found: {RAW_DATA_PATH}")
        return

    # Iterate through each domain folder (it, math, physics, electronics)
    domains = [d for d in os.listdir(RAW_DATA_PATH) if os.path.isdir(os.path.join(RAW_DATA_PATH, d))]
    
    for domain in domains:
        domain_input_path = os.path.join(RAW_DATA_PATH, domain)
        domain_db_path = os.path.join(DB_BASE_PATH, f"{domain}_index")
        
        print(f"\n--- 📦 Processing domain: {domain.upper()} ---")

        # Load all PDFs in the domain folder
        documents = []
        pdf_files = [f for f in os.listdir(domain_input_path) if f.endswith(".pdf")]
        
        if not pdf_files:
            print(f"⚠️ No PDF files in {domain}. Skipping...")
            continue

        for file in pdf_files:
            file_path = os.path.join(domain_input_path, file)
            loader = PyPDFLoader(file_path)
            # Manually add metadata to ensure consistency
            loaded_docs = loader.load()
            for doc in loaded_docs:
                doc.metadata["domain"] = domain  # Assign domain label to each page
            documents.extend(loaded_docs)
    
        print(f"✅ Loaded {len(documents)} document pages from {len(pdf_files)} files.")

        # Split text (Chunking) according to academic standards
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=150,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        splits = text_splitter.split_documents(documents)
        print(f"✅ Split into {len(splits)} chunks.")

        # Save to separate ChromaDB for each domain
        # Delete old DB to refresh with new embedding model
        if os.path.exists(domain_db_path):
            print(f"🧹 Clearing old index: {domain_db_path}")
            shutil.rmtree(domain_db_path)

        # Initialize Chroma and add documents in batches
        vectorstore = Chroma(
            persist_directory=domain_db_path,
            embedding_function=embeddings,
            collection_name=f"{domain}_collection"
        )

        batch_size = 50
        print(f"🚀 Starting ingestion for {len(splits)} chunks (Batch size: {batch_size})...")
        
        for i in range(0, len(splits), batch_size):
            batch = splits[i : i + batch_size]
            vectorstore.add_documents(batch)
            print(f"📦 Progress: {min(i + batch_size, len(splits))}/{len(splits)} chunks saved...")
        
        print(f"✨ Completed storage for domain {domain}!")

if __name__ == "__main__":
    # Ensure DB folder exists
    if not os.path.exists(DB_BASE_PATH): 
        os.makedirs(DB_BASE_PATH)
    
    ingest_docs()
    print("\n\n🎉 ALL DOMAINS HAVE BEEN SUCCESSFULLY VECTORIZED!")