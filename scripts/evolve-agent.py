#!/usr/bin/env python3
"""
evolve-agent.py — Ciclo de aprendizado: promove, arquiva, mescla agentes.

Uso:
  python scripts/evolve-agent.py --check     # Analisa e sugere acoes
  python scripts/evolve-agent.py --archive <nome>   # Arquiva um agente
  python scripts/evolve-agent.py --promote <nome>   # Promove L2 -> L1
  python scripts/evolve-agent.py --merge <a> <b>    # Mescla dois agentes
  python scripts/evolve-agent.py --status           # Mostra status dos agentes
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path


def get_repo_root() -> Path:
    here = Path(__file__).resolve().parent.parent
    if (here / ".opencode" / "opencode.json").exists():
        return here
    return here


def load_json(path: Path, default=None):
    if not path.exists():
        return default or {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default or {}


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def find_agent_file(repo: Path, name: str):
    for root in [repo / "agents" / "experts" / "L2", repo / "agents" / "experts", repo / "agents" / "core"]:
        if (root / f"{name}.md").exists():
            return root / f"{name}.md"
    return None


def do_check(repo: Path):
    log_path = Path.home() / ".config" / "opencode" / "evolution-log.json"
    fallback_path = Path.home() / ".config" / "opencode" / "fallback-log.json"
    evo = load_json(log_path, {"version": 1, "evolutions": []})
    fallback = load_json(fallback_path, {"version": 1, "entries": []})

    now = datetime.utcnow()
    suggestions = []

    agent_dir = repo / "agents" / "experts"
    l2_dir = repo / "agents" / "experts" / "L2"

    # Built-in agents (shipped with repo) are never auto-archived
    built_in = {
        "ai_integration_expert", "architect_expert", "browser_automation_expert",
        "claude_systems_expert", "database_expert", "devops_expert", "gui-super-expert",
        "integration_expert", "languages_expert", "mcp_integration_expert", "mobile_expert",
        "mql_decompilation_expert", "mql_expert", "n8n_expert", "notification_expert",
        "offensive_security_expert", "payment_integration_expert", "reverse_engineering_expert",
        "security_unified_expert", "social_identity_expert", "tester_expert", "trading_strategy_expert",
        "ai-model-specialist", "api-endpoint-builder", "architect-design-specialist",
        "claude-prompt-optimizer", "db-query-optimizer", "devops-pipeline-specialist",
        "gui-layout-specialist", "languages-refactor-specialist", "mobile-ui-specialist",
        "mql-optimization", "n8n-workflow-builder", "security-auth-specialist",
        "social-oauth-specialist", "test-unit-specialist", "trading-risk-calculator",
    }

    l1_agents = [d.stem for d in agent_dir.glob("*.md")] if agent_dir.exists() else []
    l2_agents = [d.stem for d in l2_dir.glob("*.md")] if l2_dir.exists() else []

    generated_dir = repo / "agents" / "generated"
    generated = [d.stem for d in generated_dir.glob("*.md")] if generated_dir.exists() else []

    evolved_names = {e.get("name") for e in evo.get("evolutions", [])}

    for a in l1_agents + l2_agents + generated:
        if a in built_in or a in evolved_names:
            continue
        use_count = sum(1 for e in fallback.get("entries", []) if a in str(e.get("keywords", [])))
        if use_count == 0:
            suggestions.append({"type": "archive", "name": a, "reason": "Nunca usado (criado ha mais de 30 dias)"})

    for a in l2_agents + generated:
        if a in built_in:
            continue
        use_count = sum(1 for e in fallback.get("entries", []) if a in str(e.get("keywords", [])))
        if use_count >= 10:
            suggestions.append({"type": "promote", "name": a, "reason": f"Usado {use_count}x — candidato a L1 Expert"})

    # Detect keyword overlap for merging
    agent_keywords = {}
    for a in l1_agents + l2_agents + generated:
        f = find_agent_file(repo, a)
        if f:
            text = f.read_text(encoding="utf-8", errors="ignore")
            kw_match = re.search(r"(?i)## Keywords\s*\n\s*(.+)", text)
            if kw_match:
                agent_keywords[a] = set(k.strip().lower() for k in kw_match.group(1).split(","))

    seen = set()
    for a1, kw1 in agent_keywords.items():
        for a2, kw2 in agent_keywords.items():
            if a1 >= a2 or (a1, a2) in seen or (a2, a1) in seen:
                continue
            overlap = kw1 & kw2
            if len(overlap) >= 3:
                seen.add((a1, a2))
                suggestions.append({
                    "type": "merge", "a": a1, "b": a2,
                    "reason": f"Keywords sobrepostas: {', '.join(overlap)}"
                })

    return suggestions


def do_archive(repo: Path, name: str):
    src = find_agent_file(repo, name)
    if not src:
        print(f"  [!] Agente {name} nao encontrado")
        return False

    archive_dir = repo / "agents" / "archived"
    archive_dir.mkdir(parents=True, exist_ok=True)
    dst = archive_dir / f"{name}.md"
    src.rename(dst)
    print(f"  [+] {name} movido para agents/archived/")

    # Remove from routing tables
    for tbl_path in [
        repo / "agents" / "core" / "INDEX.md",
        repo / "agents" / "core" / "orchestrator.md",
        repo / "agents" / "system" / "AGENT_REGISTRY.md",
    ]:
        if tbl_path.exists():
            text = tbl_path.read_text(encoding="utf-8")
            new_text = "\n".join(line for line in text.split("\n") if name not in line)
            if new_text != text:
                tbl_path.write_text(new_text, encoding="utf-8")
                print(f"  [+] {tbl_path.name}: entrada removida")

    return True


def do_promote(repo: Path, name: str):
    src = find_agent_file(repo, name)
    if not src:
        print(f"  [!] Agente {name} nao encontrado")
        return False

    if "L2" not in str(src):
        print(f"  [-] {name} ja e L1 Expert ou Core")
        return False

    dst = repo / "agents" / "experts" / f"{name}.md"
    text = src.read_text(encoding="utf-8")

    # Add L1-level fields if missing
    if "allowed-tools" not in text:
        text = text.replace("---\n", "---\nallowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Task]\n", 1)

    dst.write_text(text, encoding="utf-8")
    src.unlink()
    print(f"  [+] {name} promovido de L2 -> L1 (agents/experts/)")

    # Update orchestrator routing path
    orch_path = repo / "agents" / "core" / "orchestrator.md"
    if orch_path.exists():
        text = orch_path.read_text(encoding="utf-8")
        text = text.replace(f"experts/L2/{name}.md", f"experts/{name}.md")
        orch_path.write_text(text, encoding="utf-8")
        print(f"  [+] orchestrator.md: caminho atualizado para experts/{name}.md")

    return True


def do_merge(repo: Path, a: str, b: str):
    fa = find_agent_file(repo, a)
    fb = find_agent_file(repo, b)
    if not fa or not fb:
        print(f"  [!] Um dos agentes nao encontrado: {a}, {b}")
        return False

    text_a = fa.read_text(encoding="utf-8")
    text_b = fb.read_text(encoding="utf-8")

    merged_name = f"{a.split('-')[0]}-{b.split('-')[0]}-unified"
    merged_text = f"---\nname: {merged_name}\ndescription: Unified agent (merged from {a} + {b})\n---\n\n"
    merged_text += "# " + merged_name.replace("-", " ").title() + "\n\n"
    merged_text += "> Merged from: " + a + " + " + b + "\n\n"

    # Extract behavior sections
    for label, text in [("A", text_a), ("B", text_b)]:
        body = text.split("---\n", 2)[-1] if text.count("---") >= 2 else text
        merged_text += f"## From {label} ({text.split('name:')[1].split()[0] if 'name:' in text else label})\n\n{body.strip()}\n\n"

    dst = repo / "agents" / "experts" / f"{merged_name}.md"
    dst.write_text(merged_text, encoding="utf-8")
    print(f"  [+] Agent merge criado: agents/experts/{merged_name}.md")

    do_archive(repo, a)
    do_archive(repo, b)

    return True


def do_status(repo: Path):
    agent_dir = repo / "agents" / "experts"
    l2_dir = repo / "agents" / "experts" / "L2"
    archived_dir = repo / "agents" / "archived"

    l1 = list(agent_dir.glob("*.md")) if agent_dir.exists() else []
    l2 = list(l2_dir.glob("*.md")) if l2_dir.exists() else []
    archived = list(archived_dir.glob("*.md")) if archived_dir.exists() else []

    print(f"\n  AGENT ECOSYSTEM STATUS")
    print(f"  {'='*40}")
    print(f"  L1 Experts:   {len(l1)}")
    print(f"  L2 Specialists: {len(l2)}")
    print(f"  Archived:     {len(archived)}")
    print(f"  Total ativos: {len(l1) + len(l2)}\n")

    log_path = Path.home() / ".config" / "opencode" / "evolution-log.json"
    evo = load_json(log_path)
    if evo.get("evolutions"):
        print(f"  Ultimas evolucoes:")
        for e in evo["evolutions"][-5:]:
            print(f"    - {e.get('date','?')}: {e.get('action','?')} -> {e.get('name','?')}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Agent evolution cycle")
    parser.add_argument("--check", action="store_true", help="Analisa e sugere acoes")
    parser.add_argument("--archive", metavar="NAME", help="Arquiva um agente")
    parser.add_argument("--promote", metavar="NAME", help="Promove L2 -> L1")
    parser.add_argument("--merge", nargs=2, metavar=("A", "B"), help="Mescla dois agentes")
    parser.add_argument("--status", action="store_true", help="Status do ecossistema")

    args = parser.parse_args()
    repo = get_repo_root()

    if args.check:
        suggestions = do_check(repo)
        if suggestions:
            print(f"\n  SUGESTOES DE EVOLUCAO ({len(suggestions)}):\n")
            for s in suggestions:
                if s["type"] == "archive":
                    print(f"  [ARCHIVE] {s['name']}: {s['reason']}")
                elif s["type"] == "promote":
                    print(f"  [PROMOTE] {s['name']}: {s['reason']}")
                elif s["type"] == "merge":
                    print(f"  [MERGE] {s['a']} <-> {s['b']}: {s['reason']}")
            print(f"\n  Use --archive, --promote, ou --merge para executar.\n")
        else:
            print(f"\n  Nenhuma sugestao de evolucao no momento.\n")

    elif args.archive:
        do_archive(repo, args.archive)
    elif args.promote:
        do_promote(repo, args.promote)
    elif args.merge:
        do_merge(repo, args.merge[0], args.merge[1])
    elif args.status:
        do_status(repo)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
