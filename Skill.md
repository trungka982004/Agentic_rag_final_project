# System Skills & Capabilities - Intelligent Research Agent

This document outlines the detailed skill sets and capabilities possessed by the Agentic RAG system, categorized by executive functions and data processing abilities.

## 1. Reasoning & Planning Capabilities
These skills serve as the "brain" of the system, controlling the execution flow via LangGraph.

* **Self-Correction & Reflection:**
    * Ability to autonomously evaluate generated answers against retrieved documents (Hallucination Grader).
    * Automatically triggers a re-retrieval process if the initial information is insufficient to address the query.
* **Query Decomposition:**
    * Translates complex, multi-layered questions into several focused sub-queries for multi-dimensional searching.
    * Optimizes search terms (Query Expansion) tailored for specialized academic domains.
* **Context & State Management:**
    * Maintains conversation history and system state across multiple reasoning steps without losing focus or context.

## 2. Advanced Retrieval Skills
Responsible for navigating and extracting insights from the specialized database of 15,495 document chunks.

* **Hybrid Search Execution:**
    * Seamlessly integrates Semantic Search (Vector-based) with Keyword Search (BM25) to ensure maximum recall and precision.
* **Multi-Vector Retrieval:**
    * Capability to extract information from tables, images (via caption descriptions), and structured/unstructured text.
* **Re-ranking Strategy:**
    * Employs Cross-Encoders to re-score the top-K results, ensuring the most relevant context is prioritized for the LLM prompt.

## 3. Tool Use & External Integration
Extends the system's power by interacting with external environments and specialized tools.

* **Python REPL Specialist:**
    * Writes and executes Python code to perform complex numerical analysis on research data.
    * Generates visualizations (Matplotlib/Seaborn) to illustrate trends from CSV or Excel files.
* **Google Workspace Orchestrator:**
    * Autonomously drafts research summaries and reports directly into Google Docs.
    * Manages and updates research databases within Google Sheets.
* **Academic Document Rendering:**
    * Utilizes LaTeX for precise mathematical and physical formula representation.
    * Leverages Mermaid.js to dynamically render system architecture or workflow diagrams.

## 4. Quality Control & Presentation
Ensures that final outputs meet academic and professional standards.

* **Smart Citation & Attribution:**
    * Automatically tags sources for every claim made in the response.
    * Provides direct links to specific page numbers and source PDF files.
* **Multilingual Academic Processing:**
    * Processes specialized English academic literature and provides responses in professional, technical Vietnamese.
* **Safety & Guardrails:**
    * Identifies and rejects requests that violate safety policies or fall outside the project's specialized knowledge scope.

---
*Last Updated: May 15, 2026*
