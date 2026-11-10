import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RecordedTraceTests(unittest.TestCase):
    def test_authenticated_model_evidence(self):
        documents = {d["id"]: d for d in json.loads((ROOT / "data" / "documents.json").read_text(encoding="utf-8"))}
        expected = {
            "codex-normal": ("answered", ["search", "read", "finish"]),
            "codex-conflict": ("needs_clarification", ["search", "read", "read", "finish"]),
            "codex-missing": ("insufficient_information", ["search", "finish"]),
            "codex-failure": ("tool_error", ["search", "read", "finish"]),
        }
        for name, (status, actions) in expected.items():
            with self.subTest(name=name):
                output = json.loads((ROOT / "examples" / (name + ".output.json")).read_text(encoding="utf-8"))
                self.assertEqual(output["status"], status)
                self.assertEqual([step["action"] for step in output["trace"]], actions)
                for citation in output["citations"]:
                    self.assertIn(citation["quote"], documents[citation["doc_id"]]["text"])
        conflict = json.loads((ROOT / "examples" / "codex-conflict.output.json").read_text(encoding="utf-8"))
        self.assertEqual({c["doc_id"] for c in conflict["citations"]}, {"D01", "D02"})


if __name__ == "__main__":
    unittest.main()
