"""
tools/formatter.py

Output formatting processor for the Agentic RAG System.
Supports normalization of LaTeX (mathematical formulas) and Mermaid (architectural flowcharts).

Objectives:
    - Ensure mathematical formulas are correctly wrapped in LaTeX syntax ($...$ or $$...$$).
    - Ensure Mermaid code blocks are enclosed in the correct fenced code blocks.
    - Assist the frontend (Streamlit, Gradio, or any UI) to render content instantly without extra processing.
"""

import re


# ---------------------------------------------------------------------------
# LaTeX Normalizer
# ---------------------------------------------------------------------------

# Common LaTeX syntaxes that LLM often returns in incorrect format
_LATEX_INLINE_PATTERNS = [
    # \( ... \) -> $ ... $
    (r"\\\((.+?)\\\)", r"$\1$"),
    # \[ ... \] -> $$ ... $$
    (r"\\\[(.+?)\\\]", r"$$\1$$"),
]

_LATEX_BLOCK_PATTERN = re.compile(
    r"\\\[(.+?)\\\]",
    re.DOTALL,
)


def normalize_latex(text: str) -> str:
    """
    Normalizes LaTeX formulas in text to standard $ ... $ (inline)
    or $$ ... $$ (block) formats, compatible with MathJax / KaTeX.

    Args:
        text: Input text potentially containing LaTeX.

    Returns:
        Normalized text.
    """
    # Replace \\[ ... \\] (multi-line) with $$ ... $$
    text = _LATEX_BLOCK_PATTERN.sub(lambda m: f"$$\n{m.group(1).strip()}\n$$", text)

    # Replace \\( ... \\) (inline) with $ ... $
    text = re.sub(r"\\\((.+?)\\\)", r"$\1$", text)

    return text


# ---------------------------------------------------------------------------
# Mermaid Normalizer
# ---------------------------------------------------------------------------

# Pattern to detect improperly formatted mermaid blocks (missing backticks or starting with "mermaid:")
_MERMAID_LOOSE_PATTERN = re.compile(
    r"(?:```mermaid\s*\n|mermaid:\s*\n)(.*?)(?:```|$)",
    re.DOTALL | re.IGNORECASE,
)

_MERMAID_STRICT_PATTERN = re.compile(
    r"```mermaid\s*\n(.*?)```",
    re.DOTALL,
)


def normalize_mermaid(text: str) -> str:
    """
    Ensures all Mermaid diagram blocks are enclosed in standard fenced code blocks
    (```mermaid ... ```) so that the frontend can render them properly.

    If the LLM outputs "mermaid:\n<code>", this function wraps it correctly.

    Args:
        text: Input text potentially containing Mermaid diagrams.

    Returns:
        Normalized text.
    """
    # If standard ```mermaid already exists, keep as-is
    if _MERMAID_STRICT_PATTERN.search(text):
        return text

    # If loose syntax is detected, wrap it
    def _wrap(m: re.Match) -> str:
        inner = m.group(1).strip()
        return f"```mermaid\n{inner}\n```"

    text = _MERMAID_LOOSE_PATTERN.sub(_wrap, text)
    return text


# ---------------------------------------------------------------------------
# Metadata / Citation Formatter
# ---------------------------------------------------------------------------

def format_citations(text: str) -> str:
    """
    Highlights document citations (Source: ...) in the output
    by formatting them as markdown bold elements.

    Args:
        text: Text potentially containing standard citations from the ingestion pipeline.

    Returns:
        Text with highlighted citations.
    """
    # Pattern: "--- Source: filename.pdf (Page N) ---"
    citation_pattern = re.compile(
        r"---\s*Source:\s*(.+?)\s*\(Page\s*(\d+)\)\s*---",
        re.IGNORECASE,
    )

    def _bold_citation(m: re.Match) -> str:
        source = m.group(1).strip()
        page = m.group(2).strip()
        return f"\n> 📄 **Source:** `{source}` — Page **{page}**\n"

    return citation_pattern.sub(_bold_citation, text)


# ---------------------------------------------------------------------------
# Meta-Notes Filter
# ---------------------------------------------------------------------------

def strip_llm_meta_notes(text: str) -> str:
    """
    Detects and strips out LLM self-referential reflection notes (e.g., Note: Since the instruction...)
    to ensure the output is clean for the end user and document exports.
    """
    # Remove notes or comments starting with "Note:" or "Ghi chú:" that discuss system prompts, rules, or constraints
    text = re.sub(
        r"(?:Note|Ghi chú):\s*(?:Since the instruction|Bởi vì hướng dẫn|Do quy định|Because of rules|Since the rules).*?($|\n)", 
        "", 
        text, 
        flags=re.IGNORECASE | re.DOTALL
    )
    return text.strip()


# ---------------------------------------------------------------------------
# Master Formatter
# ---------------------------------------------------------------------------

def format_agent_output(text: str) -> str:
    """
    Comprehensive output processing pipeline: sequentially applies all normalizers.

    Processing order:
        1. Normalize LaTeX
        2. Normalize Mermaid
        3. Highlight Citations
        4. Strip LLM reflection and system constraint notes

    Args:
        text: Raw text generated by the LLM.

    Returns:
        Fully formatted and cleaned text.
    """
    text = normalize_latex(text)
    text = normalize_mermaid(text)
    text = format_citations(text)
    text = strip_llm_meta_notes(text)
    return text


def parse_markdown_table(text: str) -> list[list[str]] | None:
    """
    Parses the first markdown table found in the text into a list of lists of strings
    suitable for exporting to Google Sheets.
    """
    lines = text.strip().split("\n")
    table_lines = []
    in_table = False
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            in_table = True
            table_lines.append(stripped)
        else:
            if in_table:
                break
                
    if not table_lines or len(table_lines) < 2:
        return None
        
    parsed_table = []
    for line in table_lines:
        # Skip the divider/separator row (e.g., |---|---| or | :--- | :---: |)
        if all(c in " |:-" for c in line) and "-" in line:
            continue
        # Split cell contents and strip whitespaces, ignoring the leading and trailing empty split items
        row = [cell.strip() for cell in line.split("|")[1:-1]]
        parsed_table.append(row)
        
    return parsed_table if parsed_table else None
