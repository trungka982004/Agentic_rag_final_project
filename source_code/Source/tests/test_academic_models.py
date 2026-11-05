import os
import sys
import unittest
import uuid

# Ensure source root is in sys.path
SOURCE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if SOURCE_ROOT not in sys.path:
    sys.path.insert(0, SOURCE_ROOT)

from backend.database import engine, Base, get_db
from backend.models import User, Project, PaperSection, ProjectReference, DocumentSpan, InlineCitation
from sqlalchemy import inspect

class TestAcademicModels(unittest.TestCase):
    """Verifies that all Academic Studio entities migrate and relate correctly."""

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.db = next(get_db())

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_tables_exist(self):
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        for t in ["projects", "paper_sections", "project_references", "document_spans", "inline_citations"]:
            self.assertIn(t, tables, f"Table '{t}' must exist in database")

    def test_project_and_section_lifecycle(self):
        # 1. Create a test user
        unique_email = f"researcher_{uuid.uuid4().hex[:8]}@studio.test"
        user = User(email=unique_email, hashed_password="hashed_pw_test")
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # 2. Create project
        project = Project(
            user_id=user.id,
            title="A Multi-Domain Agentic RAG Platform",
            template_type="ieee_conference",
            primary_domain="it"
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)

        # 3. Create sections
        sec1 = PaperSection(
            project_id=project.id,
            title="1. Introduction",
            slug="introduction",
            order_index=1,
            content_markdown="# 1. Introduction\nLarge language models..."
        )
        sec2 = PaperSection(
            project_id=project.id,
            title="2. Methodology",
            slug="methodology",
            order_index=2,
            content_markdown="# 2. Methodology\nWe propose..."
        )
        self.db.add_all([sec1, sec2])
        self.db.commit()

        # 4. Create reference & citation
        ref = ProjectReference(
            project_id=project.id,
            bibtex_key="vaswani2017attention",
            title="Attention Is All You Need",
            year=2017,
            bibtex_raw="@article{vaswani2017, title={Attention is all you need}}"
        )
        self.db.add(ref)
        self.db.commit()
        self.db.refresh(ref)

        cite = InlineCitation(
            section_id=sec1.id,
            reference_id=ref.id,
            claim_text="Transformers use self-attention mechanism.",
            verification_status="verified"
        )
        self.db.add(cite)
        self.db.commit()

        # 5. Query verification
        fetched_project = self.db.query(Project).filter(Project.id == project.id).first()
        self.assertIsNotNone(fetched_project)
        self.assertEqual(len(fetched_project.sections), 2)
        self.assertEqual(len(fetched_project.references), 1)
        self.assertEqual(len(fetched_project.sections[0].citations), 1)
        self.assertEqual(fetched_project.sections[0].citations[0].claim_text, "Transformers use self-attention mechanism.")

        # 6. Cascade delete cleanup
        self.db.delete(user)
        self.db.commit()

        # Verify cascade
        self.assertIsNone(self.db.query(Project).filter(Project.id == project.id).first())
        self.assertIsNone(self.db.query(PaperSection).filter(PaperSection.id == sec1.id).first())

if __name__ == "__main__":
    unittest.main()
