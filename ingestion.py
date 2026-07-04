import os
import shutil
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma 

# 1. Path configuration according to new structure
RAW_DATA_PATH = "data/raw"
DB_BASE_PATH = "db/vector_stores"

def ingest_docs(target_domain: str = None, force_rebuild: bool = False):
    # Initialize Embedding model (bge-m3) - Much faster and optimized for search
    embeddings = OllamaEmbeddings(model="bge-m3")

    # Check root folder
    if not os.path.exists(RAW_DATA_PATH):
        print(f"Directory not found: {RAW_DATA_PATH}", flush=True)
        return

    # Iterate through each domain folder (it, math, physics, electronics)
    if target_domain and target_domain in ["it", "math", "physics", "electronics"]:
        domains = [target_domain]
    else:
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
        # Delete old DB to refresh with new embedding model if force_rebuild is True.
        # Handle Windows file lock permission errors gracefully.
        cleared = False
        if force_rebuild and os.path.exists(domain_db_path):
            print(f"Clearing old index (force_rebuild=True): {domain_db_path}", flush=True)
            try:
                shutil.rmtree(domain_db_path)
                cleared = True
            except Exception as e:
                print(f"Could not remove directory {domain_db_path} due to file lock: {e}. Will clear collection inside database.", flush=True)

        # Initialize Chroma for the domain
        vectorstore = Chroma(
            persist_directory=domain_db_path,
            embedding_function=embeddings,
            collection_name=f"{domain}_collection"
        )

        if force_rebuild and os.path.exists(domain_db_path) and not cleared:
            try:
                vectorstore.delete_collection()
                # Reinitialize empty vector store
                vectorstore = Chroma(
                    persist_directory=domain_db_path,
                    embedding_function=embeddings,
                    collection_name=f"{domain}_collection"
                )
                print(f"Successfully cleared collection '{domain}_collection' inside existing database.", flush=True)
            except Exception as e:
                print(f"Failed to clear collection: {e}. Proceeding anyway...", flush=True)

        # Retrieve already indexed source filenames to enable incremental ingestion
        existing_sources = set()
        if not force_rebuild:
            try:
                db_data = vectorstore.get()
                if db_data and db_data.get('metadatas'):
                    for meta in db_data['metadatas']:
                        if meta and 'source' in meta:
                            existing_sources.add(os.path.basename(meta['source']))
                print(f"Found {len(existing_sources)} already indexed documents in '{domain}_collection'.", flush=True)
            except Exception as e:
                print(f"Error reading existing sources for domain {domain}: {e}", flush=True)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512, 
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", " ", ""]
        )

        # Filter out files that are already indexed
        files_to_process = []
        for file in pdf_files:
            if not force_rebuild and file in existing_sources:
                continue
            files_to_process.append(file)

        if not files_to_process:
            print(f"All files in domain '{domain}' are already indexed. Skipping.", flush=True)
            continue

        print(f"Found {len(files_to_process)} new/remaining files out of {len(pdf_files)} to index. Starting streaming ingestion...", flush=True)
        total_chunks = 0

        for file in files_to_process:
            file_path = os.path.join(domain_input_path, file)
            print(f"  -> Processing {file}...", flush=True)
            try:
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
            except Exception as e:
                print(f"Error processing file {file}: {e}", flush=True)
            
        print(f"Completed storage for domain {domain}! Total {total_chunks} chunks saved.", flush=True)

if __name__ == "__main__":
    # Ensure DB folder exists
    if not os.path.exists(DB_BASE_PATH): 
        os.makedirs(DB_BASE_PATH)
    
    ingest_docs()
    print("\n\nALL DOMAINS HAVE BEEN SUCCESSFULLY VECTORIZED!", flush=True)