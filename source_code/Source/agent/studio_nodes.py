import re
import os
import json
import logging
from typing import Dict, Any, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from agent.state import GraphState
from local_rag import llm, retrieve_context, get_vector_db, get_bm25_retriever, logger

# Prompt 1: Literature Review Matrix Synthesizer
LITERATURE_MATRIX_PROMPT = """You are an expert Academic Literature Review Assistant for high-impact computer science, science, and engineering papers.
The user wants a comparative literature review matrix synthesizing the most relevant findings.

Research Query / Topic: {question}

Retrieved Corpus Context:
{documents}

Construct a comprehensive Markdown Literature Review Matrix table.
Format requirements:
1. Provide an executive summary paragraph contextualizing the research landscape.
2. Present a structured Markdown table with columns:
   | Paper Reference | Primary Methodology | Key Quantitative Results | Notable Limitations / Research Gaps |
3. Follow with a synthesis paragraph outlining the primary open challenge that motivates new contributions.
4. Ensure all paper citations are formatted as \\cite{{bibtex_key}} using standard author-year keys.
"""

def literature_matrix_node(state: GraphState) -> Dict[str, Any]:
    """Synthesizes a multi-paper comparative literature review matrix table."""
    logger.info("Executing studio node: literature_matrix_node")
    query = state.get("question", "")
    domain = state.get("domain", "it")
    docs = state.get("documents", [])

    if not docs:
        docs = retrieve_context(query, domain=domain, top_k=6)

    context_str = "\n\n---\n\n".join(docs[:6]) if docs else "No direct local documents found."
    
    prompt = ChatPromptTemplate.from_template(LITERATURE_MATRIX_PROMPT)
    chain = prompt | llm | StrOutputParser()
    
    try:
        generation = chain.invoke({
            "question": query,
            "documents": context_str
        })
    except Exception as e:
        logger.error(f"Error in literature_matrix_node: {e}")
        generation = f"Failed to synthesize literature matrix: {str(e)}"

    return {
        "documents": docs,
        "generation": generation
    }


# Prompt 2: Smart Citation Suggester & BibTeX Extractor
CITATION_SUGGEST_PROMPT = """You are a grounded Academic Citation and Bibliographical Indexer.
Analyze the provided draft paragraph, ground its factual claims in the retrieved literature, and insert accurate in-text \\cite{{key}} citations.

Draft Paragraph:
{draft_text}

Available Academic Corpus Context:
{documents}

Instructions:
1. Rewrite the draft paragraph inserting \\cite{{bibtex_key}} immediately after any claim, empirical metric, or architectural formulation supported by the context.
2. Underneath the paragraph, output a ```bibtex code block containing clean BibTeX entries for all cited papers.
3. If an assertion is not grounded in the corpus, flag it with [Citation Needed].
"""

def citation_suggest_node(state: GraphState) -> Dict[str, Any]:
    """Scans draft text, queries literature corpus, and injects grounded \\cite{} tags and BibTeX entries."""
    logger.info("Executing studio node: citation_suggest_node")
    draft_text = state.get("question", "")
    domain = state.get("domain", "it")
    docs = state.get("documents", [])

    if not docs:
        docs = retrieve_context(draft_text, domain=domain, top_k=5)

    context_str = "\n\n---\n\n".join(docs[:5]) if docs else "No local documents available."
    prompt = ChatPromptTemplate.from_template(CITATION_SUGGEST_PROMPT)
    chain = prompt | llm | StrOutputParser()

    try:
        generation = chain.invoke({
            "draft_text": draft_text,
            "documents": context_str
        })
    except Exception as e:
        logger.error(f"Error in citation_suggest_node: {e}")
        generation = f"Failed to suggest citations: {str(e)}"

    return {
        "documents": docs,
        "generation": generation
    }


# Prompt 3: Scientific Tone & Grammar Polish
TONE_POLISH_PROMPT = """You are a senior academic editor for top-tier IEEE/ACM transactions and Springer Nature journals.
Refine the following paragraph into formal, rigorous scientific prose.

Input Text:
{draft_text}

Rules:
1. Transform colloquial phrasing into formal academic English (e.g. "we tested a lot" -> "we conducted extensive empirical evaluation").
2. Maintain objective third-person or precise first-person plural active voice.
3. Format all mathematical variables into LaTeX math notation (e.g., $N$, $\\mathcal{{L}}_{{CE}}$, $\\mathbb{{R}}^d$).
4. Retain all existing \\cite{{...}} references exactly in place.
5. Provide the polished paragraph followed by a brief bullet list of key stylistic enhancements made.
"""

def tone_polish_node(state: GraphState) -> Dict[str, Any]:
    """Refines rough draft sections into publication-grade IEEE/ACM scientific English."""
    logger.info("Executing studio node: tone_polish_node")
    draft_text = state.get("question", "")

    prompt = ChatPromptTemplate.from_template(TONE_POLISH_PROMPT)
    chain = prompt | llm | StrOutputParser()

    try:
        generation = chain.invoke({
            "draft_text": draft_text
        })
    except Exception as e:
        logger.error(f"Error in tone_polish_node: {e}")
        generation = f"Failed to polish academic tone: {str(e)}"

    return {
        "generation": generation
    }
