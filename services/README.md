# opencode-core/services

Decoupled services extracted from `opencode-crypto-platform`. No internal `backend.*` imports — all dependencies are injected via `configure()`.

## Usage

```python
from opencode_core.services import configure_ranking, configure_feedback

# Provide your DB layer
import sqlite3
conn = sqlite3.connect("crypto.db")
conn.row_factory = sqlite3.Row

configure_ranking(conn_fn=lambda: conn)
configure_feedback(conn_fn=lambda: conn)

# Now use the services
from opencode_core.services.ranking_engine import score_all_opportunities
count = score_all_opportunities()
```

## Files

| File | Purpose |
|------|---------|
| `ranking_engine.py` | Scores opportunities with confidence/risk metrics |
| `feedback_learning.py` | User feedback, topic weights, source trust, narratives |
| `__init__.py` | Package exports with convenience `configure_*` wrappers |
