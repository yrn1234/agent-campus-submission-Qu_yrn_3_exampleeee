"""Command line entry point: python -m src.cli."""
import argparse
import json
from pathlib import Path

from .agent import run_agent
from .models import CodexCLIModel, LiveModel, MockModel
from .tools import KnowledgeTools


def main():
    parser = argparse.ArgumentParser(description="企业知识问答 Agent（题目 3）")
    parser.add_argument("question")
    parser.add_argument("--mode", choices=["mock", "live", "codex"], default="mock")
    parser.add_argument("--history-file", help="JSON array of {role,content} messages")
    parser.add_argument("--documents", default=str(Path(__file__).resolve().parents[1] / "data" / "documents.json"))
    parser.add_argument("--fail-tool", choices=["search", "read"])
    parser.add_argument("--max-steps", type=int, default=8)
    args = parser.parse_args()
    history = json.loads(Path(args.history_file).read_text(encoding="utf-8")) if args.history_file else []
    model = {"mock": MockModel, "live": LiveModel, "codex": CodexCLIModel}[args.mode]()
    tools = KnowledgeTools(args.documents, fail_tool=args.fail_tool)
    result = run_agent(args.question, model, tools, history=history, max_steps=args.max_steps)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
