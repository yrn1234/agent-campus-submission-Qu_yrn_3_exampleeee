"""Bounded model -> tool -> observation loop and citation validation."""


def run_agent(question, model, tools, history=None, max_steps=8):
    messages = [{"role": "user", "question": question, "history": history or []}]
    trace = []
    read_docs = {}
    if not question.strip():
        return {"status": "insufficient_information", "answer": "请提供问题。", "citations": [],
                "missing_information": "问题", "trace": trace}
    for step in range(1, max_steps + 1):
        action = "model"
        parameters = {}
        reason = ""
        decision = {}
        try:
            decision = model.decide(messages)
            action = decision["action"]
            reason = decision.get("reason", "")
            if action == "finish":
                status = decision.get("status", "invalid_answer")
                citations = decision.get("citations", [])
                valid_statuses = {"answered", "needs_clarification", "insufficient_information", "tool_error"}
                valid = status in valid_statuses and isinstance(citations, list)
                if valid:
                    for citation in citations:
                        doc = read_docs.get(citation.get("doc_id"))
                        if not doc or not citation.get("quote") or citation["quote"] not in doc["text"]:
                            valid = False
                            break
                if status == "answered" and not citations:
                    valid = False
                # A final answer must account for every document returned by the last search.
                searches = [m for m in messages if m.get("role") == "tool" and m.get("action") == "search"]
                if status == "answered" and searches:
                    hit_ids = {h["doc_id"] for h in searches[-1]["result"].get("hits", [])}
                    if not hit_ids.issubset(set(read_docs)):
                        valid = False
                if not valid:
                    status = "invalid_answer"
                    decision = {"answer": "模型输出未通过引用校验。", "citations": [],
                                "missing_information": "需要可核实的原文引用"}
                trace.append({"step": step, "action": "finish", "parameters": {}, "result": status,
                              "reason": reason})
                return {"status": status, "answer": decision.get("answer", ""),
                        "citations": decision.get("citations", []),
                        "missing_information": decision.get("missing_information", ""), "trace": trace}
            if action == "search":
                parameters = {"query": decision["query"]}
                result = {"hits": tools.search(**parameters)}
            elif action == "read":
                parameters = {"doc_id": decision["doc_id"]}
                result = tools.read(**parameters)
                read_docs[result["doc_id"]] = result
            else:
                raise ValueError("unsupported action: " + str(action))
        except Exception as exc:
            result = {"error": str(exc)}
        trace.append({"step": step, "action": action, "parameters": parameters,
                      "result": result, "reason": reason})
        if action == "model":
            return {"status": "tool_error", "answer": "模型接口调用失败，无法核实答案。",
                    "citations": [], "missing_information": str(result["error"]), "trace": trace}
        messages.append({"role": "assistant", "decision": decision})
        messages.append({"role": "tool", "action": action, "result": result})
    return {"status": "incomplete_step_limit", "answer": "达到执行步数上限，未完成核实。",
            "citations": [], "missing_information": "需要继续执行", "trace": trace}
