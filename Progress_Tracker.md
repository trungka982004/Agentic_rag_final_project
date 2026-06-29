# Progress Tracker

Based on the `Implementation_Plan.md` and the actual state of the codebase (updated as of May 15, 2026), below is the checklist of items required to complete the Agentic RAG project. You can use this file to track and check off completed tasks.

## Phase 1: Foundation & Data Ingest
- [x] Configure environment: Python 3.10+, Ollama, ChromaDB on local.
- [x] Ingestion Pipeline: Parse PDFs using PyMuPDF and Unstructured.
- [x] Vector Database: Build domain-specific collections (it, math, physics, electronics) containing 15,495 chunks.
- [x] Embedding: Integrate embedding model (currently using `bge-m3`).
  - [x] *(Optional)* Transition embedding model to `BGE-M3` or `text-embedding-3-small` as planned.

## Phase 2: Agentic Reasoning Workflow
- [x] Construct LangGraph skeleton: router, retrieve, web_search, and generate nodes.
- [x] Node **Router Grader**: Classify the query's domain.
- [x] Self-RAG logic - **Retrieve Grader**: Check the correlation between retrieved documents and the query (`grade_documents_node`).
- [x] Self-RAG logic - **Hallucination Grader**: Evaluate LLM generation against the retrieved context to prevent hallucination.
- [x] Self-RAG logic - **Answer Grader**: Assess if the answer satisfies the user's requirements.
- [x] Update Conditional Edges in `graph.py` to link the Hallucination Grader and Answer Grader.
- [x] **State Management**: Configure Checkpointing/Snapshotting (e.g. `MemorySaver`) during LangGraph compilation to preserve conversation state.

## Phase 3: Tool Integration & Advanced Features (Completed - 2026-05-16)
- [x] **Hybrid Search**: Add BM25 (keyword search) and combine it with existing Vector Search using `EnsembleRetriever`.
- [x] **Python REPL Tool**: Enable the Agent to execute Python code and return structured results for Google Sheets.
- [x] **Google Workspace API Tool**: Support exporting reports to Google Docs/Sheets (including Google Drive API).
- [x] **LaTeX & Mermaid Support**: Render math formulas and automatically compile Mermaid diagram codes into embedded images within reports.
- [x] **Export Streamlining**: Automatically detect export intents and bypass unnecessary chat preamble/filler text.

## Phase 4: Evaluation, Optimization & Polishing
- [ ] Integrate **RAGAS** evaluation framework (Faithfulness, Answer Relevance, Context Precision) in `evaluate.py`.
- [x] **Performance & Latency Optimization**: Implement Fast Keyword-First Routing (saving LLM router calls), Joint Grader (merging 2 Self-RAG graders), Dynamic Retrieval Weights, context chunk deduplication, and Parallel Google Workspace Export (ThreadPoolExecutor).
- [x] **Security & Guardrails**: Configure `recursion_limit` in LangGraph to prevent infinite loops.

## Phase 5: Backend API & WebSocket Integration
- [x] **FastAPI Gateway Setup**: Implement User Authentication (JWT), PostgreSQL database schemas for session, user, and message persistence.
- [x] **WebSocket API**: Stream LangGraph execution events (node updates) in real-time, handling async updates.
- [x] **State Accumulator & Double-run Prevention**: Fix redundant graph execution by implementing event state accumulator and checking for None final state.
- [x] **Database Migration & Docker Setup**: Configure PostgreSQL on port 5433 using Docker Compose for persistence.

## Phase 6: Frontend Development & UI/UX (Completed Design)
- [x] **UI/UX Design**: Build and standardize the frontend interface designs on Stitch, exposing the Agent's Thought Process.
- [x] **Citations & Formatting**: Display source citations precisely and render Markdown, LaTeX, and Mermaid.

---
**Usage Instructions:**
When you complete a feature, change `[ ]` to `[x]` in this file to easily track development progress.
