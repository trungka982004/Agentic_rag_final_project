import unittest
import os
import sys
import zipfile

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.export_service import (
    markdown_to_latex,
    build_project_latex_source,
    compile_pdf_in_app,
    generate_overleaf_zip_bundle
)

class MockProject:
    title = "Empirical Evaluation of Tri-Tier Agentic RAG"
    abstract_text = "Retrieval-Augmented Generation evaluation across 618 papers."
    keywords = ["Agentic RAG", "Evaluation", "Software Engineering"]

class MockSection:
    def __init__(self, title, slug, order, content):
        self.title = title
        self.slug = slug
        self.order_index = order
        self.content_markdown = content

class MockReference:
    def __init__(self, key, title, authors, year, raw):
        self.bibtex_key = key
        self.title = title
        self.authors = authors
        self.year = year
        self.bibtex_raw = raw

class TestExportService(unittest.TestCase):
    def test_markdown_to_latex(self):
        """Verify markdown conversion to clean LaTeX syntax."""
        md = "## 1. Introduction\n\n**Deep learning** is *effective*.\n$$\nE = mc^2\n$$"
        tex = markdown_to_latex(md)
        self.assertIn(r"\subsection{1. Introduction}", tex)
        self.assertIn(r"\textbf{Deep learning}", tex)
        self.assertIn(r"\textit{effective}", tex)
        self.assertIn(r"\begin{equation}", tex)

    def test_build_project_latex_source(self):
        """Verify generation of complete IEEEtran main.tex and references.bib."""
        proj = MockProject()
        sections = [
            MockSection("Introduction", "intro", 1, "## Introduction\n\nPrior work has shown promise."),
            MockSection("Methodology", "method", 2, "## Methodology\n\nOur system architecture is tri-tier.")
        ]
        refs = [
            MockReference("vaswani2017", "Attention Is All You Need", "Vaswani et al.", 2017, "@article{vaswani2017, title={Attention}}")
        ]

        latex_src, bib_src = build_project_latex_source(proj, sections, refs)
        self.assertIn(r"\documentclass[conference]{IEEEtran}", latex_src)
        self.assertIn("Empirical Evaluation of Tri-Tier Agentic RAG", latex_src)
        self.assertIn(r"\bibliography{references}", latex_src)
        self.assertIn("@article{vaswani2017", bib_src)

    def test_compile_pdf_in_app(self):
        """Verify in-app PDF compilation engine produces valid camera-ready PDF."""
        proj = MockProject()
        sections = [MockSection("Introduction", "intro", 1, "Introduction content.")]
        refs = []
        latex_src, bib_src = build_project_latex_source(proj, sections, refs)

        out_pdf = compile_pdf_in_app("test_proj_001", latex_src, bib_src, output_dir="temp_assets/test_output")
        self.assertTrue(os.path.exists(out_pdf))
        self.assertTrue(os.path.getsize(out_pdf) > 1000) # Valid PDF size

    def test_generate_overleaf_zip_bundle(self):
        """Verify Overleaf ZIP archive contains main.tex, references.bib, and instructions."""
        proj = MockProject()
        sections = [MockSection("Abstract", "abstract", 0, "Abstract")]
        refs = [MockReference("ref1", "Title", "Author", 2026, "@article{ref1, title={Title}}")]
        latex_src, bib_src = build_project_latex_source(proj, sections, refs)

        zip_buf = generate_overleaf_zip_bundle("test_proj_001", latex_src, bib_src)
        self.assertTrue(zip_buf.getbuffer().nbytes > 100)

        with zipfile.ZipFile(zip_buf, "r") as zf:
            namelist = zf.namelist()
            self.assertIn("main.tex", namelist)
            self.assertIn("references.bib", namelist)
            self.assertIn("README.md", namelist)

if __name__ == "__main__":
    unittest.main()
