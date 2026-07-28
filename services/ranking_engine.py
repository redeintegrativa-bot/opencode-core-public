import json
import math

_DEFAULT_SCORING_WEIGHTS = {
    "liquidity": 0.15,
    "volume": 0.15,
    "tvl": 0.20,
    "apy": 0.10,
    "narrative": 0.10,
    "risk": 0.15,
    "feedback": 0.15,
}

get_conn = None
row_to_dict = lambda row: dict(row) if row else {}
rows_to_list = lambda rows: [dict(r) for r in rows]
SCORING_WEIGHTS = dict(_DEFAULT_SCORING_WEIGHTS)


def configure(conn_fn, row_to_dict_fn=None, rows_to_list_fn=None, scoring_weights=None):
    global get_conn, row_to_dict, rows_to_list, SCORING_WEIGHTS
    get_conn = conn_fn
    if row_to_dict_fn:
        row_to_dict = row_to_dict_fn
    if rows_to_list_fn:
        rows_to_list = rows_to_list_fn
    if scoring_weights:
        SCORING_WEIGHTS = scoring_weights


def score_all_opportunities():
    profile = _get_profile()
    topic_weights = _get_topic_weights()
    narrative_scores = _get_narrative_scores()

    with get_conn() as conn:
        opps = [dict(r) for r in conn.execute("SELECT * FROM opportunities").fetchall()]

    for opp in opps:
        result = _score_single(opp, profile, topic_weights, narrative_scores)
        opp["confidence"] = result["confidence"]
        opp["risk_score"] = result["risk"]
        opp["reasons"] = result["reasons"]
        opp["explanation"] = result["explanation"]

        with get_conn() as conn:
            conn.execute("""
                UPDATE opportunities SET confidence=?, risk_score=?, reasons=?, explanation=?,
                       updated_at=datetime('now') WHERE id=?
            """, (
                result["confidence"], result["risk"],
                json.dumps(result["reasons"]), result["explanation"],
                opp["id"]
            ))

    return len(opps)


def _score_single(opp, profile, topic_weights, narrative_scores):
    tvl = opp.get("tvl", 0) or 0
    volume = opp.get("volume_24h", 0) or 0
    liquidity = opp.get("liquidity", 0) or 0
    apy = opp.get("apy", 0) or 0

    pref_chains = json.loads(profile.get("preferred_chains", "[]"))
    pref_narratives = json.loads(profile.get("preferred_narratives", "[]"))
    risk_tolerance = profile.get("risk_tolerance", "moderado")
    max_risk = profile.get("max_risk", 0.7)

    W = SCORING_WEIGHTS

    liq_score = _log_scale(liquidity, 50_000_000)
    vol_score = _log_scale(volume, 100_000_000)
    tvl_score = _log_scale(tvl, 5_000_000_000)
    apy_score = min(apy / 30, 1.0) if apy > 0 else 0

    opp_narratives = opp.get("narrative", [])
    if isinstance(opp_narratives, str):
        try:
            opp_narratives = json.loads(opp_narratives)
        except (json.JSONDecodeError, TypeError):
            opp_narratives = []
    narr_match = len(set(opp_narratives) & set(pref_narratives)) / max(len(pref_narratives), 1)
    narr_bonus = 0
    for n in opp_narratives:
        if n in narrative_scores:
            narr_bonus += narrative_scores[n]["score"] * 0.1
    narrative_score = min(narr_match + narr_bonus, 1.0)

    risk = 0.2
    risk_factors = []

    if liquidity < 5_000_000:
        risk += 0.25
        risk_factors.append("Liquidez muito baixa - alto risco de slippage em operacoes grandes")
    elif liquidity < 20_000_000:
        risk += 0.10
        risk_factors.append("Liquidez moderada - adequada para posicoes menores")

    if apy > 50:
        risk += 0.20
        risk_factors.append(f"APY extremamente alto ({apy:.1f}%) - pode indicar risco elevado ou incentivacao temporaria")
    elif apy > 25:
        risk += 0.08
        risk_factors.append(f"APY alto ({apy:.1f}%) - yield atrativo mas verifique a sustentabilidade")

    meta = opp.get("metadata", {})
    if isinstance(meta, str):
        try:
            meta = json.loads(meta)
        except (json.JSONDecodeError, TypeError):
            meta = {}

    if not meta.get("audited"):
        risk += 0.12
        risk_factors.append("Protocolo nao possui auditoria publica conhecida")

    if meta.get("buys_24h", 0) and meta.get("sells_24h", 0):
        buy_sell = meta["buys_24h"] / max(meta["sells_24h"], 1)
        if buy_sell < 0.5:
            risk += 0.10
            risk_factors.append("Pressao vendedora forte - vendas superam compras nas ultimas 24h")

    if opp.get("chain", "") not in pref_chains:
        risk += 0.05
        risk_factors.append(f"Rede {opp.get('chain')} nao esta nas suas redes preferidas")

    risk = round(min(risk, 0.95), 2)

    chain_bonus = 0.12 if opp.get("chain") in pref_chains else 0
    audit_bonus = 0.08 if meta.get("audited") else 0
    bounty_bonus = 0.04 if meta.get("bug_bounty") else 0
    fee_bonus = 0.05 if (opp.get("fees_24h", 0) or 0) > 1_000_000 else 0

    fb_score = _get_feedback_boost(opp.get("id", ""), topic_weights)

    confidence = (
        liq_score * W["liquidity"] +
        vol_score * W["volume"] +
        tvl_score * W["tvl"] +
        apy_score * W["apy"] +
        narrative_score * W["narrative"] +
        (1 - risk) * W["risk"] +
        fb_score * W["feedback"] +
        chain_bonus + audit_bonus + bounty_bonus + fee_bonus
    )
    confidence = round(min(max(confidence, 0.05), 0.98), 2)

    reasons = _build_reasons(opp, confidence, risk, liq_score, vol_score,
                             tvl_score, apy_score, narrative_score, risk_factors,
                             meta, chain_bonus, audit_bonus, bounty_bonus, fb_score)

    explanation = _build_explanation(opp, confidence, risk, reasons, tvl, volume, liquidity, apy)

    return {
        "confidence": confidence,
        "risk": risk,
        "reasons": reasons,
        "explanation": explanation
    }


def _log_scale(value, max_ref):
    if value <= 0:
        return 0
    log_val = math.log10(max(value, 1))
    log_max = math.log10(max(max_ref, 1))
    return min(log_val / log_max, 1.0)


def _get_profile():
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM user_profile WHERE id = 1").fetchone()
    return row_to_dict(row) if row else {
        "risk_tolerance": "moderado",
        "preferred_chains": '["ethereum","arbitrum","base","solana"]',
        "preferred_narratives": '["DeFi","RWA","AI","L2","Restaking"]',
        "max_risk": 0.7
    }


def _get_topic_weights():
    with get_conn() as conn:
        rows = conn.execute("SELECT topic, weight FROM topic_weights").fetchall()
    return {r["topic"]: r["weight"] for r in rows}


def _get_narrative_scores():
    with get_conn() as conn:
        rows = conn.execute("SELECT narrative, score FROM narrative_scores").fetchall()
    return {r["narrative"]: {"score": r["score"]} for r in rows}


def _get_feedback_boost(opp_id, topic_weights):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT reaction FROM feedback WHERE item_id = ? AND item_type = 'opportunity'",
            (opp_id,)
        ).fetchall()

    if not rows:
        return 0.5

    reactions = [r["reaction"] for r in rows]
    pos = reactions.count("boa") + reactions.count("quero_mais") * 1.5
    neg = reactions.count("ruim") + reactions.count("nao_quero") * 1.5
    total = pos + neg

    if total == 0:
        return 0.5

    return min(max((pos - neg) / total * 0.5 + 0.5, 0.1), 0.95)


def _fmt(n):
    if n >= 1e9: return f"${n/1e9:.1f}B"
    if n >= 1e6: return f"${n/1e6:.0f}M"
    if n >= 1e3: return f"${n/1e3:.0f}K"
    return f"${n:.0f}"


def _build_reasons(opp, confidence, risk, liq_s, vol_s, tvl_s, apy_s,
                    narr_s, risk_factors, meta, chain_b, audit_b, bounty_b, fb_s):
    reasons = []

    if confidence > 0.7:
        reasons.append("Oportunidade bem ranqueada com metricas solidas no mercado")
    elif confidence > 0.5:
        reasons.append("Score moderado - apresenta bons indicadores gerais")
    elif confidence < 0.3:
        reasons.append("Score baixo - metricas insuficientes ou alto risco identificado")

    tvl = opp.get("tvl", 0) or 0
    if tvl > 5_000_000_000:
        reasons.append(f"TVL excepcionalmente alto ({_fmt(tvl)}) - indica forte adocao e confianca do mercado")
    elif tvl > 1_000_000_000:
        reasons.append(f"TVL solido ({_fmt(tvl)}) - protocolo maduro com boa liquidez")
    elif tvl > 100_000_000:
        reasons.append(f"TVL razoavel ({_fmt(tvl)}) - crescimento positivo")
    elif tvl > 10_000_000:
        reasons.append(f"TVL baixo ({_fmt(tvl)}) - protocolo em fase inicial")
    elif tvl > 0:
        reasons.append(f"TVL muito baixo ({_fmt(tvl)}) - alto risco de inexistencia de liquidez")

    vol = opp.get("volume_24h", 0) or 0
    if vol > 500_000_000:
        reasons.append(f"Volume de negociacao excepcional ({_fmt(vol)}/dia) - alta atividade de mercado")
    elif vol > 50_000_000:
        reasons.append(f"Volume saudavel ({_fmt(vol)}/dia) - liquidez ativa")
    elif vol > 5_000_000:
        reasons.append(f"Volume moderado ({_fmt(vol)}/dia)")
    elif vol > 0:
        reasons.append(f"Volume baixo ({_fmt(vol)}/dia) - pode ter slippage significativo")

    liq = opp.get("liquidity", 0) or 0
    if liq > 100_000_000:
        reasons.append("Liquidez profunda - execucoes com baixo impacto no preco")
    elif liq > 20_000_000:
        reasons.append("Liquidez adequada para a maioria das operacoes")
    elif liq > 5_000_000:
        reasons.append("Liquidez limitada - cuidado com posicoes grandes")

    apy = opp.get("apy", 0) or 0
    if apy > 20:
        reasons.append(f"Yield muito atrativo ({apy:.1f}%) - verifique se e sustentavel")
    elif apy > 10:
        reasons.append(f"Yield interessante ({apy:.1f}%) - acima da media do mercado")
    elif apy > 0:
        reasons.append(f"Yield conservador ({apy:.1f}%) - prioriza seguranca")

    if audit_b > 0:
        reasons.append("Contrato auditado por firma especializada - maior seguranca")
    if bounty_b > 0:
        reasons.append("Programa de bug bounty ativo - incentiva descoberta e correcao de vulnerabilidades")
    if chain_b > 0:
        reasons.append(f"Disponivel na rede {opp.get('chain')} - esta nas suas redes preferidas")

    if fb_s > 0.6:
        reasons.append("Feedback positivo dos usuarios que ja interagiram com este protocolo")
    elif fb_s < 0.4:
        reasons.append("Feedback negativo - usuarios reportaram problemas")

    reasons.extend(risk_factors[:3])

    return reasons[:8]


def _build_explanation(opp, confidence, risk, reasons, tvl, volume, liquidity, apy):
    name = opp.get("name", "Protocolo")
    chain = opp.get("chain", "")
    category = opp.get("category", "")

    risk_label = "baixo" if risk < 0.35 else "moderado" if risk < 0.6 else "alto"
    conf_label = "forte" if confidence > 0.7 else "moderado" if confidence > 0.4 else "fraco"

    positive = [r for r in reasons if not any(w in r.lower() for w in ["baixa", "alto", "fora", "vendas", "nao", "negativo", "limitada", "muito baixo"])][:2]
    negative = [r for r in reasons if any(w in r.lower() for w in ["baixa", "alto", "fora", "vendas", "nao", "negativo", "limitada", "muito baixo"])][:1]

    parts = []

    parts.append(f"{name} ({chain}) apresenta confianca {conf_label} com score de {confidence:.0%} e risco {risk_label} avaliado em {risk:.0%}.")

    metrics = []
    if tvl > 0: metrics.append(f"TVL de {_fmt(tvl)}")
    if volume > 0: metrics.append(f"volume diario de {_fmt(volume)}")
    if liquidity > 0: metrics.append(f"liquidez de {_fmt(liquidity)}")
    if apy > 0: metrics.append(f"APY de {apy:.1f}%")
    if metrics:
        parts.append(f"Indicadores: {'; '.join(metrics)}.")

    if positive:
        parts.append("Pontos favoraveis: " + "; ".join(positive) + ".")
    if negative:
        parts.append("Pontos de atencao: " + "; ".join(negative) + ".")

    parts.append("Esta analise e automatizada - sempre faca sua propria pesquisa (DYOR) antes de investir.")

    return " ".join(parts)
