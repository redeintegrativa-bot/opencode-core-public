#!/usr/bin/env python3
"""Knowledge Store — JSONL-based persistent project knowledge.

Stores structured knowledge entries (facts, decisions, patterns, docs)
as a JSONL corpus with tagging, full-text search, and source tracking.
Designed for CLI and agent consumption.
"""

import json
import os
import sys
import uuid
import argparse
import logging
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("knowledge_store")


class KnowledgeStore:
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.store_dir = os.path.join(project_root, "knowledge", "store")
        self.index_path = os.path.join(self.store_dir, "INDEX.json")
        os.makedirs(self.store_dir, exist_ok=True)
        self._ensure_index()

    def _ensure_index(self):
        if not os.path.isfile(self.index_path):
            with open(self.index_path, "w") as f:
                json.dump({"corpora": [], "created": datetime.now().isoformat()}, f, indent=2)

    def _load_index(self) -> Dict:
        with open(self.index_path) as f:
            return json.load(f)

    def _save_index(self, index: Dict):
        with open(self.index_path, "w") as f:
            json.dump(index, f, indent=2)

    def create_corpus(self, name: str, description: str = "", tags: Optional[List[str]] = None) -> str:
        corpus_id = str(uuid.uuid4())[:8]
        path = os.path.join(self.store_dir, f"{corpus_id}.jsonl")
        index = self._load_index()
        entry = {
            "id": corpus_id,
            "name": name,
            "description": description,
            "tags": tags or [],
            "path": path,
            "created": datetime.now().isoformat(),
            "entry_count": 0,
        }
        index["corpora"].append(entry)
        self._save_index(index)
        with open(path, "w") as f:
            pass
        logger.info("Created corpus '%s' (%s)", name, corpus_id)
        return corpus_id

    def add_entry(self, corpus_id: str, content: Dict, tags: Optional[List[str]] = None, source: str = "") -> str:
        index = self._load_index()
        corpus = next((c for c in index["corpora"] if c["id"] == corpus_id), None)
        if not corpus:
            raise ValueError(f"Corpus {corpus_id} not found")
        entry_id = str(uuid.uuid4())[:12]
        entry = {
            "id": entry_id,
            "content": content,
            "tags": tags or [],
            "source": source,
            "timestamp": datetime.now().isoformat(),
        }
        path = corpus["path"]
        with open(path, "a") as f:
            f.write(json.dumps(entry) + "\n")
        corpus["entry_count"] += 1
        self._save_index(index)
        return entry_id

    def search(self, query: str, corpus_id: Optional[str] = None, tags: Optional[List[str]] = None, top: int = 20) -> List[Dict]:
        query_lower = query.lower()
        target_tags = set(t.lower() for t in (tags or []))
        results: List[Dict] = []

        index = self._load_index()
        for corpus in index["corpora"]:
            if corpus_id and corpus["id"] != corpus_id:
                continue
            path = corpus["path"]
            if not os.path.isfile(path):
                continue
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if target_tags:
                        entry_tags = set(t.lower() for t in entry.get("tags", []))
                        if not target_tags & entry_tags:
                            continue
                    text = json.dumps(entry.get("content", {})).lower()
                    if query and query_lower not in text:
                        continue
                    results.append({
                        "corpus_id": corpus["id"],
                        "corpus_name": corpus["name"],
                        "entry_id": entry["id"],
                        "content": entry["content"],
                        "tags": entry.get("tags", []),
                        "source": entry.get("source", ""),
                        "timestamp": entry.get("timestamp", ""),
                    })
        results.sort(key=lambda r: r.get("timestamp", ""), reverse=True)
        return results[:top]

    def get_corpus_stats(self) -> Dict:
        index = self._load_index()
        total_entries = sum(c["entry_count"] for c in index["corpora"])
        return {
            "total_corpora": len(index["corpora"]),
            "total_entries": total_entries,
            "corpora": [
                {"id": c["id"], "name": c["name"], "entries": c["entry_count"], "tags": c["tags"]}
                for c in index["corpora"]
            ],
        }

    def add_decision(self, title: str, context: str, decision: str, consequences: str, tags: Optional[List[str]] = None):
        corpus_id = self._ensure_corpus("architecture-decisions", "Architecture Decision Records")
        entry = {
            "type": "adr",
            "title": title,
            "context": context,
            "decision": decision,
            "consequences": consequences,
        }
        return self.add_entry(corpus_id, entry, tags=(tags or []) + ["adr", "decision"], source="agent")

    def add_api_doc(self, service: str, endpoint: str, method: str, description: str, request: Dict, response: Dict):
        corpus_id = self._ensure_corpus("api-docs", "API Documentation")
        entry = {
            "type": "api",
            "service": service,
            "endpoint": endpoint,
            "method": method,
            "description": description,
            "request": request,
            "response": response,
        }
        return self.add_entry(corpus_id, entry, tags=["api", service, method.lower()], source="agent")

    def add_pattern(self, name: str, problem: str, solution: str, example: str, tags: Optional[List[str]] = None):
        corpus_id = self._ensure_corpus("patterns", "Reusable Patterns")
        entry = {
            "type": "pattern",
            "name": name,
            "problem": problem,
            "solution": solution,
            "example": example,
        }
        return self.add_entry(corpus_id, entry, tags=(tags or []) + ["pattern"], source="agent")

    def _ensure_corpus(self, name: str, description: str) -> str:
        index = self._load_index()
        existing = next((c for c in index["corpora"] if c["name"] == name), None)
        if existing:
            return existing["id"]
        return self.create_corpus(name, description)

    def list_corpora(self) -> List[Dict]:
        return self._load_index()["corpora"]


def cli_add(args):
    store = KnowledgeStore(args.root)
    tags = args.tags.split(",") if args.tags else []
    if args.type == "fact":
        content = {"text": args.content}
        if args.title:
            content["title"] = args.title
    elif args.type == "adr":
        return store.add_decision(args.title, args.content, "N/A", "N/A", tags)
    elif args.type == "api":
        return store.add_api_doc(args.title, args.content, "GET", "", {}, {})
    else:
        content = {"text": args.content}
    entry_id = store.add_entry("_auto", content, tags, source="cli")
    print(json.dumps({"entry_id": entry_id}))


def cli_search(args):
    store = KnowledgeStore(args.root)
    tags = args.tags.split(",") if args.tags else None
    results = store.search(args.query, args.corpus, tags, args.top)
    if not results:
        print("No results found.")
        return
    print(f"Found {len(results)} result(s):\n")
    for r in results:
        print(f"[{r['corpus_name']}] {json.dumps(r['content'], indent=2)}")
        print(f"  tags={r['tags']} source={r['source']} [{r['timestamp']}]\n")


def cli_stats(args):
    store = KnowledgeStore(args.root)
    stats = store.get_corpus_stats()
    print("=== Knowledge Store Statistics ===")
    print(f"  Total corpora:  {stats['total_corpora']}")
    print(f"  Total entries:  {stats['total_entries']}")
    for c in stats["corpora"]:
        print(f"    {c['name']:30} {c['entries']:4d} entries  tags={c['tags']}")


def cli_corpora(args):
    store = KnowledgeStore(args.root)
    corpora = store.list_corpora()
    if not corpora:
        print("No corpora found.")
        return
    print(f"{'ID':10} {'Name':30} {'Entries':8} Tags")
    print("-" * 70)
    for c in corpora:
        print(f"{c['id']:10} {c['name']:30} {c['entry_count']:<8} {','.join(c['tags'])}")


def cli_create(args):
    store = KnowledgeStore(args.root)
    corpus_id = store.create_corpus(args.name, args.description)
    print(json.dumps({"corpus_id": corpus_id}))


def main():
    parser = argparse.ArgumentParser(description="Knowledge Store — JSONL Project Memory")
    parser.add_argument("--root", default=os.getcwd(), help="Project root")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("add")
    p.add_argument("type", choices=["fact", "adr", "api", "pattern"])
    p.add_argument("title", nargs="?", default="")
    p.add_argument("content")
    p.add_argument("--tags")
    p.set_defaults(func=cli_add)

    p = sub.add_parser("search")
    p.add_argument("query", nargs="?", default="")
    p.add_argument("--corpus")
    p.add_argument("--tags")
    p.add_argument("--top", type=int, default=20)
    p.set_defaults(func=cli_search)

    p = sub.add_parser("stats")
    p.set_defaults(func=cli_stats)

    p = sub.add_parser("corpora")
    p.set_defaults(func=cli_corpora)

    p = sub.add_parser("create")
    p.add_argument("name")
    p.add_argument("--description", default="")
    p.set_defaults(func=cli_create)

    args = parser.parse_args()
    try:
        return args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
