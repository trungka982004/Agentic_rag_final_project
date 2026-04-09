import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

# 1. Cấu hình đường dẫn
DATA_PATH = "data/"
DB_PATH = "db/"

def ingest_docs():
    # Bước 1: Load tất cả file PDF trong thư mục data
    documents = []
    for file in os.listdir(DATA_PATH):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(DATA_PATH, file))
            documents.extend(loader.load())
    
    print(f"✅ Đã tải {len(documents)} trang tài liệu.")

    # Bước 2: Chia nhỏ văn bản (Chunking)
    # chunk_size=1000 và overlap=100 giúp giữ ngữ cảnh giữa các đoạn
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    splits = text_splitter.split_documents(documents)
    print(f"✅ Đã chia thành {len(splits)} đoạn văn bản (chunks).")

    # Bước 3: Khởi tạo Embedding model (sử dụng Qwen qua Ollama hoặc mxbai-embed-large)
    # Lưu ý: Ollama có model chuyên dụng cho embedding như 'mxbai-embed-large' 
    # sẽ hiệu quả hơn dùng trực tiếp model chat để embed.
    embeddings = OllamaEmbeddings(model="qwen2.5:7b")

    # Bước 4: Lưu vào ChromaDB
    print("🚀 Đang tiến hành Vectorizing và lưu vào DB... (Vui lòng đợi)")
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=DB_PATH
    )
    
    print(f"✨ Hoàn tất! Vector Database đã được lưu tại: {DB_PATH}")

if __name__ == "__main__":
    # Tạo thư mục nếu chưa có
    if not os.path.exists(DATA_PATH): os.makedirs(DATA_PATH)
    
    ingest_docs()