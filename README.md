# Agentic RAG Project

This project implements a basic Agentic RAG (Retrieval-Augmented Generation) system using LangChain, Ollama, and ChromaDB to process and query PDF documents.

## 🚀 Features
- Automated PDF document loading and processing.
- Intelligent text chunking using `RecursiveCharacterTextSplitter`.
- Local Vector Embedding storage using ChromaDB.
- Semantic similarity search powered by LLM models via Ollama.

## 📋 Prerequisites
Before you begin, ensure you have the following installed:
- [Python 3.9+](https://www.python.org/downloads/)
- [Ollama](https://ollama.com/)
- The `qwen2.5:7b` model in Ollama (or update the model identifier in the code).

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd Agentic_rag_final_project
   ```

2. **Create a Virtual Environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment:**
   - **Windows:**
     ```bash
     .\venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Install Required Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Pull the LLM Model (Ollama):**
   ```bash
   ollama pull qwen2.5:7b
   ```

## 📖 Usage Guide

### 1. Data Ingestion
- Place your PDF files into the `data/` directory.
- Run the ingestion script to process documents and create the vector database:
  ```bash
  python ingestion.py
  ```

### 2. Testing the Database
- After ingestion is complete, you can test the retrieval system:
  ```bash
  python test_db.py
  ```

## 📂 Project Structure
- `data/`: Input directory for PDF documents.
- `db/`: Local storage directory for the ChromaDB vector store.
- `ingestion.py`: Script for document processing and embedding.
- `test_db.py`: Script for testing semantic search queries.
- `main.py`: Entry point for the application (under development).
- `requirements.txt`: List of required Python packages.

## 📝 Troubleshooting & Notes
- **Ollama Engine:** Ensure the Ollama application is running before executing ingestion or search scripts.
- **Model Configuration:** If you wish to use a different model, update the `model` parameter in both `ingestion.py` and `test_db.py`.
- **Directory Creation:** The script automatically creates `data/` and `db/` folders if they do not exist.
