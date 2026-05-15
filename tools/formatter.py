"""
tools/formatter.py

Bộ xử lý định dạng đầu ra cho Agentic RAG System.
Hỗ trợ chuẩn hoá LaTeX (công thức toán học) và Mermaid (sơ đồ kiến trúc).

Mục tiêu:
    - Đảm bảo công thức toán học được bao bọc đúng cú pháp LaTeX ($...$  hoặc $$...$$).
    - Đảm bảo các đoạn mã Mermaid được đặt trong fenced code block đúng chuẩn.
    - Giúp frontend (Streamlit, Gradio, hoặc bất kỳ UI nào) render được ngay lập tức
      mà không cần xử lý thêm.
"""

import re


# ---------------------------------------------------------------------------
# LaTeX Normalizer
# ---------------------------------------------------------------------------

# Các cú pháp LaTeX phổ biến mà LLM thường trả về sai format
_LATEX_INLINE_PATTERNS = [
    # \( ... \) → $ ... $
    (r"\\\((.+?)\\\)", r"$\1$"),
    # \[ ... \] → $$ ... $$
    (r"\\\[(.+?)\\\]", r"$$\1$$"),
]

_LATEX_BLOCK_PATTERN = re.compile(
    r"\\\[(.+?)\\\]",
    re.DOTALL,
)


def normalize_latex(text: str) -> str:
    """
    Chuẩn hoá các công thức LaTeX trong văn bản về dạng $ ... $ (inline)
    hoặc $$ ... $$ (block), tương thích với MathJax / KaTeX.

    Args:
        text: Văn bản đầu vào có thể chứa LaTeX.

    Returns:
        Văn bản đã được chuẩn hoá.
    """
    # Thay \\[ ... \\] (multi-line) bằng $$ ... $$
    text = _LATEX_BLOCK_PATTERN.sub(lambda m: f"$$\n{m.group(1).strip()}\n$$", text)

    # Thay \\( ... \\) (inline) bằng $ ... $
    text = re.sub(r"\\\((.+?)\\\)", r"$\1$", text)

    return text


# ---------------------------------------------------------------------------
# Mermaid Normalizer
# ---------------------------------------------------------------------------

# Pattern nhận diện các khối mermaid bị viết sai (thiếu backtick, hoặc chỉ có "mermaid:")
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
    Đảm bảo tất cả khối Mermaid diagram đều nằm trong fenced code block
    chuẩn (```mermaid ... ```) để frontend có thể render được.

    Nếu LLM xuất ra "mermaid:\n<code>", hàm này sẽ bọc lại đúng chuẩn.

    Args:
        text: Văn bản đầu vào có thể chứa Mermaid diagram.

    Returns:
        Văn bản đã được chuẩn hoá.
    """
    # Nếu đã có ``` mermaid đúng chuẩn → không cần sửa, giữ nguyên
    if _MERMAID_STRICT_PATTERN.search(text):
        return text

    # Nếu phát hiện cú pháp lỏng lẻo → bọc lại
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
    Làm nổi bật các trích dẫn nguồn tài liệu (Source: ...) trong output
    bằng cách bổ sung định dạng markdown bold.

    Args:
        text: Văn bản có thể chứa nguồn trích dẫn theo chuẩn ingestion pipeline.

    Returns:
        Văn bản với các trích dẫn được làm nổi bật.
    """
    # Pattern: "--- Source: filename.pdf (Page N) ---"
    citation_pattern = re.compile(
        r"---\s*Source:\s*(.+?)\s*\(Page\s*(\d+)\)\s*---",
        re.IGNORECASE,
    )

    def _bold_citation(m: re.Match) -> str:
        source = m.group(1).strip()
        page = m.group(2).strip()
        return f"\n> 📄 **Nguồn:** `{source}` — Trang **{page}**\n"

    return citation_pattern.sub(_bold_citation, text)


# ---------------------------------------------------------------------------
# Master Formatter
# ---------------------------------------------------------------------------

def format_agent_output(text: str) -> str:
    """
    Pipeline xử lý đầu ra tổng hợp: áp dụng tuần tự tất cả các bộ chuẩn hoá.

    Thứ tự xử lý:
        1. Chuẩn hoá LaTeX
        2. Chuẩn hoá Mermaid
        3. Làm nổi bật Citations

    Args:
        text: Văn bản thô từ LLM.

    Returns:
        Văn bản đã được định dạng đầy đủ.
    """
    text = normalize_latex(text)
    text = normalize_mermaid(text)
    text = format_citations(text)
    return text
