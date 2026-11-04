# Tiered Self-Corrective Multi-Domain Agentic RAG Platform

<p align="center">
  <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License: Apache-2.0"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white" alt="Python 3.10+"></a>
  <a href="https://fastapi.tiangolo.com"><img src="https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white" alt="FastAPI"></a>
  <a href="https://github.com/langchain-ai/langgraph"><img src="https://img.shields.io/badge/Orchestrator-LangGraph-FF6F00.svg" alt="LangGraph"></a>
  <a href="https://nextjs.org"><img src="https://img.shields.io/badge/Next.js-14.2-black.svg?logo=next.dot.js&logoColor=white" alt="Next.js 14"></a>
  <a href="https://ollama.ai"><img src="https://img.shields.io/badge/Local_LLM-Qwen2.5_7B-8A2BE2.svg" alt="Ollama Qwen2.5"></a>
  <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/Deploy-1--Click_Docker-2496ED.svg?logo=docker&logoColor=white" alt="Docker"></a>
</p>

<p align="center">
  <strong>An end-to-end, open-source Multi-Domain Agentic Retrieval-Augmented Generation (RAG) Platform engineered specifically for academic and scientific inquiry.</strong>
</p>

<p align="center">
  <img src="science_paper_assets/science_paper_images/fig5_ui_walkthrough.png" alt="Multi-Domain Agentic RAG Platform Interactive UI Walkthrough" width="96%" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);" />
</p>

Operating under a **"Local-First, Multi-Tiered Fallback"** philosophy, the system formalizes retrieval and reasoning as a stateful directed graph $\mathcal{G} = (\mathcal{V}, \mathcal{E}, \mathcal{S})$ orchestrated via **LangGraph**, coupling intent-aware adaptive hybrid search ($bge\text{-}m3$ + BM25) with a resource-efficient Two-Phase Verification mechanism, node-by-node WebSocket chunk streaming, and 100% local inference privacy.

---

## 📑 Table of Contents
- [Key Architectural Highlights](#-key-architectural-highlights)
- [Multi-Tier Documentation Architecture](#-multi-tier-documentation-architecture)
- [System Architecture](#-system-architecture)
- [Repository Structure](#-repository-structure)
- [Scientific Papers & Preprints](#-scientific-papers--preprints)
- [Quantitative Benchmark & SOTA Baselines](#-quantitative-benchmark--sota-baselines)
- [Feature Comparison with Open-Source Platforms](#-feature-comparison-with-open-source-platforms)
- [Quick Start Guide (1-Click Docker)](#-quick-start-guide-1-click-docker)
- [Manual Development Setup](#-manual-development-setup)
- [Evaluation & Benchmarking](#-evaluation--benchmarking)
- [Citation](#-citation)
- [License](#-license)

---

## 🗺 Multi-Tier Documentation Architecture

This repository adopts a modular, distributed documentation architecture with specialized documentation for each functional area:

| Functional Area | Documentation Path | Description |
| :--- | :--- | :--- |
| **Research Overview** | [`science_paper_assets/README.md`](science_paper_assets/README.md) | Manuscripts, LaTeX source, Overleaf packaging & BibTeX. |
| **Methodology** | [`science_paper_assets/methodology/README.md`](science_paper_assets/methodology/README.md) | State graph $\mathcal{G} = (\mathcal{V}, \mathcal{E}, \mathcal{S})$, routing policies & algorithms. |
| **Experiments** | [`science_paper_assets/experiments/README.md`](science_paper_assets/experiments/README.md) | Benchmark setup, 5 SOTA baselines, $t$-tests & ablation studies. |
| **Application Overview** | [`source_code/Source/README.md`](source_code/Source/README.md) | Fullstack architecture, Docker Compose & configuration. |
| **Frontend Web Client** | [`source_code/Source/frontend/README.md`](source_code/Source/frontend/README.md) | Next.js 14, Tailwind, WebSocket streaming & KaTeX math rendering. |
| **Backend Gateway** | [`source_code/Source/backend/README.md`](source_code/Source/backend/README.md) | FastAPI, JWT authentication, PostgreSQL schemas & WebSocket protocol. |
| **AI Agent Orchestrator** | [`source_code/Source/agent/README.md`](source_code/Source/agent/README.md) | LangGraph nodes, edges, state transitions & local Ollama inference. |
| **Project Roadmaps & Reports** | [`docs/README.md`](docs/README.md) | Strategic roadmaps, software plans & formal advisor reports. |

---

## 🌟 Key Architectural Highlights

1. **Domain-Isolated Multi-Store Topology:**
   - Rather than pooling documents into a single flat collection, the knowledge base partitions **618 scientific publications into 8 isolated ChromaDB collections** (144,318 text chunks across Computer Science, Electronics, Mathematics, Physics, Agriculture, Economics, Law, Medicine).
   - Eliminates cross-disciplinary semantic collision and increases Context Precision to **0.56 (+14.3% over CRAG)**.
2. **Intent-Aware Adaptive Hybrid Retrieval:**
   - Combines multilingual dense representations ($bge\text{-}m3$, 1024-d) with sparse lexical BM25 using dynamic weighting based on query intent (Conceptual vs. Factoid).
3. **Resource-Efficient Two-Phase Verification:**
   - **Phase 1 (Fast Lexical Token Overlap Filter):** Rapidly prunes context noise ($\tau_{\text{overlap}} \ge 0.25$, latency $< 0.01$s).
   - **Phase 2 (Post-Generation Joint Grader):** Structured JSON schema validation preventing hallucination without heavy GPU overhead.
   - Slashes marginal API costs to **$0.90 / 1,000 queries** (saving **71.9%** vs. CRAG at $3.20 and **50.0%** vs. Self-RAG at $1.80).
4. **Local-First Privacy & Zero Cloud Data Leak:**
   - Default inference engine runs **Qwen2.5 7B** locally via Ollama with automatic GPU/CPU memory fallback. Ideal for proprietary laboratory research and pre-publication manuscripts.
5. **Node-by-Node WebSocket Telemetry:**
   - Fullstack asynchronous WebSocket protocol (`/api/ws/chat/{session_id}`) pushing live agent milestones (`[Router]` $\rightarrow$ `[Hybrid Search]` $\rightarrow$ `[Grader]` $\rightarrow$ `[Generator]`) and incremental Markdown/LaTeX formula rendering in real time.

---

## 🏛 System Architecture

The platform operates across three hierarchical tiers:
* **Tier 1 (Local Vector Store $K_{\text{local}}$):** 8 isolated ChromaDB domain collections with hybrid BM25 + $bge\text{-}m3$ retrieval.
* **Tier 2 (Automated Web Fallback $K_{\text{web}}$):** Automatic context remediation via DuckDuckGo with zero API licensing cost.
* **Tier 3 (Expert Synthesis API $K_{\text{expert}}$):** Precision routing to Tavily API for complex cross-paper comparisons and contemporary trends.

<p align="center">
  <img src="science_paper_assets/science_paper_images/fig1_architecture.png" alt="System Architecture Diagram" width="90%" />
</p>

### LangGraph Agent State Machine

The reasoning process executes on a state graph $\mathcal{G} = (\mathcal{V}, \mathcal{E}, \mathcal{S})$ governing discrete transition policies $\delta_{\text{router}}$ and $\delta_{\text{grader}}$:

<p align="center">
  <img src="science_paper_assets/science_paper_images/fig2_state_graph.png" alt="LangGraph State Transition Graph" width="70%" />
</p>

```mermaid
flowchart TD
    User["Client UI (Next.js 14)"] -->|WebSocket /api/ws/chat| Gateway["FastAPI Gateway"]
    Gateway --> Orchestrator["LangGraph Orchestrator"]
    
    subgraph Routing ["Agent State Graph"]
        Orchestrator --> Router{"Router Policy δ_router"}
        Router -->|Factoid / Conceptual| Tier1["Tier 1: Local Hybrid Search<br>(bge-m3 + BM25)"]
        Router -->|Comparative / Trends| Tier3["Tier 3: Expert API<br>(Tavily Search)"]
        
        Tier1 --> Grader{"Two-Phase Grader δ_grader<br>(Token Overlap ≥ 0.25)"}
        Grader -->|Pass S_rel = 1| Gen["Generator Node<br>(Local Qwen2.5 7B)"]
        Grader -->|Fail S_rel = 0| Tier2["Tier 2: Web Search Fallback<br>(DuckDuckGo)"]
        Tier2 --> Gen
        Tier3 --> Gen
    end
    
    Gen -->|Token & Math Stream| User
    Gen -->|Optional Export| Export["Google Docs / Sheets Export"]
```

---

## 📁 Repository Structure

```text
Agentic_rag_final_project/
├── docs/                       # Action plans, upgrade roadmaps & advisor reports
│   └── paper_roadmap/          # Dual-paper roadmap & technical reports
├── overleaf_packages/          # Pre-packaged Overleaf zip projects (0 compile errors)
│   ├── overleaf_project_en.zip               # Paper 1 Overleaf Package
│   └── overleaf_project_system_paper_en.zip  # Paper 2 Overleaf Package
├── science_paper_assets/       # Academic paper manuscripts, LaTeX templates & assets
│   ├── main_en.tex             # Paper 1: Core Research Paper (IEEE Conference)
│   ├── system_paper_en.tex     # Paper 2: Open-Source System Demo Paper (IEEE Track)
│   ├── references.bib          # Standardized BibTeX citations (19 entries)
│   ├── science_paper_images/   # High-resolution 300 DPI vector diagrams & screenshots
│   └── scripts/                # Verification, packaging & plotting scripts
├── source_code/
│   └── Source/                 # Core implementation source code
│       ├── agent/              # LangGraph workflow (state, nodes, edges, graph)
│       ├── backend/            # FastAPI gateway, JWT auth, WebSocket handlers, DB models
│       ├── frontend/           # Next.js 14 client UI, TailwindCSS, WebSocket hooks
│       ├── tools/              # External APIs (Tavily, DuckDuckGo, Google Workspace)
│       ├── db/                 # ChromaDB vector index stores
│       ├── data/raw/           # Raw PDF literature partitioned across 8 domains
│       ├── docker-compose.yml  # 1-Click Multi-Service Orchestration
│       ├── Dockerfile          # Backend container specification
│       ├── evaluate.py         # Automated RAGAS benchmark evaluation suite
│       ├── ingestion.py        # PDF extraction, bge-m3 embedding & BM25 indexing
│       └── requirements.txt    # Python backend dependencies
├── LICENSE                     # Apache License Version 2.0
└── README.md                   # Project documentation
```

---

## 📄 Scientific Papers & Preprints

This repository hosts the source code and reproduction materials for two peer-reviewed academic manuscripts:

| Manuscript | Type | Venue / Format | Source Files | Description |
| :--- | :---: | :---: | :---: | :--- |
| **Tiered Self-Corrective Agentic RAG: Dynamic Knowledge Routing with Multi-Domain Hybrid Retrieval** | Research Paper | IEEE Conference (6 pages) | [`science_paper_assets/main_en.tex`](science_paper_assets/main_en.tex) | Mathematical formalization of $\mathcal{G} = (\mathcal{V}, \mathcal{E}, \mathcal{S})$, two-phase context verification, and quantitative evaluation against 5 SOTA baselines. |
| **An Open-Source Multi-Domain Agentic RAG Platform with Tiered Knowledge Routing and Real-Time State Synchronization** | System Demo | IEEE System Demo Track (4 pages) | [`science_paper_assets/system_paper_en.tex`](science_paper_assets/system_paper_en.tex) | Production system architecture, real-time WebSocket state streaming protocol, technical feature matrix, and Docker reproducibility. |

---

## 📊 Quantitative Benchmark & SOTA Baselines

Evaluated on a standardized benchmark of **150 multi-domain academic queries** across 4 STEM disciplines (Computer Science: 38, Physics: 38, Mathematics: 37, Electronics: 37) with **Fleiss' Kappa $\kappa = 0.81$** inter-annotator agreement.

All baselines share the identical local foundation model (**Qwen2.5 7B**) as their primary answer generator:

| Architecture / Baseline Model | Relevance | Faithfulness | Context Precision | Context Recall | First-Token (s) | End-to-End (s) | Marginal Cost ($/1k) | Domain Isolated |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Naive RAG** *(Lewis et al., 2020)* | 0.58 $\pm$ 0.04 | 0.49 $\pm$ 0.05 | 0.44 $\pm$ 0.05 | 0.43 $\pm$ 0.05 | **1.12 $\pm$ 0.15** | **1.85 $\pm$ 0.20** | **$0.00** | No |
| **Advanced RAG** *(Gao et al., 2023)* | 0.62 $\pm$ 0.03 | 0.51 $\pm$ 0.04 | 0.46 $\pm$ 0.04 | 0.45 $\pm$ 0.04 | 1.45 $\pm$ 0.18 | 2.30 $\pm$ 0.25 | **$0.00** | No |
| **Adaptive-RAG** *(Jeong et al., 2024)* | 0.66 $\pm$ 0.04 | 0.53 $\pm$ 0.04 | 0.47 $\pm$ 0.04 | 0.48 $\pm$ 0.04 | 2.15 $\pm$ 0.25 | 3.20 $\pm$ 0.35 | $1.50 | No |
| **Corrective RAG (CRAG)** *(Yan et al., 2024)* | 0.67 $\pm$ 0.03 | 0.54 $\pm$ 0.04 | 0.48 $\pm$ 0.04 | 0.51 $\pm$ 0.04 | 3.80 $\pm$ 0.35 | 4.85 $\pm$ 0.45 | $3.20 | No |
| **Self-RAG** *(Asai et al., 2024)* | 0.68 $\pm$ 0.03 | 0.58 $\pm$ 0.04 | 0.49 $\pm$ 0.04 | 0.49 $\pm$ 0.04 | 4.20 $\pm$ 0.40 | 5.45 $\pm$ 0.50 | $1.80 | No |
| **Proposed Agentic RAG (Ours)** | **0.73 $\pm$ 0.03** | **0.62 $\pm$ 0.04** | **0.56 $\pm$ 0.04** | **0.54 $\pm$ 0.04** | 1.85 $\pm$ 0.25 | 3.65 $\pm$ 0.40 | **$0.90** | **Yes (8 Stores)** |

*Statistical Significance:* Paired Student's $t$-test ($df=149$) confirms statistically significant gains over CRAG ($t=3.82, p < 0.001$ on Relevance; $t=3.95, p < 0.001$ on Faithfulness) and Self-RAG ($t=3.61, p < 0.001$ on Relevance; $t=2.48, p = 0.014$ on Faithfulness).

### Pareto Frontier Trade-Off Analysis

<p align="center">
  <img src="science_paper_assets/science_paper_images/fig4_pareto_chart.png" alt="Empirical Pareto Frontier: Faithfulness vs Marginal Cost" width="75%" />
</p>

The empirical non-dominated Pareto frontier is formed by Advanced RAG ($0.00, 0.51 Faithfulness) and the Proposed Agentic RAG ($0.90, 0.62 Faithfulness). All other multi-turn agentic baselines (CRAG and Self-RAG) are strictly dominated.

---

## 🔍 Feature Comparison with Open-Source Platforms

| Technical Criterion | **Proposed System** | **Dify** | **RAGFlow** | **FastGPT** | **Khoj** |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Target Application** | **Academic & Scientific Research** | General SaaS / Enterprise | Document OCR Workflow | Customer FAQ / Bots | Personal AI Assistant |
| **Knowledge Architecture** | **8 Isolated Specialized Stores** | Shared Flat Collections | Dataset Folder Hierarchies | Flat Knowledge Base | Flat Local Files |
| **Retrieval Strategy** | **Dynamic Intent Hybrid (bge-m3+BM25)** | Keyword / Vector Search | DeepDoc Parser + Dense | Vector Search + Reranker | Dense Vector Search |
| **Self-Correction** | **Two-Phase Token Grader + Fallback** | Manual Workflow Configuration | Reranker Score Threshold | Static Keyword Filter | None |
| **Local LLM Privacy** | **Native Ollama (Zero Cloud Leak)** | Cloud-First Architecture | High Local GPU Demands | Cloud-First Architecture | Local Desktop App |
| **Streaming Telemetry** | **Chunk WebSocket (Node-by-node)** | Workflow Execution Event Logs | Intermediate Step Logs | Chat Token Stream Only | Token Stream |
| **Tool Execution** | **Python REPL + Google Workspace** | Webhooks & Custom Plugins | Limited Document Parsers | HTTP Call Nodes | Custom Plugins |
| **Deployment Footprint** | **1-Click Docker (3 services, <2.1GB)** | Multi-container (8+ services) | Heavy Multi-container | Medium Multi-container | Single Binary / Desktop |
| **Open-Source License** | **Apache-2.0** | Apache-2.0 | Apache-2.0 | Apache-2.0 | GPL-3.0 |

---

## 🚀 Quick Start Guide (1-Click Docker)

The easiest way to launch the fullstack platform (PostgreSQL, FastAPI, and Next.js) is via Docker Compose:

### 1. Prerequisites
- [Docker](https://docs.docker.com/get-docker/) & Docker Compose v2+
- [Ollama](https://ollama.ai) running on the host machine:
  ```bash
  ollama pull qwen2.5:7b
  ollama pull bge-m3
  ```

### 2. Launch Stack
```bash
# Clone the repository
git clone https://github.com/trungka982004/Agentic_rag_final_project.git
cd Agentic_rag_final_project/source_code/Source

# Start all microservices in background
docker compose up -d
```

### 3. Service Endpoints
- **Web Client UI:** `http://localhost:3000`
- **FastAPI OpenAPI Docs:** `http://localhost:8000/docs`
- **PostgreSQL Database:** `localhost:5433` (Database: `agentic_rag`)

---

## 🛠 Manual Development Setup

If you prefer to run services individually for local development:

### 1. Backend Environment Setup
```bash
cd source_code/Source

# Create virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL service via Docker
docker compose up -d postgres

# Configure environment variables
cp .env.example .env
```

Ensure `.env` contains:
```env
TAVILY_API_KEY=your_tavily_key
JWT_SECRET=your_secret_key_here
DATABASE_URL=postgresql://postgres:mysecretpassword@localhost:5433/agentic_rag
OLLAMA_BASE_URL=http://localhost:11434
```

Start the FastAPI gateway:
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Frontend Setup
```bash
cd source_code/Source/frontend

# Install node dependencies
npm install

# Start Next.js development server
npm run dev
```
Open `http://localhost:3000` in your browser.

#### Pre-Configured Test Accounts:
| Email | Password | Role / Purpose |
| :--- | :--- | :--- |
| **`test@example.com`** | `password` | Primary Researcher Account (Preloaded sample sessions) |
| **`test1@example.com`** | `pass123_1` | Benchmark & WebSocket Integration Testing |

---

## 📈 Evaluation & Benchmarking

To reproduce the benchmark results on the 150 STEM test cases:
```bash
cd source_code/Source
python evaluate.py
```
To resume a benchmark run:
```bash
python evaluate.py --resume
```
Results and metrics are incrementally persisted to `evaluation_results.json` and `evaluation_results.csv`.

---

## 📖 Citation

If you find this work, codebase, or benchmark useful in your research, please cite our papers:

```bibtex
@inproceedings{phan2024tiered,
  author    = {Phan, Thiet Trung and Vu, Dinh Hong},
  title     = {Tiered Self-Corrective Agentic {RAG}: Dynamic Knowledge Routing with Multi-Domain Hybrid Retrieval},
  booktitle = {Proceedings of the IEEE Conference},
  year      = {2024}
}

@inproceedings{phan2024opensource,
  author    = {Phan, Thiet Trung and Vu, Dinh Hong},
  title     = {An Open-Source Multi-Domain Agentic {RAG} Platform with Tiered Knowledge Routing and Real-Time State Synchronization},
  booktitle = {Proceedings of the IEEE Conference (System Demonstration Track)},
  year      = {2024}
}
```

---

## 📜 License

This project is licensed under the **Apache License 2.0** — see the [LICENSE](LICENSE) file for details.
