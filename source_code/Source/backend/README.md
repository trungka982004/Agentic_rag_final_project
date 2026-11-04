# Multi-Domain Agentic RAG — FastAPI Gateway Backend

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy_2.0-D71F00.svg)](https://www.sqlalchemy.org)

The core API gateway and lifecycle orchestrator for the **Multi-Domain Agentic RAG Platform**, built with FastAPI (Asyncio), SQLAlchemy 2.0, and PostgreSQL. It manages user authentication, conversation persistence, and bidirectional WebSocket state streaming with the LangGraph reasoning engine.

---

## 🌟 Key Responsibilities

1. **Authentication & Session Lifecycle:**
   - JWT-based bearer authentication (`/api/auth/login`, `/api/auth/register`).
   - Multi-session management with automatic conversation history retrieval and message persistence.
2. **Chunk-Based WebSocket State Streaming Protocol:**
   - Endpoint: `/api/ws/chat/{session_id}`.
   - Streams asynchronous JSON state frames to the client upon completion of each LangGraph node:
     ```json
     {
       "type": "state_update",
       "node": "router",
       "domain": "Computer Science",
       "intent": "conceptual",
       "timestamp": "2026-11-04T10:00:00Z"
     }
     ```
   - Followed by incremental token chunks during LLM generation:
     ```json
     {
       "type": "token",
       "content": "Attention mechanism..."
     }
     ```
3. **LangGraph Agent Lifecycle Management:**
   - Instantiates and executes compiled `StateGraph` workflows per conversation turn.
   - Manages graceful memory fallback and error recovery.

---

## 📁 Backend Directory Structure

```text
backend/
├── routers/
│   ├── __init__.py
│   ├── auth.py         # Login, registration & JWT token generation endpoints
│   ├── chat.py         # REST & WebSocket conversation endpoints (/api/ws/chat/{session_id})
│   └── sessions.py     # Conversation session CRUD handlers
├── auth.py             # Password hashing (bcrypt) & JWT token validation middleware
├── database.py         # Async/Sync SQLAlchemy database engine & session maker
├── main.py             # FastAPI application entry point, CORS & lifecycle events
├── models.py           # Relational PostgreSQL ORM models (User, Session, Message)
└── schemas.py          # Pydantic v2 schemas for request validation & response formatting
```

---

## 🗄 Relational Database Schema (PostgreSQL)

```mermaid
erDiagram
    User ||--o{ Session : owns
    Session ||--o{ Message : contains
    
    User {
        uuid id PK
        string email UK
        string hashed_password
        datetime created_at
    }
    
    Session {
        uuid id PK
        uuid user_id FK
        string title
        datetime created_at
        datetime updated_at
    }
    
    Message {
        uuid id PK
        uuid session_id FK
        string role
        text content
        jsonb metadata
        datetime created_at
    }
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- Running PostgreSQL database on port 5433 (or configured in `.env`)
- Running Ollama instance with `qwen2.5:7b` and `bge-m3`

### 2. Environment Configuration
Ensure `.env` in the parent directory (`source_code/Source/.env`) contains:
```env
DATABASE_URL=postgresql://postgres:mysecretpassword@localhost:5433/agentic_rag
JWT_SECRET=your_jwt_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=1440
OLLAMA_BASE_URL=http://localhost:11434
TAVILY_API_KEY=your_tavily_key
```

### 3. Launch Gateway
```bash
# From source_code/Source/
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
Interactive Swagger API documentation is available at `http://127.0.0.1:8000/docs`.

