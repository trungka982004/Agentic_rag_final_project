# Scientific Research Manuscripts & LaTeX Assets

This directory contains the complete LaTeX source code, figure assets, standardized BibTeX references, and Overleaf distribution packages for the two academic papers accepted/prepared for IEEE conference submission.

---

## 📑 Directory Contents

```text
science_paper_assets/
├── methodology/                # Detailed mathematical formalization & algorithms
│   └── README.md
├── experiments/                # Benchmark setups, baseline comparisons & Pareto analysis
│   └── README.md
├── science_paper_images/       # High-resolution (300 DPI) vector diagrams & screenshots
│   ├── fig1_architecture.png   # Three-tier system architecture
│   ├── fig2_state_graph.png    # LangGraph state transition graph
│   ├── fig3_sequence_diagram.png # Real-time WebSocket streaming sequence
│   ├── fig4_pareto_chart.png   # Pareto frontier chart (Marginal cost vs Faithfulness)
│   └── fig5_ui_walkthrough.png # Real Next.js 14 web client interface screenshot
├── scripts/                    # LaTeX verification, figure generation & packaging scripts
│   ├── pack_overleaf_projects.py # One-click Overleaf zip generator
│   └── generate_academic_pareto.py # Pareto chart generation script
├── main_en.tex                 # Paper 1: Core Research Paper (IEEEtran Conference Format)
├── main_en_standalone.tex      # Paper 1: Self-contained LaTeX (inlined bibliography)
├── system_paper_en.tex         # Paper 2: Open-Source System Demo Paper (IEEE Track)
├── system_paper_en_standalone.tex # Paper 2: Self-contained LaTeX (inlined bibliography)
├── references.bib              # Standardized BibTeX citations (19 entries)
└── README.md                   # This overview document
```

---

## 📄 Academic Papers Overview

### Paper 1: Research Paper (Core Method & Algorithms)
* **Title:** *Tiered Self-Corrective Agentic RAG: Dynamic Knowledge Routing with Multi-Domain Hybrid Retrieval*
* **Template:** IEEE Conference (double-column, 6 pages).
* **Source:** [`main_en.tex`](main_en.tex) (Standalone: [`main_en_standalone.tex`](main_en_standalone.tex))
* **Core Contributions:**
  1. Formalization of global state space $\mathcal{S}$ and discrete transition policies $\delta_{\text{router}}$ and $\delta_{\text{grader}}$ on LangGraph.
  2. Intent-aware adaptive hybrid search ($bge\text{-}m3$ + BM25) across 8 isolated domain collections.
  3. Resource-efficient Two-Phase Context Verification combining a $<0.01$s lexical token overlap filter with a structured JSON post-grader.
  4. Quantitative benchmark against 5 SOTA baselines (Naive, Advanced, Adaptive, CRAG, Self-RAG) with paired Student's $t$-test and Wilcoxon statistical validation.
* **Detailed Documentation:**
  - [Mathematical Formalization & Graph Policies](methodology/README.md)
  - [Quantitative Benchmark & Empirical Results](experiments/README.md)

### Paper 2: Open-Source System Demonstration Paper
* **Title:** *An Open-Source Multi-Domain Agentic RAG Platform with Tiered Knowledge Routing and Real-Time State Synchronization*
* **Template:** IEEE System Demonstration Track (double-column, 4 pages).
* **Source:** [`system_paper_en.tex`](system_paper_en.tex) (Standalone: [`system_paper_en_standalone.tex`](system_paper_en_standalone.tex))
* **Core Contributions:**
  1. Fullstack production architecture (FastAPI Gateway, LangGraph Core, Next.js 14 Web UI, PostgreSQL 16).
  2. Chunk-based WebSocket state streaming protocol rendering live reasoning badge telemetry.
  3. 100% local inference privacy via Ollama Qwen2.5 7B (Zero Cloud Leak).
  4. Comprehensive feature matrix comparison against leading open-source RAG platforms (Dify, RAGFlow, FastGPT, Khoj).
  5. 1-Click Docker Compose deployment under Apache-2.0 License.

---

## 📦 Overleaf Packaging & Compilation

To build the camera-ready PDFs on Overleaf or local LaTeX:

```bash
# Run packaging script to bundle tex, bib, and images into overleaf_packages/
python scripts/pack_overleaf_projects.py
```

Generated packages in `overleaf_packages/`:
- `overleaf_project_en.zip`: Research Paper project.
- `overleaf_project_system_paper_en.zip`: System Demo Paper project.
- `overleaf_project_v10.zip`: Full Vietnamese graduation thesis report.

---

## 📚 Standardized BibTeX Citation

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

