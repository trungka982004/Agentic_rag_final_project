# Methodology & Formal Algorithmic Formulations

This document provides the formal mathematical framework, state transition policies, and algorithms of the **Tiered Self-Corrective Agentic RAG Architecture** implemented in the research paper.

---

## 1. Global State Space & Graph Formalization

The workflow is modeled as a directed state machine $\mathcal{G} = (\mathcal{V}, \mathcal{E}, \mathcal{S})$ orchestrated via LangGraph:

### 1.1 Global State Space $\mathcal{S}$
At discrete execution step $t$, the state is defined as a tuple:
$$\mathbf{s}_t = \langle q, q_{\text{orig}}, d, d_{\text{target}}, \mathcal{D}_{\text{ret}}, S_{\text{rel}}, A, r, f_{\text{web}}, f_{\text{expert}} \rangle$$

* $q \in \Sigma^*$: Normalized query string.
* $q_{\text{orig}} \in \Sigma^*$: Original user prompt.
* $d \in \{1, \dots, 8\} \cup \{\emptyset\}$: Active academic knowledge domain.
* $d_{\text{target}} \in \Sigma^* \cup \{\emptyset\}$: Explicit target document identifier constraint.
* $\mathcal{D}_{\text{ret}} = \{c_1, c_2, \dots, c_k\}$: Retrieved context passage set.
* $S_{\text{rel}} \in \{0, 1\}$: Binary relevance verification score.
* $A \in \Sigma^*$: Synthesized text output.
* $r \in \mathbb{N}_{\le 2}$: Remediation loop counter (maximum 2 passes).
* $f_{\text{web}}, f_{\text{expert}} \in \{0, 1\}$: Fallback routing telemetry flags.

### 1.2 Node Set $\mathcal{V}$
$$\mathcal{V} = \{N_{\text{router}}, N_{\text{local}}, N_{\text{grader}}, N_{\text{web}}, N_{\text{expert}}, N_{\text{generator}}\}$$

---

## 2. Dynamic Routing Policies

### 2.1 Intent Routing Policy $\delta_{\text{router}}(q)$
The entry routing policy directs queries either to the local hybrid multi-domain engine or immediately to the expert synthesis API:

$$\delta_{\text{router}}(q) = \begin{cases} N_{\text{expert}}, & \text{if } \text{Intent}(q) \in \{\text{Comparison}, \text{Trend}\} \\ N_{\text{local}}, & \text{otherwise} \end{cases}$$

$\text{Intent}(q)$ combines a heuristic keyword fast-path ($< 0.005$s) with zero-shot LLM classification over strict Pydantic schemas, bounding total routing latency to $< 0.12$s.

### 2.2 Self-Correction Verification Policy $\delta_{\text{grader}}(\mathcal{D}_{\text{ret}}, q)$
Following local retrieval, the grader node validates whether the context is sufficient to answer $q$:

$$\delta_{\text{grader}}(\mathcal{D}_{\text{ret}}, q) = \begin{cases} N_{\text{generator}}, & \text{if } S_{\text{rel}}(\mathcal{D}_{\text{ret}}, q) = 1 \\ N_{\text{web}}, & \text{if } S_{\text{rel}}(\mathcal{D}_{\text{ret}}, q) = 0 \end{cases}$$

When $S_{\text{rel}} = 0$, the state transits to $N_{\text{web}}$ (DuckDuckGo Search) for zero-cost context remediation before re-entering $N_{\text{generator}}$.

---

## 3. Adaptive Hybrid Retrieval Operator

Within Tier 1 ($K_{\text{local}}$), queries are executed against domain-isolated ChromaDB collections using an intent-aware hybrid operator:

$$\text{Ret}_{\text{hybrid}}(q) = w_{\text{bm25}} \cdot \text{BM25}(q) + w_{\text{dense}} \cdot \text{DenseSim}(q)$$

where dense similarities are computed using 1024-dimensional $bge\text{-}m3$ embeddings, and weights adapt dynamically based on query type:

$$(w_{\text{bm25}}, w_{\text{dense}}) = \begin{cases} (0.30, 0.70), & q \in Q_{\text{sem}} \quad \text{(Conceptual inquiries)} \\ (0.60, 0.40), & q \in Q_{\text{fact}} \quad \text{(Entity / Exact-formula inquiries)} \end{cases}$$

---

## 4. Two-Phase Context Evaluation Algorithm

To prevent heavy LLM evaluator latency from blocking every retrieved passage, evaluation is decomposed into two distinct phases:

```text
Algorithm 1: Two-Phase Context Evaluation and Dynamic Fallback
------------------------------------------------------------------------
Input : Graph state s, overlap threshold τ_overlap = 0.25
Output: Updated state s' with designated target destination

1: Function EvaluateContextAndRoute(s)
2:     if s.D_ret is empty then
3:         s.S_rel ← 0; s.NextNode ← N_web
4:         return s
5:     end if
6:     if s.d_target ≠ ∅ then
7:         s.S_rel ← 1; s.NextNode ← N_generator
8:         return s                          // Fast-path: user-selected document
9:     end if
10:    T_q ← ExtractMeaningfulTokens(s.q)
11:    H   ← ∑_{t ∈ T_q} 𝕀(t ∈ s.D_ret[0])    // Phase 1: Top-1 lexical overlap
12:    Ratio ← H / |T_q|
13:    if Ratio ≥ τ_overlap then
14:        s.S_rel ← 1; s.NextNode ← N_generator
15:    else
16:        s.S_rel ← 0; s.NextNode ← N_web    // Trigger Phase 2 fallback
17:    end if
18:    return s
19: end Function
```

* **Phase 1 (Sub-centisecond Token Overlap):** Computes lexical overlap on the top-1 ranked chunk with latency $< 0.01$s and 84.6% recall.
* **Phase 2 (Post-Generation Joint Grader):** Verifies factual groundedness and query utility after generation under strict JSON schemas. If violated and loop counter $r < 2$, self-correction is triggered.

