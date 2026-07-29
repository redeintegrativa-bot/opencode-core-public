# Knowledge Store — JSONL Project Memory

Persistent knowledge across sessions. Structured JSONL storage with tagging and full-text search.

## Quick Start

```bash
# Save an architecture decision
python knowledge_store.py add adr "Use PostgreSQL" "Decision: migrate from SQLite for horizontal scaling"

# Search past decisions
python knowledge_store.py search "postgres" --tags adr

# Log an API endpoint
python knowledge_store.py add api "/users/create" "POST /users — creates user account" --tags auth

# View stats
python knowledge_store.py stats

# List all corpora
python knowledge_store.py corpora
```

## Integration

Agents access the store via CLI. The orchestrator references it in `orchestrator.md` Knowledge Store section.

## Storage

All data lives in `knowledge/store/{corpus_id}.jsonl` with an `INDEX.json` registry.
