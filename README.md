# Agentic RAG Final Project

## Overview
This project implements an advanced **Agentic Retrieval-Augmented Generation (RAG)** system designed to provide highly accurate, context-aware answers by intelligently routing queries across multiple knowledge tiers. 

Originally built as a CLI application, the system has transitioned to a **Fullstack Architecture** with:
- A **FastAPI Backend Gateway** providing JWT-based User Authentication and Session Management.
- Real-time **WebSocket chat endpoint** (`/api/ws/chat/{session_id}`) streaming LangGraph execution steps (node-by-node updates) directly to clients.
- Persistent storage using **PostgreSQL** (storing users, sessions, and messages).

The system employs a "Local First, Global Second" strategy to optimize both latency and response quality.

## Architecture & Tool Layering

The system operates across three distinct knowledge tiers:

1. **Tier 1 (Local Knowledge Base):** 
   - **ChromaDB** storing vectorized academic PDFs categorized into four domains: IT, Math, Physics, and Electronics.
   - Hybrid Search combining BM25 keyword retrieval and Vector Search using `EnsembleRetriever`.
   - Powered by local `bge-m3` embeddings.
2. **Tier 2 (Web Search Fallback):**
   - **DuckDuckGo Search** is triggered automatically if the local database lacks relevant information.
3. **Tier 3 (Expert Consultant):**
   - **Tavily API** is invoked for complex, trend-based, or comparative questions requiring deep research and expert summarization.

### The LangGraph Workflow
- **Router Node:** Classifies the user's intent and domain, deciding whether to route to the Local DB or consult the Expert API immediately.
- **Grader Node (Self-Correction):** Evaluates the retrieved local documents. If the relevance score is low, it intelligently falls back to Web Search.
- **Generator Node:** Synthesizes the final answer using **Qwen2.5 (7b)** via Ollama, strictly adhering to the provided context to prevent hallucinations.
- **Google Workspace Exporter:** Automatically compiles report text, generates tables, renders Mermaid diagrams to images, uploads them to Google Drive, and exports them to Google Docs & Google Sheets.

## Project Structure
```text
Agentic_rag_final_project/
├── agent/                  # LangGraph workflow definitions
│   ├── edges.py            # Routing logic and conditional edges
│   ├── graph.py            # StateGraph assembly and compilation
│   ├── nodes.py            # Execution nodes (router, grader, generator)
│   └── state.py            # TypedDict defining the GraphState
├── backend/                # FastAPI Fullstack Backend
│   ├── routers/            # API Route handlers
│   │   ├── __init__.py
│   │   └── chat.py         # WebSocket Chat Handler (LangGraph integration)
│   ├── auth.py             # JWT token handling & User authentication
│   ├── database.py         # SQLAlchemy connection & DB engine
│   ├── main.py             # FastAPI entrypoint (app configuration)
│   ├── models.py           # SQLAlchemy persistent models (User, Session, Message)
│   └── schemas.py          # Pydantic data schemas
├── tools/                  # External API wrappers (expert search, web search, formatting)
├── db/                     # Persisted ChromaDB vector stores
├── evaluate.py             # Pipeline evaluator script
├── ingestion.py            # PDF vectorization script
├── local_rag.py            # Core local RAG functions (LLM setup, retrieval)
├── main.py                 # CLI entry point
├── test_websocket.py       # WebSocket client integration test script
├── requirements.txt        # Project dependencies
└── .env                    # Environment variables (API Keys & DB config)
```

## Prerequisites
1. **Python 3.10+**
2. **Ollama** installed and running locally with the following models pulled:
   ```bash
   ollama pull qwen2.5:7b
   ollama pull bge-m3
   ```
3. **Tavily API Key**: Get a free API key from [tavily.com](https://tavily.com/).
4. **PostgreSQL**: Set up PostgreSQL running on port **5433** (e.g. via Docker Compose).
5. **Google Workspace API Credentials**: Setup a Google Cloud Project with Google Docs, Sheets, and Drive APIs enabled. Place `credentials.json` in the root folder.

## Installation & Setup

1. **Clone the repository and navigate to the folder:**
   ```bash
   git clone <repository_url>
   cd Agentic_rag_final_project
   ```

2. **Set up a virtual environment and activate it:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Create a `.env` file in the root directory and add the following settings:
   ```env
   # API Keys
   TAVILY_API_KEY=your_tavily_api_key_here
   
   # JWT Configuration
   SECRET_KEY=your_jwt_secret_key_here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=1440
   
   # Database Configuration (PostgreSQL on port 5433)
   DATABASE_URL=postgresql://postgres:postgres@localhost:5433/agentic_rag
   ```

5. **Start PostgreSQL:**
   Ensure PostgreSQL is running and accessible at the connection string specified above.

## Usage

### 1. Data Ingestion (Vectorizing Documents)
Place your PDF files into the respective domain folders inside `data/raw/` (`it`, `math`, `physics`, `electronics`). Then run the ingestion script:
```bash
python ingestion.py
```
This will process the documents and build the local ChromaDB indices.

### 2. Run in CLI Mode
Start the interactive terminal interface:
```bash
python main.py
```

### 3. Run the Backend API Server
Start the FastAPI server via Uvicorn:
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
The documentation is available at `http://127.0.0.1:8000/docs`.

### 4. Test WebSockets Chat
Verify authentication and real-time streaming using the integrated test script:
```bash
python test_websocket.py
```

## License
MIT License
