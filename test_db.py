from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

# Phải dùng đúng cấu hình như lúc ingestion
embeddings = OllamaEmbeddings(model="qwen2.5:7b")
vectorstore = Chroma(persist_directory="db/", embedding_function=embeddings)

# Thử hỏi một câu liên quan đến nội dung PDF bạn vừa nạp
query = "Nội dung chính của tài liệu này là gì?"
docs = vectorstore.similarity_search(query, k=2)

print(f"Tìm thấy {len(docs)} đoạn liên quan:")
for i, doc in enumerate(docs):
    print(f"\n--- Đoạn {i+1} ---\n{doc.page_content[:200]}...")