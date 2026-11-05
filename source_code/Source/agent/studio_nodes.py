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
