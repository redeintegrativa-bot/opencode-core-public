#!/usr/bin/env python3
"""Diagnostico rapido e somente leitura dos repositorios de um diretorio."""

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def run_git(repo: Path, *args: str) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return completed.stdout.strip() if completed.returncode == 0 else ""


def project_status(repo: Path) -> dict:
    porcelain = run_git(repo, "status", "--porcelain")
    changes = [line for line in porcelain.splitlines() if line]
    head = run_git(repo, "rev-parse", "--abbrev-ref", "HEAD") or "detached"
    commit = run_git(repo, "log", "-1", "--format=%h %cs %s") or "sem commits"
    return {
        "name": repo.name,
        "path": str(repo),
        "branch": head,
        "dirty": bool(changes),
        "changes": len(changes),
        "last_commit": commit,
    }


def discover(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(
        path for path in root.iterdir()
        if path.is_dir() and (path / ".git").exists()
    )


def print_human(report: dict) -> None:
    projects = report["projects"]
    clean = sum(not item["dirty"] for item in projects)
    print("Projetos: {} ({} limpos, {} com alteracoes)".format(
        len(projects), clean, len(projects) - clean
    ))
    print()
    for item in projects:
        state = "PENDENTE" if item["dirty"] else "LIMPO"
        suffix = " ({} arquivo(s))".format(item["changes"]) if item["dirty"] else ""
        print("[{}] {} [{}]{}".format(state, item["name"], item["branch"], suffix))
        print("  {}".format(item["last_commit"]))


def main() -> int:
    parser = argparse.ArgumentParser(description="Mostra a saude Git dos projetos.")
    parser.add_argument("--root", type=Path, default=Path.home() / "projects")
    parser.add_argument("--json", action="store_true", help="Emite JSON para automacoes.")
    args = parser.parse_args()

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(args.root),
        "projects": [project_status(repo) for repo in discover(args.root)],
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
