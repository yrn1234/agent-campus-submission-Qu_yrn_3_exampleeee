"""Live model adapter and a clearly limited offline decision policy."""
import json
import os
import subprocess
import tempfile
import urllib.request
from pathlib import Path


SYSTEM = """你是企业知识问答 Agent。每步只输出一个 JSON 对象。
可用动作：search(query), read(doc_id), finish(status, answer, citations, missing_information)。
status 只可为 answered, needs_clarification, insufficient_information, tool_error。
先检索再读取原文。只据已读取文档回答；引用格式为 {doc_id, quote}，quote 必须是原文的连续片段。
发现冲突时列出两边原文并请求确认适用制度，不要擅选。无资料、工具失败时说明缺口。
每个动作附简短 reason（行动依据，不是内部推理）。不要输出 Markdown。"""


class LiveModel:
    def __init__(self, model=None, base_url=None, api_key=None):
        self.model = model or os.environ.get("MODEL_NAME", "gpt-4o-mini")
        self.base_url = (base_url or os.environ.get("MODEL_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.api_key = api_key or os.environ.get("MODEL_API_KEY", "")
        if not self.api_key:
            raise ValueError("MODEL_API_KEY is required for live mode")

    def decide(self, messages):
        payload = {"model": self.model, "temperature": 0,
                   "messages": [{"role": "system", "content": SYSTEM}] +
                   [{"role": "user", "content": json.dumps(m, ensure_ascii=False)} for m in messages],
                   "response_format": {"type": "json_object"}}
        request = urllib.request.Request(
            self.base_url + "/chat/completions",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Authorization": "Bearer " + self.api_key, "Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.load(response)
        return json.loads(body["choices"][0]["message"]["content"])


class CodexCLIModel:
    """Use an authenticated Codex CLI call for each model decision, without an API key."""
    def __init__(self, model=None, runner=None):
        self.model = model or os.environ.get("CODEX_MODEL", "gpt-6-sol")
        self.runner = runner or subprocess.run

    def decide(self, messages):
        prompt = (SYSTEM + "\n只依据下列当前可见交互选择一个动作；不得访问本地文件或调用其他工具。"
                  "只输出 JSON 对象。\n交互：" + json.dumps(messages, ensure_ascii=False))
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "decision.json"
            args = ["codex", "exec", "--model", self.model, "--sandbox", "read-only",
                    "--ephemeral", "--skip-git-repo-check", "-o", str(output), "-"]
            completed = self.runner(args, input=prompt, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, encoding="utf-8", timeout=180,
                                    env=os.environ.copy(), cwd=directory)
            if completed.returncode != 0 or not output.exists():
                # Stderr may contain account or network details; do not put it in a trace.
                raise RuntimeError("Codex CLI model call failed")
            return json.loads(output.read_text(encoding="utf-8"))


class MockModel:
    """Observation-driven demo policy; does not establish model decision quality."""
    def decide(self, messages):
        user = messages[0]
        observations = [m for m in messages if m.get("role") == "tool"]
        if not observations:
            question = user["question"]
            if user.get("history") and ("它" in question or "还" in question):
                question = " ".join(m.get("content", "") for m in user["history"][-2:]) + " " + question
            return {"action": "search", "query": question, "reason": "先定位可能相关的制度"}
        last = observations[-1]
        if "error" in last["result"]:
            return {"action": "finish", "status": "tool_error", "answer": "知识工具调用失败，无法核实答案。",
                    "citations": [], "missing_information": last["action"] + ": " + last["result"]["error"],
                    "reason": "工具错误后停止，避免猜测"}
        searches = [m for m in observations if m["action"] == "search"]
        reads = [m["result"] for m in observations if m["action"] == "read"]
        hits = searches[-1]["result"].get("hits", []) if searches else []
        if not hits:
            if len(searches) == 1:
                return {"action": "search", "query": user["question"] + " 制度 规定",
                        "reason": "首次无结果，扩大查询一次"}
            return {"action": "finish", "status": "insufficient_information", "answer": "未检索到支持该问题的资料。",
                    "citations": [], "missing_information": "需要相关制度或 FAQ", "reason": "补充检索仍无结果"}
        read_ids = {r["doc_id"] for r in reads}
        for hit in hits:
            if hit["doc_id"] not in read_ids:
                return {"action": "read", "doc_id": hit["doc_id"], "reason": "读取命中文档的原文以核对答案"}
        citations = [{"doc_id": r["doc_id"], "quote": r["text"]} for r in reads]
        if len({r["text"] for r in reads}) > 1 and len({r["topic"] for r in reads}) == 1:
            return {"action": "finish", "status": "needs_clarification",
                    "answer": "资料存在冲突：" + "；".join(r["doc_id"] + "：" + r["text"].rstrip("。") for r in reads) + "。请确认适用制度。",
                    "citations": citations, "missing_information": "文档适用范围或优先级",
                    "reason": "同一主题的已读原文不同，不能擅自选定"}
        return {"action": "finish", "status": "answered", "answer": "根据 " + reads[0]["doc_id"] + "：" + reads[0]["text"],
                "citations": citations, "missing_information": "", "reason": "原文足以支持回答"}
