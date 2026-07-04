# DETAILED REPORT: SYSTEM ARCHITECTURE UPGRADE OF AGENTIC RAG TO FULLSTACK WEB
**Project:** Intelligent Research Agent (Agentic RAG)  
**Author:** Project Development Team  
**Date:** June 27, 2026  

---

## 1. Introduction & Problem Statement

The **Agentic RAG (Retrieval-Augmented Generation)** system was originally developed as a Command Line Interface (CLI) application. The Core AI Engine utilizes the **LangGraph** framework to orchestrate the task execution graph, combined with the **Qwen2.5-7B** large language model running locally via **Ollama**, a **ChromaDB** vector database, and the **BGE-M3** embedding model to retrieve domain-specific academic literature. The system also integrates advanced capabilities such as web search (DuckDuckGo Search), expert consult API (Tavily Search), dynamic code execution (Python REPL), diagram generation (Mermaid.js), and automated report export to the cloud (Google Workspace).

However, operating the system via a CLI presents several critical limitations for production deployment:
* **Interface and Experience (UI/UX) Barriers:** The command-line interface is inaccessible to academic researchers and cannot natively render complex formats such as LaTeX formulas or interactive Mermaid flowcharts, forcing users to rely on static intermediate files.
* **Lack of Multi-Session Persistence:** Conversational state only exists in-memory during the CLI process or must be manually saved to flat JSON files, preventing users from tracking, reviewing, or resuming past contexts.
* **No User Authentication:** The system lacks authentication, making it impossible to isolate conversational history or Google Workspace configurations between different users.
* **Absence of Real-Time Feedback:** Since an Agentic RAG run traverses multiple complex nodes (Routing, Retrieving, Grading, Generating, Exporting), execution latency is high. In a CLI, users must wait for the entire process to complete before receiving any output, making the system appear unresponsive.

To address these issues, the project has executed a strategic architectural migration: **upgrading the CLI application to a Fullstack Web Application (Client-Server architecture)**. This report details the migration process, including environment setup, database design, FastAPI backend development, real-time WebSocket communication, and progress milestones.

---

## 2. System Architecture Analysis & Comparison

### 2.1. Proposed Architecture vs. Actual Implementation
The actual implementation adheres to the 3-Tier architecture outlined in `Fullstack_Architecture_Plan.md`, ensuring strict separation of concerns:

```mermaid
graph TD
    subgraph Presentation Layer [Presentation Layer - Frontend]
        NextJS[Next.js App Router] --> React[React Components & Hooks]
        React --> WSClient[WebSocket Client /chat/session_id]
        React --> HttpClient[HTTP Client Axios/Fetch]
    end

    subgraph Business Logic Layer [Business Logic Layer - Backend]
        FastAPI[FastAPI Gateway]
        Auth[JWT Authentication]
        WSHandler[WebSocket Chat Handler]
        LGraph[LangGraph Core Engine]
        
        HttpClient --> Auth
        HttpClient --> FastAPI
        WSClient --> WSHandler
        WSHandler --> LGraph
    end

    subgraph Data Access Layer [Data Access Layer - Database]
        PostgreSQL[(PostgreSQL Port 5433)]
        ChromaDB[(ChromaDB Vector Store)]
        
        FastAPI -->|SQLAlchemy ORM| PostgreSQL
        LGraph -->|Vector Search| ChromaDB
        LGraph -->|Read/Write History| PostgreSQL
    end
    
    subgraph External Services [External Services]
        Tavily[Tavily Search API]
        GWorkspace[Google Workspace Docs/Sheets/Drive]
        Ollama[Ollama Local LLM]
        
        LGraph --> Tavily
        LGraph --> GWorkspace
        LGraph --> Ollama
    end
```

### 2.2. Architectural Comparison: CLI vs. Web Fullstack

| Dimension | CLI System (Legacy) | Fullstack Web System (Current) |
| :--- | :--- | :--- |
| **User Interface** | Terminal (Monochrome Text) | Modern Web UI (Next.js, TailwindCSS) |
| **Authentication & Security** | None (Local execution) | JSON Web Token (JWT) via FastAPI Auth modules |
| **Session Management** | Single-session, context lost on exit | Multi-session persistent storage in PostgreSQL |
| **Communication Protocol** | Synchronous execution on main Python thread | Hybrid: HTTP RESTful (static data) + WebSocket (real-time stream) |
| **Agent Reasoning UX** | User blocks for 30s-2m until final output | Real-time node-by-node thought process streaming |
| **Conversation Storage** | None or raw JSON exports | Structured relational database (PostgreSQL) |

---

## 3. Environment Setup & Database Initialization

### 3.1. Environment Configuration and Docker Compose
To avoid port conflicts with pre-existing PostgreSQL installations on the developer's machine (which default to `5432`), the database is configured to run on port **5433** inside a Docker container.

The environment configuration file `.env` at the root folder contains:
```env
# API Keys for RAG Tools
TAVILY_API_KEY=tvly-********************************

# JWT Settings
SECRET_KEY=supersecretagenticragkey1234567890!
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Database Connection (PostgreSQL on Port 5433)
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/agentic_rag
```

### 3.2. Relational Database Schema
The database uses three primary tables: `users`, `chat_sessions`, and `messages`. The database structure is mapped via SQLAlchemy ORM in [models.py](file:///d:/PHANTHIETTRUNG/SCHOOL_SEMESTER/KLTN/Agentic_rag_final_project/backend/models.py):

#### `users` Table (Identity Management)
* `id` (`UUID` - Primary Key): Auto-generated using UUIDv4 for security.
* `email` (`VARCHAR(255)` - Unique, Indexed): User login credentials.
* `hashed_password` (`VARCHAR(255)`): Stored using bcrypt hashing via the `passlib` package.
* `created_at` (`DateTime`): Timestamp of account registration.

#### `chat_sessions` Table (Session Tracking)
* `id` (`UUID` - Primary Key): Unique session ID. This also serves as the `thread_id` in LangGraph's checkpointer to restore conversational memory.
* `user_id` (`UUID` - Foreign Key): References `users.id` with `ondelete="CASCADE"`.
* `title` (`VARCHAR(255)`): Title of the chat conversation, defaulting to "New Conversation" and auto-updated based on the first query.
* `updated_at` (`DateTime`): Tracks activity timestamps to sort active sessions.

#### `messages` Table (Chat Logs and Metadata)
* `id` (`UUID` - Primary Key): Message identifier.
* `session_id` (`UUID` - Foreign Key): References `chat_sessions.id` with cascade deletion.
* `role` (`VARCHAR(50)`): Sender classification (`user` or `agent`).
* `content` (`Text`): Body text of the prompt or response.
* `export_links` (`JSON`): Stores URLs to exported workspace files (e.g., `{"docs": "https://...", "sheets": "https://..."}`).
* `flags` (`JSON`): Tracks tool configuration triggers (e.g., `{"expert_required": true, "python_repl": false}`).

### 3.3. Automated Table Creation
In the main entrypoint [main.py](file:///d:/PHANTHIETTRUNG/SCHOOL_SEMESTER/KLTN/Agentic_rag_final_project/backend/main.py), tables are automatically checked and initialized in PostgreSQL using:
```python
Base.metadata.create_all(bind=engine)
```
This guarantees plug-and-play setup for new development environments.

---

## 4. Backend API & WebSocket Implementation Details

The backend server is built using **FastAPI** to handle asynchronous connections, supporting standard HTTP endpoints alongside persistent WebSocket channels.

### 4.1. JWT Authentication
User credentials and tokens are managed in [auth.py](file:///d:/PHANTHIETTRUNG/SCHOOL_SEMESTER/KLTN/Agentic_rag_final_project/backend/auth.py):
1. An `OAuth2PasswordBearer` scheme extracts credentials from the HTTP `Authorization` header.
2. Tokens are decoded using the `HS256` algorithm.
3. Access tokens are requested at `/api/auth/login` and validate access to secure resources via the `get_current_user` dependency.

### 4.2. Real-Time WebSocket Chat Endpoint
The interaction between the FastAPI Web Server and the LangGraph runtime occurs over the WebSocket channel `/api/ws/chat/{session_id}` in [chat.py](file:///d:/PHANTHIETTRUNG/SCHOOL_SEMESTER/KLTN/Agentic_rag_final_project/backend/routers/chat.py):

```mermaid
sequenceDiagram
    autonumber
    actor Client as Client (Frontend)
    participant WS as WebSocket Route
    participant DB as PostgreSQL DB
    participant LG as LangGraph Engine
    
    Client->>WS: Connect WebSocket + JWT Token
    WS->>DB: Verify Token & Check Session Ownership
    alt Token Invalid or Session does not belong to User
        WS-->>Client: Close Connection (Code 1008)
    else Valid
        WS-->>Client: Accept Connection
    end
    
    Note over Client, WS: Receive Message Loop
    Client->>WS: Send JSON {"question": "..."}
    WS->>DB: Save User Message to `messages` Table
    WS->>DB: Retrieve Past Messages in Session
    DB-->>WS: Return Message List
    WS->>WS: Reconstruct Chat History into Pairs {"user": ..., "agent": ...}
    
    WS->>WS: Prepare LangGraph Inputs (with chat_history)
    WS-->>Client: Send JSON {"type": "status", "message": "Agent processing started..."}
    
    WS->>LG: Execute astream(inputs, config, stream_mode="updates")
    loop For Each Completed Node in LangGraph
        LG-->>WS: Return Node State Update (e.g. Router, Grader...)
        WS-->>Client: Send JSON {"type": "node_update", "node": node_name, ...}
    end
    LG-->>WS: Return Final State
    
    WS->>DB: Save Agent Message (+ export_links & flags) to DB
    WS->>DB: Update Session Title if First Message
    WS-->>Client: Send JSON {"type": "final_answer", "content": generation, ...}
```

#### Core Real-Time Streaming and State Features:
* **Chat History Reconstruction:** To maintain continuity, the backend retrieves all historical messages from PostgreSQL, sorts them chronologically, and parses them into alternating user-agent pairs:
  ```python
  chat_history = [{"user": "Question 1", "agent": "Answer 1"}, ...]
  ```
  This formatted history is fed into the LangGraph state to preserve session context for downstream query condensation nodes.
* **Node-by-Node Update Streaming:** Instead of blocking via synchronous `ainvoke`, the channel utilizes `agent_app.astream(..., stream_mode="updates")`. As soon as a node completes its task (e.g., the `retrieve` node gathers chunks or the `web_search` node fetches external queries), the backend pushes an immediate progress event to the client. This exposes the Agent's "Thought Process" to the client interface, improving user engagement during longer inference runs.
* **State Accumulator & Double-Run Prevention:** During events stream iteration, the backend accumulates state updates into a local dictionary variable. This captures output parameters (such as the generated report `generation`, file URLs `export_links`, and tool triggers `flags`) without requiring a separate `ainvoke` call, preventing redundant runs and duplicate document exports.

---

## 5. Project Execution Progress and Engineering Milestones

Following the system roadmap for migrating from a command-line utility to a fullstack web service, development has progressed across five main milestones:

### 5.1. Milestone 1: Backend Foundation & Database Design
This stage established the relational storage base to support persistent multi-session workflows:
* **Completed Tasks:**
  * Created the backend directory layout and established the database session factory using SQLAlchemy in `database.py`.
  * Designed schemas in `models.py` for `User`, `ChatSession`, and `Message` tables, including foreign key relationships and index structures.
  * Implemented JWT generation, password hashing via bcrypt, and the JWT token validation dependency in `auth.py`.
  * Exposed HTTP RESTful endpoints for user registration, user login, and session management in `main.py`.

### 5.2. Milestone 2: Real-Time API Integration (WebSocket Channel)
This milestone linked the backend endpoints with the LangGraph execution flow:
* **Completed Tasks:**
  * Created the WebSocket routing endpoint `/api/ws/chat/{session_id}` in `backend/routers/chat.py`.
  * Configured token extraction and verification during the WebSocket handshake.
  * Associated session parameters with the LangGraph thread configuration to utilize the graph checkpointer.
  * Implemented the asynchronous `astream` loop to broadcast active node transitions to the frontend client.
  * Handled the persistence of generated agent responses and metadata flags inside PostgreSQL upon graph completion.

### 5.3. Milestone 3: Long-Term Memory & Conversation Context Restoration
This phase focused on ensuring that the Agent maintains memory across multi-turn sessions:
* **Completed Tasks:**
  * Restored prior conversations from the database to populate the LangGraph conversational inputs.
  * Optimized the Query Condensation node to compile follow-up inputs and chat context into standalone search queries before calling retrieval mechanisms.

### 5.4. Milestone 4: Graph Logic Refinement & Tool Integration Polish
This stage fixed integration bugs encountered when executing RAG tools under a web server context:
* **Completed Tasks:**
  * Corrected state propagation between the `expert_consult` node and the `generate` node, ensuring Tavily search findings are included in the finalized reports.
  * Resolved image embedding bugs in the Google Docs exporter and standardized the Mermaid flowchart parser regex to run reliably in a server process.
  * Sanitized final output generation and completed localization adjustments.

### 5.5. Milestone 5: Technical Documentation & Progress Synchronization
This step completed testing assets and updated technical specifications:
* **Completed Tasks:**
  * Synced progress checklists in `Progress_Tracker.md`, marking Phase 5 (Backend API & WebSocket Integration) and Phase 6 UI Design as fully complete.
  * Documented setup guidelines, project layouts, and testing instructions in `README.md`.
  * Provided a mock client testing script in `test_websocket.py` to verify authentication and streaming logs.

---

## 6. Summary & Future Roadmap

The transition from a CLI tool to a Fullstack Web Application is complete for the backend API and database tiers:
1. **Robust Data Layer:** Relational storage in PostgreSQL secures user sessions and logs conversation history.
2. **Low-Latency Experience:** Node-by-node updates via WebSocket streaming provide interactive feedback.
3. **Standardized Security:** Token-based authentication protects API endpoints and isolates user environments.

### Immediate Action Items:
* **Next.js Frontend Integration (Phase 6 Frontend):** Build login/registration forms, session management sidebars, and the chat console interface. Develop components to render Markdown, LaTeX, and Mermaid flowcharts dynamically from the WebSocket message stream.
* **Automated Evaluation (Phase 4 Evaluation):** Implement the **RAGAS** evaluation script in `evaluate.py` to monitor answer correctness (Faithfulness, Answer Relevance) and retrieval precision (Context Precision).
* **Resource Optimization:** Configure PostgreSQL connection pools and schedule automated cleanup tasks for temporary assets (like compiled Mermaid graphics) in `temp_assets`.

---
*End of Report.*
