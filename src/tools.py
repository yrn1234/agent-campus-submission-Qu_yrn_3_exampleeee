"""Small, inspectable local knowledge tools."""
import json


CONCEPTS = {
    "annual_leave": ("年假", "休假", "休年假", "假期"),
    "expense": ("报销", "费用", "发票"),
    "remote": ("远程办公", "居家办公", "远程", "居家"),
}


class KnowledgeTools:
    def __init__(self, path, fail_tool=None):
        with open(str(path), encoding="utf-8") as handle:
            self.documents = json.load(handle)
        self.by_id = {doc["id"]: doc for doc in self.documents}
        self.fail_tool = fail_tool

    def search(self, query):
        if self.fail_tool == "search":
            raise RuntimeError("injected search failure")
        query = query.strip()
        matched = set()
        for concept, terms in CONCEPTS.items():
            if any(term in query for term in terms):
                matched.add(concept)
        # Avoid matching a vague follow-up solely on common words such as 申请.
        return [{"doc_id": d["id"], "title": d["title"], "version_date": d["version_date"]}
                for d in self.documents if d["topic"] in matched]

    def read(self, doc_id):
        if self.fail_tool == "read":
            raise RuntimeError("injected read failure")
        if doc_id not in self.by_id:
            raise KeyError("unknown document: " + doc_id)
        doc = self.by_id[doc_id]
        return {"doc_id": doc["id"], "title": doc["title"],
                "version_date": doc["version_date"], "topic": doc["topic"],
                "text": doc["text"]}
