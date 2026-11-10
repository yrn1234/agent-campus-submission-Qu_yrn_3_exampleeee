import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.models import CodexCLIModel


class CodexCLIModelTests(unittest.TestCase):
    def test_decision_uses_cli_output_and_visible_observations(self):
        calls = []

        class Completed:
            returncode = 0

        def fake_run(args, **kwargs):
            calls.append((args, kwargs))
            output = Path(args[args.index("-o") + 1])
            output.write_text(json.dumps({"action": "read", "doc_id": "D03", "reason": "命中后读原文"}), encoding="utf-8")
            return Completed()

        messages = [
            {"role": "user", "question": "年假要提前多久？", "history": []},
            {"role": "tool", "action": "search", "result": {"hits": [{"doc_id": "D03"}]}}
        ]
        decision = CodexCLIModel(runner=fake_run).decide(messages)
        self.assertEqual(decision["action"], "read")
        self.assertEqual(decision["doc_id"], "D03")
        self.assertIn("D03", calls[0][1]["input"])
        self.assertIn("--sandbox", calls[0][0])
        self.assertIn("read-only", calls[0][0])


if __name__ == "__main__":
    unittest.main()
