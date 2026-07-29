#!/usr/bin/env python3
"""
register-agent.py — Registra um novo agente nos arquivos do sistema.

Uso:
  python scripts/register-agent.py <nome> --level L1 --keywords "k1, k2" --desc "descricao" --path "agents/experts/nome.md" [--parent "parent_name"]

Atualiza:
  - agents/core/INDEX.md
  - agents/system/AGENT_REGISTRY.md
  - agents/core/orchestrator.md
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path


def get_repo_root() -> Path:
    here = Path(__file__).resolve().parent.parent
    if (here / ".opencode" / "opencode.json").exists():
        return here
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, timeout=5
    )
    if result.returncode == 0:
        return Path(result.stdout.strip())
    return here


def update_index_md(repo: Path, name: str, level: str, description: str, keywords: str, parent: str = ""):
    path = repo / "agents" / "core" / "INDEX.md"
    if not path.exists():
        print(f"  [!] INDEX.md nao encontrado: {path}")
        return

    text = path.read_text(encoding="utf-8")

    if level.upper() == "L1":
        section_header = "## L1 EXPERTS"
        new_row = f"| **{name}.md** | {description} | {keywords} |"
        marker = "|-------|------|----------|"
    else:
        section_header = "## L2 SPECIALISTS"
        new_row = f"| **{name}.md** | {parent} | {description} |"
        marker = "|-------|---------------|-----------|"

    if f"**{name}.md**" in text:
        print(f"  [-] {name}.md ja existe em INDEX.md, pulando")
        return

    section_start = text.find(section_header)
    if section_start == -1:
        print(f"  [!] Secao {section_header} nao encontrada em INDEX.md")
        return

    after_section = text[section_start:]
    marker_pos = after_section.find(marker)
    if marker_pos == -1:
        print(f"  [!] Marcador de tabela nao encontrado")
        return

    table_start = section_start + marker_pos + len(marker)
    table_lines = text[table_start:].split("\n")

    insert_idx = 1
    for i, line in enumerate(table_lines[1:], start=1):
        if not line.strip().startswith("| **"):
            insert_idx = i
            break
        existing_name = line.split("|")[1].strip().strip("*").replace(".md", "")
        if existing_name.lower() > name.lower():
            insert_idx = i
            break
        insert_idx = i + 1

    updated_lines = text.split("\n")
    insert_line = table_start + sum(len(l) + 1 for l in updated_lines[:table_lines.index(table_lines[0])]) + 1
    actual_line = 0
    line_count = 0
    for i, line in enumerate(updated_lines):
        if line_count >= insert_idx:
            actual_line = i
            break
        line_count += 1

    # simpler approach: just append before the next empty line after table
    sep_line = None
    for i in range(actual_line, len(updated_lines)):
        if updated_lines[i].strip() == "" or updated_lines[i].strip().startswith("---"):
            sep_line = i
            break

    if sep_line is None:
        sep_line = len(updated_lines)

    updated_lines.insert(sep_line, new_row)
    path.write_text("\n".join(updated_lines), encoding="utf-8")
    print(f"  [+] INDEX.md: entrada adicionada para {name}")


def update_agent_registry(repo: Path, name: str, keywords: str):
    path = repo / "agents" / "system" / "AGENT_REGISTRY.md"
    if not path.exists():
        print(f"  [!] AGENT_REGISTRY.md nao encontrado: {path}")
        return

    text = path.read_text(encoding="utf-8")

    if f"→ {name}" in text:
        print(f"  [-] {name} ja registrado em AGENT_REGISTRY.md, pulando")
        return

    keyword_part = "/".join(k.strip() for k in keywords.split(",")[:4])
    new_line = f"│  {keyword_part} → {name} {' ' * max(0, 70 - len(keyword_part) - len(name) - 6)}│"

    box_end = text.rfind("└")
    if box_end == -1:
        print(f"  [!] Box ASCII nao encontrado em AGENT_REGISTRY.md")
        return

    before_box = text[:box_end]
    lines = before_box.split("\n")

    for i in range(len(lines) - 1, -1, -1):
        if "→" in lines[i] and lines[i].strip().startswith("│"):
            lines.insert(i + 1, new_line)
            path.write_text("\n".join(lines) + text[box_end:], encoding="utf-8")
            print(f"  [+] AGENT_REGISTRY.md: rota adicionada para {name}")
            return

    print(f"  [!] Nao foi possivel encontrar posicao no box ASCII")


def update_orchestrator_routing(repo: Path, name: str, level: str, keywords: str, parent: str = ""):
    path = repo / "agents" / "core" / "orchestrator.md"
    if not path.exists():
        print(f"  [!] orchestrator.md nao encontrado: {path}")
        return

    text = path.read_text(encoding="utf-8")

    if name in text:
        print(f"  [-] {name} ja registrado em orchestrator.md, pulando")
        return

    if level.upper() == "L2" and parent:
        agent_path = f"experts/L2/{name}.md"
        model = "sonnet (inherit)"
    else:
        agent_path = f"experts/{name}.md"
        model = "sonnet (inherit)"

    keyword_str = ", ".join(k.strip() for k in keywords.split(","))
    new_row = f"| {keyword_str} | {agent_path} | {model} |"

    fallback_marker = "Fallback: `core/coder.md`"
    fallback_pos = text.find(fallback_marker)
    if fallback_pos == -1:
        print(f"  [!] Marcador de fallback nao encontrado em orchestrator.md")
        return

    before_fallback = text[:fallback_pos]
    lines = before_fallback.split("\n")

    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip().startswith("| "):
            lines.insert(i + 1, new_row)
            break

    path.write_text("\n".join(lines) + text[fallback_pos:], encoding="utf-8")
    print(f"  [+] orchestrator.md: rota adicionada para {name}")


def update_counts(repo: Path, name: str, level: str):
    """Atualiza os contadores nos arquivos relevantes."""
    for fname in ["INDEX.md", "orchestrator.md", "CLAUDE.md"]:
        path = repo / "agents" / "core" / fname
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")

        def increment_count(m):
            current = int(m.group(1))
            return m.group(0).replace(str(current), str(current + 1))

        text = re.sub(r"(\d+)\s*agents?\s", increment_count, text, count=1)
        text = re.sub(r"(\d+)\s*(Total|totale|totali)", increment_count, text, count=1)
        path.write_text(text, encoding="utf-8")
        print(f"  [+] {fname}: contadores atualizados")


def main():
    parser = argparse.ArgumentParser(description="Registra um novo agente no sistema")
    parser.add_argument("name", help="Nome do agente (sem .md)")
    parser.add_argument("--level", required=True, choices=["L1", "L2"], help="Nivel do agente")
    parser.add_argument("--keywords", required=True, help="Keywords separadas por virgula")
    parser.add_argument("--desc", required=True, help="Descricao do agente")
    parser.add_argument("--path", help="Caminho completo do arquivo (opcional)")
    parser.add_argument("--parent", default="", help="Parent expert (se L2)")
    parser.add_argument("--dry-run", action="store_true", help="Mostra o que seria feito sem alterar arquivos")

    args = parser.parse_args()
    repo = get_repo_root()

    name_clean = args.name.replace(".md", "")
    print(f"\n  Registrando agente: {name_clean}")
    print(f"  Nivel: {args.level}")
    print(f"  Keywords: {args.keywords}")
    print(f"  Descricao: {args.desc}")
    if args.parent:
        print(f"  Parent: {args.parent}")
    print()

    if args.dry_run:
        print("  [DRY RUN] Nenhum arquivo foi alterado.\n")
        return

    update_index_md(repo, name_clean, args.level, args.desc, args.keywords, args.parent)
    update_agent_registry(repo, name_clean, args.keywords)
    update_orchestrator_routing(repo, name_clean, args.level, args.keywords, args.parent)
    update_counts(repo, name_clean, args.level)

    print(f"\n  Agente {name_clean} registrado com sucesso!\n")


if __name__ == "__main__":
    main()
