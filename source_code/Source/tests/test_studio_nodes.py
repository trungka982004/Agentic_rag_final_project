import unittest
import os
import sys

# Ensure backend and agent modules can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.studio_nodes import (
    literature_matrix_node,
    citation_suggest_node,
    tone_polish_node,
    reviewer2_audit_node
)
from agent.studio_graph import create_studio_agent_graph, route_studio_task

class TestAcademicStudioNodes(unittest.TestCase):
    def test_routing_logic(self):
        """Verify dynamic routing selects appropriate studio state nodes."""
        self.assertEqual(route_studio_task({"question": "audit this paragraph"}), "reviewer2_audit")
        self.assertEqual(route_studio_task({"question": "polish my tone"}), "tone_polish")
        self.assertEqual(route_studio_task({"question": "suggest citations for ResNet"}), "citation_suggest")
        self.assertEqual(route_studio_task({"question": "compare transformers in CV"}), "literature_matrix")

    def test_tone_polish_execution(self):
        """Verify tone polish node elevates draft text into formal scientific prose."""
        state = {
            "question": "we tested a lot of models and our rag is way better than normal chat.",
            "chat_history": []
        }
        res = tone_polish_node(state)
        self.assertIn("generation", res)
        self.assertTrue(len(res["generation"]) > 20)
        # Verify formal academic terms were generated
        gen_lower = res["generation"].lower()
        self.assertTrue("empirical" in gen_lower or "outperformed" in gen_lower or "evaluation" in gen_lower)

    def test_graph_compilation(self):
        """Verify LangGraph Academic Studio compiles with memory saver checkpoints."""
        graph = create_studio_agent_graph()
        self.assertIsNotNone(graph)
        self.assertTrue(hasattr(graph, "invoke"))

if __name__ == "__main__":
    unittest.main()
