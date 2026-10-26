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

### 1. Backend Setup

1. **Clone the repository and navigate to the folder:**
   ```bash
   git clone <repository_url>
   cd Agentic_rag_final_project
   ```

2. **Start the PostgreSQL Database:**
   Start the PostgreSQL container running on port `5433` using Docker Compose:
   ```bash
   docker compose up -d
   ```

3. **Set up a virtual environment and activate it:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

4. **Install Backend dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure Backend Environment Variables:**
   Copy `.env.example` to `.env` or create a new `.env` file in the root directory:
   ```env
   # API Keys
   TAVILY_API_KEY=your_tavily_api_key_here
   
   # JWT Configuration
   JWT_SECRET=your_jwt_secret_key_here
   ACCESS_TOKEN_EXPIRE_MINUTES=1440
   
   # Database Configuration (PostgreSQL on port 5433)
   DATABASE_URL=postgresql://postgres:mysecretpassword@localhost:5433/agentic_rag
   ```

### 2. Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Frontend dependencies:**
   ```bash
   npm install
   ```

3. **Configure Frontend Environment Variables:**
   Copy `.env.local.example` to `.env.local`:
   ```bash
   cp .env.local.example .env.local
   ```
   Ensure `NEXT_PUBLIC_API_URL` points to your backend URL:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

---

## Usage & Execution

### 1. Data Ingestion (Vectorizing Documents)
Place your PDF files into the respective domain folders inside `data/raw/` (`it`, `math`, `physics`, `electronics`). Run the ingestion script:
```bash
python ingestion.py
```
This will process the documents and build the local ChromaDB indices.

### 2. Start the Backend API Server
With your virtual environment active, start the FastAPI server via Uvicorn:
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
* The API docs will be available at `http://127.0.0.1:8000/docs`.

### 3. Start the Frontend Application
Navigate to the `frontend` directory and start the Next.js development server:
```bash
cd frontend
npm run dev
```
* Access the web application at `http://localhost:3000`.

#### Default Test Accounts
Use the pre-configured test credentials below to instantly log in and test the system:

| Email | Password | Role / Description | Historical Context |
| :--- | :--- | :--- | :---: |
| **`test@example.com`** | `password` | **Primary Researcher Account** (Recommended) | 4 sessions (11 messages) |
| **`test1@example.com`** | `pass123_1` | **Secondary Benchmark & WebSocket Tester** | 3 sessions (6 messages) |

### 4. Running in CLI Mode (Optional)
If you wish to use the interactive terminal interface:
```bash
python main.py
```

### 5. Test WebSockets Connection (Optional)
Verify authentication and real-time streaming using the integrated test script:
```bash
python test_websocket.py
```

## License
MIT License
