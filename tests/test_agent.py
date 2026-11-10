import json
import unittest
import tempfile
from pathlib import Path

from src.agent import run_agent
from src.models import MockModel
from src.tools import KnowledgeTools


ROOT = Path(__file__).resolve().parents[1]


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.tools = KnowledgeTools(ROOT / "data" / "documents.json")

    def ask(self, question, **kwargs):
        return run_agent(question, MockModel(), self.tools, **kwargs)

    def test_clear_answer_cites_original_text(self):
        result = self.ask("年假需要提前多久申请？")
        self.assertEqual(result["status"], "answered")
        self.assertEqual([c["doc_id"] for c in result["citations"]], ["D03"])
        self.assertIn(result["citations"][0]["quote"], self.tools.by_id["D03"]["text"])
        self.assertTrue(any(t["action"] == "read" for t in result["trace"]))

    def test_conflict_is_disclosed_with_both_sources(self):
        result = self.ask("报销期限是多久？")
        self.assertEqual(result["status"], "needs_clarification")
        self.assertEqual({c["doc_id"] for c in result["citations"]}, {"D01", "D02"})
        self.assertIn("冲突", result["answer"])

    def test_out_of_scope_question(self):
        result = self.ask("火星办公室的停车费是多少？")
        self.assertEqual(result["status"], "insufficient_information")
        self.assertEqual(result["citations"], [])

    def test_paraphrase_search(self):
        result = self.ask("休年假要早几天提？")
        self.assertEqual(result["status"], "answered")
        self.assertEqual(result["citations"][0]["doc_id"], "D03")

    def test_annual_leave_query_with_submit_excludes_expense_docs(self):
        hits = self.tools.search("年假申请需要提前多久提交")
        self.assertEqual([h["doc_id"] for h in hits], ["D03"])

    def test_context_followup(self):
        result = self.ask("还需要主管批准吗？", history=[{"role": "user", "content": "年假怎么申请？"}])
        self.assertEqual(result["status"], "answered")
        self.assertEqual(result["citations"][0]["doc_id"], "D03")

    def test_tool_failure_is_not_answered(self):
        tools = KnowledgeTools(ROOT / "data" / "documents.json", fail_tool="read")
        result = run_agent("年假需要提前多久申请？", MockModel(), tools)
        self.assertEqual(result["status"], "tool_error")
        self.assertIn("read", result["missing_information"])

    def test_search_failure_is_not_answered(self):
        tools = KnowledgeTools(ROOT / "data" / "documents.json", fail_tool="search")
        result = run_agent("年假需要提前多久申请？", MockModel(), tools)
        self.assertEqual(result["status"], "tool_error")

    def test_changed_source_changes_answer(self):
        documents = json.loads((ROOT / "data" / "documents.json").read_text(encoding="utf-8"))
        documents[2]["text"] = "年假须至少提前 5 个工作日申请，并经直属主管批准。"
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "docs.json"
            path.write_text(json.dumps(documents, ensure_ascii=False), encoding="utf-8")
            result = run_agent("年假需要提前多久申请？", MockModel(), KnowledgeTools(path))
        self.assertIn("5 个工作日", result["answer"])
        self.assertNotIn("3 个工作日", result["answer"])

    def test_step_limit_is_explicit(self):
        result = self.ask("年假需要提前多久申请？", max_steps=1)
        self.assertEqual(result["status"], "incomplete_step_limit")

    def test_unsupported_quote_is_rejected(self):
        class BadModel:
            def decide(self, messages):
                return {"action": "finish", "status": "answered", "answer": "凭空答案", "citations": [{"doc_id": "D03", "quote": "不存在的原文"}], "reason": "test"}
        result = run_agent("年假需要提前多久申请？", BadModel(), self.tools)
        self.assertEqual(result["status"], "invalid_answer")


if __name__ == "__main__":
    unittest.main()
