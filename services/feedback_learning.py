import json

get_conn = None
row_to_dict = lambda row: dict(row) if row else {}
rows_to_list = lambda rows: [dict(r) for r in rows]


def configure(conn_fn, row_to_dict_fn=None, rows_to_list_fn=None):
    global get_conn, row_to_dict, rows_to_list
    get_conn = conn_fn
    if row_to_dict_fn:
        row_to_dict = row_to_dict_fn
    if rows_to_list_fn:
        rows_to_list = rows_to_list_fn


def submit_feedback(item_id, item_type, reaction):
    valid = ["boa", "ruim", "quero_mais", "nao_quero"]
    if reaction not in valid:
        return None

    with get_conn() as conn:
        conn.execute(
            "INSERT INTO feedback (item_id, item_type, reaction) VALUES (?, ?, ?)",
            (item_id, item_type, reaction)
        )
        _update_topic_weights(conn, item_id, item_type, reaction)
        _update_source_trust(conn, item_id, item_type, reaction)
        _update_narrative_scores(conn, item_id, item_type, reaction)
        _log_history(conn, "feedback", item_id, item_type, {"reaction": reaction})

    return {"status": "ok", "item_id": item_id, "reaction": reaction}


def _update_topic_weights(conn, item_id, item_type, reaction):
    if item_type != "news":
        return
    row = conn.execute("SELECT topics FROM news WHERE id = ?", (item_id,)).fetchone()
    if not row:
        return
    topics = json.loads(row["topics"])

    delta = {"boa": 0.10, "quero_mais": 0.15, "ruim": -0.10, "nao_quero": -0.20}.get(reaction, 0)

    for topic in topics:
        existing = conn.execute(
            "SELECT weight, feedback_count FROM topic_weights WHERE topic = ?", (topic,)
        ).fetchone()
        if existing:
            new_w = max(0.1, min(3.0, existing["weight"] + delta))
            conn.execute(
                "UPDATE topic_weights SET weight=?, feedback_count=feedback_count+1, updated_at=datetime('now') WHERE topic=?",
                (new_w, topic)
            )
        else:
            conn.execute(
                "INSERT INTO topic_weights (topic, weight, feedback_count) VALUES (?, ?, 1)",
                (topic, 1.0 + delta)
            )


def _update_source_trust(conn, item_id, item_type, reaction):
    if item_type != "news":
        return
    row = conn.execute("SELECT source FROM news WHERE id = ?", (item_id,)).fetchone()
    if not row:
        return
    source = row["source"]

    delta = {"boa": 1, "quero_mais": 1, "ruim": -1, "nao_quero": -1}.get(reaction, 0)
    existing = conn.execute(
        "SELECT trust_score, positive_feedback, negative_feedback FROM source_trust WHERE source = ?",
        (source,)
    ).fetchone()

    if existing:
        pos = existing["positive_feedback"] + (1 if delta > 0 else 0)
        neg = existing["negative_feedback"] + (1 if delta < 0 else 0)
        total = pos + neg
        new_score = pos / total if total > 0 else 0.5
        conn.execute(
            "UPDATE source_trust SET trust_score=?, positive_feedback=?, negative_feedback=?, article_count=article_count+1, updated_at=datetime('now') WHERE source=?",
            (new_score, pos, neg, source)
        )
    else:
        conn.execute(
            "INSERT INTO source_trust (source, trust_score, article_count, positive_feedback, negative_feedback) VALUES (?, ?, 1, ?, ?)",
            (source, 0.5 + delta * 0.1, 1 if delta > 0 else 0, 1 if delta < 0 else 0)
        )


def _update_narrative_scores(conn, item_id, item_type, reaction):
    if item_type != "news":
        return
    row = conn.execute("SELECT narrative FROM news WHERE id = ?", (item_id,)).fetchone()
    if not row or not row["narrative"]:
        return
    narrative = row["narrative"]

    delta = {"boa": 0.08, "quero_mais": 0.12, "ruim": -0.08, "nao_quero": -0.15}.get(reaction, 0)

    existing = conn.execute(
        "SELECT score, mention_count FROM narrative_scores WHERE narrative = ?", (narrative,)
    ).fetchone()

    if existing:
        new_score = max(0.1, min(2.0, existing["score"] + delta))
        conn.execute(
            "UPDATE narrative_scores SET score=?, mention_count=mention_count+1, updated_at=datetime('now') WHERE narrative=?",
            (new_score, narrative)
        )
    else:
        conn.execute(
            "INSERT INTO narrative_scores (narrative, score, mention_count) VALUES (?, ?, 1)",
            (narrative, 1.0 + delta)
        )


def _log_history(conn, action, item_id, item_type, details):
    conn.execute(
        "INSERT INTO history (action, item_id, item_type, details) VALUES (?, ?, ?, ?)",
        (action, item_id, item_type, json.dumps(details))
    )


def get_topic_weights():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT topic, weight, feedback_count FROM topic_weights ORDER BY weight DESC"
        ).fetchall()
    return rows_to_list(rows)


def get_source_trust():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT source, trust_score, article_count, positive_feedback, negative_feedback FROM source_trust ORDER BY trust_score DESC"
        ).fetchall()
    return rows_to_list(rows)


def get_narrative_scores():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT narrative, score, mention_count FROM narrative_scores ORDER BY score DESC"
        ).fetchall()
    return rows_to_list(rows)


def get_feedback_stats():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT reaction, item_type, COUNT(*) as c FROM feedback GROUP BY reaction, item_type"
        ).fetchall()
    stats = {"total": 0, "by_reaction": {}, "by_type": {}}
    for r in rows:
        stats["total"] += r["c"]
        stats["by_reaction"][r["reaction"]] = stats["by_reaction"].get(r["reaction"], 0) + r["c"]
        stats["by_type"][r["item_type"]] = stats["by_type"].get(r["item_type"], 0) + r["c"]
    return stats


def get_user_profile():
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM user_profile WHERE id = 1").fetchone()
    if row:
        return row_to_dict(row)
    _init_profile()
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM user_profile WHERE id = 1").fetchone()
    return row_to_dict(row)


def update_profile(data):
    current = get_user_profile()
    risk = data.get("risk_tolerance", current["risk_tolerance"])
    chains = json.dumps(data.get("preferred_chains", json.loads(current["preferred_chains"])))
    narratives = json.dumps(data.get("preferred_narratives", json.loads(current["preferred_narratives"])))
    categories = json.dumps(data.get("preferred_categories", json.loads(current.get("preferred_categories", "[]"))))
    min_conf = data.get("min_confidence", current["min_confidence"])
    min_liq = data.get("min_liquidity", current["min_liquidity"])
    min_tvl = data.get("min_tvl", current.get("min_tvl", 100000))
    max_risk = data.get("max_risk", current.get("max_risk", 0.7))

    with get_conn() as conn:
        conn.execute("""
            UPDATE user_profile SET
                risk_tolerance=?, preferred_chains=?, preferred_narratives=?,
                preferred_categories=?, min_confidence=?, min_liquidity=?,
                min_tvl=?, max_risk=?, updated_at=datetime('now')
            WHERE id=1
        """, (risk, chains, narratives, categories, min_conf, min_liq, min_tvl, max_risk))
    return get_user_profile()


def get_history(limit=50, action=None, item_type=None):
    with get_conn() as conn:
        query = "SELECT * FROM history WHERE 1=1"
        params = []
        if action:
            query += " AND action = ?"
            params.append(action)
        if item_type:
            query += " AND item_type = ?"
            params.append(item_type)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(query, params).fetchall()
    return rows_to_list(rows)


def _init_profile():
    with get_conn() as conn:
        conn.execute("INSERT OR IGNORE INTO user_profile (id) VALUES (1)")
