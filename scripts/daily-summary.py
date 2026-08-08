#!/usr/bin/env python3
"""Gera um resumo diario local a partir do diagnostico de projetos."""

import argparse
import json
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path


def load_report(root: Path) -> dict:
    command = [sys.executable, str(Path(__file__).with_name("project-health.py")), "--root", str(root), "--json"]
    result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=60)
    return json.loads(result.stdout)


def render(report: dict) -> str:
    projects = report["projects"]
    pending = [item for item in projects if item["dirty"]]
    lines = [
        "# Resumo diario - {}".format(date.today().isoformat()),
        "",
        "Gerado em: {}".format(datetime.now().astimezone().strftime("%H:%M %z")),
        "",
        "## Projetos",
    ]
    for item in projects:
        state = "pendente" if item["dirty"] else "limpo"
        detail = " ({} arquivo(s))".format(item["changes"]) if item["dirty"] else ""
        lines.append("- **{}**: {}{} - `{}`".format(item["name"], state, detail, item["last_commit"]))
    lines.extend(["", "## Atencao"])
    if pending:
        lines.append("- Projetos com alteracoes locais: {}.".format(", ".join(item["name"] for item in pending)))
    else:
        lines.append("- Nenhum projeto com alteracoes locais.")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera resumo diario local dos projetos.")
    parser.add_argument("--root", type=Path, default=Path.home() / "projects")
    parser.add_argument("--output-dir", type=Path, default=Path.home() / ".config" / "opencode" / "daily")
    parser.add_argument("--print", action="store_true", dest="print_only")
    args = parser.parse_args()

    summary = render(load_report(args.root))
    if args.print_only:
        print(summary, end="")
        return 0
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir / "{}.md".format(date.today().isoformat())
    output.write_text(summary, encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
