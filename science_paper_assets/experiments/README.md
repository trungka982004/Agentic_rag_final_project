# Empirical Evaluation, Benchmark & Statistical Validation

This document details the experimental setup, quantitative results against 5 SOTA baselines, paired statistical hypothesis testing, component ablation studies, and instructions to reproduce all empirical findings.

---

## 1. Experimental Setup & Benchmark Dataset

* **Test Corpus:** 150 diverse multi-domain academic queries across 4 core STEM disciplines with high mathematical and technical density:
  - Computer Science: 38 queries
  - Physics: 38 queries
  - Mathematics: 37 queries
  - Electronics: 37 queries
* **Ground Truth Validation:** Verified by three independent domain experts under binary relevance criteria, achieving an overall **Fleiss' Kappa $\kappa = 0.81$** (95% CI: $[0.74, 0.88]$):
  - CS: $\kappa = 0.84$
  - Physics: $\kappa = 0.82$
  - Mathematics: $\kappa = 0.80$
  - Electronics: $\kappa = 0.79$
* **Foundation Model:** All baselines and the proposed framework run on an identical local foundation model (**Qwen2.5 7B**, context 3,072 tokens, $T=0.0$) via Ollama to ensure strict comparability.

---

## 2. Quantitative Comparison against SOTA Baselines

Metrics are reported as $\text{Mean} \pm \text{Std. Dev.}$ across 5 independent runs on $N = 150$ queries:

| Architecture / Baseline Model | Relevance (RAGAS) | Faithfulness (RAGAS) | Context Precision | Context Recall | First-Token (s) | End-to-End (s) | Marginal Cost ($/1k) | Domain Isolated |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Naive RAG** *(Lewis et al., 2020)* | 0.58 $\pm$ 0.04 | 0.49 $\pm$ 0.05 | 0.44 $\pm$ 0.05 | 0.43 $\pm$ 0.05 | **1.12 $\pm$ 0.15** | **1.85 $\pm$ 0.20** | **$0.00** | No |
| **Advanced RAG** *(Gao et al., 2023)* | 0.62 $\pm$ 0.03 | 0.51 $\pm$ 0.04 | 0.46 $\pm$ 0.04 | 0.45 $\pm$ 0.04 | 1.45 $\pm$ 0.18 | 2.30 $\pm$ 0.25 | **$0.00** | No |
| **Adaptive-RAG** *(Jeong et al., 2024)* | 0.66 $\pm$ 0.04 | 0.53 $\pm$ 0.04 | 0.47 $\pm$ 0.04 | 0.48 $\pm$ 0.04 | 2.15 $\pm$ 0.25 | 3.20 $\pm$ 0.35 | $1.50 | No |
| **Corrective RAG (CRAG)** *(Yan et al., 2024)* | 0.67 $\pm$ 0.03 | 0.54 $\pm$ 0.04 | 0.48 $\pm$ 0.04 | 0.51 $\pm$ 0.04 | 3.80 $\pm$ 0.35 | 4.85 $\pm$ 0.45 | $3.20 | No |
| **Self-RAG** *(Asai et al., 2024)* | 0.68 $\pm$ 0.03 | 0.58 $\pm$ 0.04 | 0.49 $\pm$ 0.04 | 0.49 $\pm$ 0.04 | 4.20 $\pm$ 0.40 | 5.45 $\pm$ 0.50 | $1.80 | No |
| **Proposed Agentic RAG (Ours)** | **0.73 $\pm$ 0.03** | **0.62 $\pm$ 0.04** | **0.56 $\pm$ 0.04** | **0.54 $\pm$ 0.04** | 1.85 $\pm$ 0.25 | 3.65 $\pm$ 0.40 | **$0.90** | **Yes (8 Stores)** |

### 2.1 Marginal API Cost Formulation
$$\text{Cost}_{\text{marginal}}/1k = 1{,}000 \times \big( C_{\text{local}} + f_{\text{fallback}} \cdot C_{\text{web}} + f_{\text{expert}} \cdot C_{\text{tavily}} + C_{\text{buffer}} \big)$$

* $C_{\text{local}} = \$0.00$ (Local Qwen2.5 7B runtime via Ollama).
* $f_{\text{fallback}} = 18.0\%$ (27/150 queries triggering free DuckDuckGo search).
* $f_{\text{expert}} = 12.0\%$ (18/150 complex queries routed to Tavily API at $C_{\text{tavily}} = \$0.005/\text{query}$).
* $C_{\text{buffer}} = \$0.0003/\text{query}$ (\$0.30/1k buffer).
* **Net marginal cost:** **$0.90 / 1,000 queries** (**71.9% reduction** vs. CRAG at $3.20; **50.0% reduction** vs. Self-RAG at $1.80).

---

## 3. Paired Statistical Hypothesis Testing

To prove that performance gains are statistically significant and not random artifacts of sampling, two-tailed **paired Student's $t$-tests ($df = 149$)** and non-parametric **Wilcoxon signed-rank tests** were conducted on paired differences ($d_i = y_i^{\text{ours}} - y_i^{\text{base}}$):

* **Over Corrective RAG (CRAG):**
  - Answer Relevance: $t = 3.82, p < 0.001$; Wilcoxon $W = 3380, p < 0.001$.
  - Faithfulness: $t = 3.95, p < 0.001$; Wilcoxon $W = 3290, p < 0.001$.
* **Over Self-RAG:**
  - Answer Relevance: $t = 3.61, p < 0.001$; Wilcoxon $W = 3420, p < 0.001$.
  - Faithfulness: $t = 2.48, p = 0.014$; Wilcoxon $W = 4350, p = 0.014$.
* **Over Advanced RAG:**
  - Answer Relevance: $t = 5.46, p < 0.001$; Wilcoxon $W = 2150, p < 0.001$.
  - Faithfulness: $t = 4.78, p < 0.001$; Wilcoxon $W = 2680, p < 0.001$.

---

## 4. Component Ablation Study

Evaluated across 5 independent benchmark runs ($N = 150$ each):

| Configuration | Relevance | Faithfulness | Context Precision | Context Recall | Average Loops |
| :--- | :---: | :---: | :---: | :---: | :---: |
| (1) Dense DPR ($bge\text{-}m3$) | 0.58 $\pm$ 0.04 | 0.49 $\pm$ 0.05 | 0.44 $\pm$ 0.05 | 0.43 $\pm$ 0.05 | 1.00 |
| (2a) Static Hybrid | 0.62 $\pm$ 0.03 | 0.51 $\pm$ 0.04 | 0.46 $\pm$ 0.04 | 0.45 $\pm$ 0.04 | 1.00 |
| (2b) Adaptive Hybrid | 0.65 $\pm$ 0.03 | 0.54 $\pm$ 0.04 | 0.49 $\pm$ 0.04 | 0.48 $\pm$ 0.04 | 1.00 |
| (3) Hybrid + Router | 0.69 $\pm$ 0.03 | 0.56 $\pm$ 0.04 | 0.52 $\pm$ 0.04 | 0.51 $\pm$ 0.04 | 1.05 |
| (3a) + Phase 1 Only (Lexical) | 0.70 $\pm$ 0.03 | 0.58 $\pm$ 0.04 | 0.53 $\pm$ 0.04 | 0.52 $\pm$ 0.04 | 1.08 |
| (3b) + Phase 2 Only (LLM) | 0.71 $\pm$ 0.03 | 0.60 $\pm$ 0.04 | 0.55 $\pm$ 0.04 | 0.53 $\pm$ 0.04 | 1.24 |
| **(4) Full Proposed (Two-Phase)** | **0.73 $\pm$ 0.03** | **0.62 $\pm$ 0.04** | **0.56 $\pm$ 0.04** | **0.54 $\pm$ 0.04** | **1.18** |

*Takeaway:* Phase 1 alone eliminates obvious lexical noise with $<0.01$s overhead. Phase 2 alone provides deep factual verification but causes loop overhead to spike to 1.24 without Phase 1 pruning. Unifying both produces the optimal balance: **Faithfulness 0.62** with **average loops bounded at 1.18** (82.0% first-pass completion).

---

## 5. How to Reproduce Benchmarks

Navigate to the source directory and execute the benchmark suite:

```bash
cd source_code/Source

# Run the complete 150 test case benchmark
python evaluate.py

# Resume an interrupted evaluation
python evaluate.py --resume
```

Results are saved incrementally to:
- `source_code/Source/evaluation_results.json`
- `source_code/Source/evaluation_results.csv`

