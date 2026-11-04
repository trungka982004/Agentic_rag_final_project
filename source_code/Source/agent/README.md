# LangGraph AI Agent Orchestration Engine

[![LangGraph](https://img.shields.io/badge/Orchestrator-LangGraph-FF6F00.svg)](https://github.com/langchain-ai/langgraph)
[![Ollama](https://img.shields.io/badge/Local_Inference-Ollama-8A2BE2.svg)](https://ollama.ai)
[![ChromaDB](https://img.shields.io/badge/Vector_Store-ChromaDB-FC521F.svg)](https://www.trychroma.com)

The cognitive reasoning core of the **Multi-Domain Agentic RAG Platform**, formulated as a directed state graph $\mathcal{G} = (\mathcal{V}, \mathcal{E}, \mathcal{S})$ on LangGraph. It manages dynamic intent routing, hybrid vector/keyword retrieval across 8 isolated domains, two-phase self-corrective verification, and local LLM answer generation.

---

## 🌟 Architectural Workflow

```mermaid
flowchart TD
    Start([User Query q]) --> Router["N_router: Intent Classification & Domain Mapping"]
    
    Router -->|Intent ∈ {Comparison, Trend}| Expert["N_expert: Tavily Research API"]
    Router -->|Factoid / Conceptual| Local["N_local: Hybrid Search (bge-m3 + BM25)"]
    
    Local --> Grader{"N_grader: Token Overlap Check<br>(τ_overlap ≥ 0.25)"}
    
    Grader -->|Pass: S_rel = 1| Gen["N_generator: Local Qwen2.5 7B"]
    Grader -->|Fail: S_rel = 0 & r < 2| Web["N_web: DuckDuckGo Fallback"]
    
    Web --> Gen
    Expert --> Gen
    
    Gen --> End([Token Streaming & Output A])
```

---

## 📁 Agent Directory Structure

```text
agent/
├── state.py    # GraphState TypedDict defining the global context tuple
├── nodes.py    # Execution nodes implementing logic for each step
├── edges.py    # Conditional routing policy functions (δ_router, δ_grader)
└── graph.py    # StateGraph assembly, conditional edge binding & compilation
```

---

## ⚙️ Component Details

### 1. Global Graph State (`state.py`)
Tracks the execution variables through the reasoning lifecycle:
```python
class GraphState(TypedDict):
    query: str                      # Normalized query string
    orig_query: str                 # Raw user prompt
    domain: Optional[str]           # Classified academic domain (1 of 8)
    target_doc: Optional[str]       # Explicit target document constraint
    retrieved_docs: List[Document]  # Retrieved chunk set (BM25 + bge-m3)
    relevance_score: int            # Binary verification status (0 or 1)
    generation: str                 # Synthesized answer
    loop_count: int                 # Remediation loop counter (r <= 2)
    web_fallback: bool              # Tier 2 activation flag
    expert_fallback: bool           # Tier 3 activation flag
```

### 2. Execution Nodes (`nodes.py`)
* **`router_node`:** Identifies domain category and intent using keyword fast-paths and zero-shot Pydantic classification.
* **`local_hybrid_retriever_node`:** Queries the active domain's isolated ChromaDB store using intent-weighted BM25 + dense $bge\text{-}m3$ fusion.
* **`grader_node`:** Computes Phase 1 lexical keyword overlap on the top-1 ranked chunk. If overlap $\ge 0.25$, proceeds directly to generator; otherwise flags for fallback.
* **`web_fallback_node`:** Engages DuckDuckGo for missing context with zero API cost.
* **`expert_node`:** Queries Tavily API for multi-source comparative inquiries.
* **`generator_node`:** Synthesizes the grounded answer using local Qwen2.5 7B ($T=0.0$, context 3,072) with strict citation anchoring.

### 3. Conditional Edges (`edges.py`)
* **`route_query`:** Implements $\delta_{\text{router}}(q)$, branching to `N_expert` or `N_local`.
* **`decide_to_generate`:** Implements $\delta_{\text{grader}}(\mathcal{D}_{\text{ret}}, q)$, branching to `N_generator` or `N_web`. Enforces the loop ceiling $r \le 2$ to guarantee deterministic runtime termination.

### 4. Graph Assembly (`graph.py`)
Compiles the workflow into an executable `CompiledGraph`:
```python
from langgraph.graph import StateGraph, END
from agent.state import GraphState
from agent.nodes import router_node, local_hybrid_retriever_node, grader_node, web_fallback_node, expert_node, generator_node
from agent.edges import route_query, decide_to_generate

workflow = StateGraph(GraphState)
# Add Nodes
workflow.add_node("router", router_node)
workflow.add_node("local_retriever", local_hybrid_retriever_node)
workflow.add_node("grader", grader_node)
workflow.add_node("web_search", web_fallback_node)
workflow.add_node("expert_search", expert_node)
workflow.add_node("generator", generator_node)

# Set Entry & Conditional Edges
workflow.set_entry_point("router")
workflow.add_conditional_edges("router", route_query)
workflow.add_edge("local_retriever", "grader")
workflow.add_conditional_edges("grader", decide_to_generate)
workflow.add_edge("web_search", "generator")
workflow.add_edge("expert_search", "generator")
workflow.add_edge("generator", END)

app = workflow.compile()
```

