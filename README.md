# Agentic RAG Final Project

## Overview
This project implements an advanced **Agentic Retrieval-Augmented Generation (RAG)** system designed to provide highly accurate, context-aware answers by intelligently routing queries across multiple knowledge tiers. 

Currently in **Phase 3 (Agentic Tier)**, the system transitions from a linear RAG pipeline to a dynamic, graph-based agent workflow using **LangGraph**. It employs a "Local First, Global Second" strategy to optimize both latency and response quality.

## Architecture & Tool Layering

The system operates across three distinct knowledge tiers:

1. **Tier 1 (Local Knowledge Base):** 
   - **ChromaDB** storing vectorized academic PDFs categorized into four domains: IT, Math, Physics, and Electronics.
   - Powered by local `nomic-embed-text` embeddings.
2. **Tier 2 (Web Search Fallback):**
   - **DuckDuckGo Search** is triggered automatically if the local database lacks relevant information.
3. **Tier 3 (Expert Consultant):**
   - **Tavily API** is invoked for complex, trend-based, or comparative questions requiring deep research and expert summarization.

### The LangGraph Workflow
- **Router Node:** Classifies the user's intent and domain, deciding whether to route to the Local DB or consult the Expert API immediately.
- **Grader Node (Self-Correction):** Evaluates the retrieved local documents. If the relevance score is low, it intelligently falls back to Web Search.
- **Generator Node:** Synthesizes the final answer using **Qwen2.5 (7b)** via Ollama, strictly adhering to the provided context to prevent hallucinations.

## Project Structure
```text
Agentic_rag_final_project/
├── agent/                  # LangGraph workflow definitions
│   ├── edges.py            # Routing logic and conditional edges
│   ├── graph.py            # StateGraph assembly and compilation
│   ├── nodes.py            # Execution nodes (router, grader, generator)
│   └── state.py            # TypedDict defining the GraphState
├── tools/                  # External API wrappers
│   ├── expert_search.py    # Tavily API integration
│   └── web_search.py       # DuckDuckGo integration
├── data/                   # Raw PDF documents (categorized by domain)
├── db/                     # Persisted ChromaDB vector stores
├── ingestion.py            # Script to chunk and vectorize PDFs
├── local_rag.py            # Core local RAG functions (LLM setup, retrieval)
├── main.py                 # Application entry point
├── requirements.txt        # Project dependencies
└── .env                    # Environment variables (API Keys)
```

## Prerequisites
1. **Python 3.10+**
2. **Ollama** installed and running locally with the following models pulled:
   ```bash
   ollama pull qwen2.5:7b
   ollama pull nomic-embed-text
   ```
3. **Tavily API Key**: Get a free API key from [tavily.com](https://tavily.com/).

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
   Create a `.env` file in the root directory and add your Tavily API Key:
   ```env
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

## Usage

### 1. Data Ingestion (Vectorizing Documents)
Place your PDF files into the respective domain folders inside `data/raw/` (`it`, `math`, `physics`, `electronics`). Then run the ingestion script:
```bash
python ingestion.py
```
This will process the documents and build the local ChromaDB indices.

### 2. Run the Agentic RAG System
Start the main interactive terminal interface:
```bash
python main.py
```
You can now ask questions. The Agent will autonomously decide whether to retrieve local documents, search DuckDuckGo, or consult Tavily.

## License
MIT License
