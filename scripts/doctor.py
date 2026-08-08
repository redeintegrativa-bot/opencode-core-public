#!/usr/bin/env python3
"""Verificacoes locais de configuracao sem modificar o ambiente."""

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Verifica integridade do OpenCode Core.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    findings = []
    for link in root.rglob("*"):
        if link.is_symlink() and not link.exists():
            findings.append({"level": "warning", "check": "broken_symlink", "path": str(link.relative_to(root))})
    registry = json.loads((root / "skills" / "registry.json").read_text(encoding="utf-8"))
    disk_skills = {p.parent.name for p in (root / "skills").glob("*/SKILL.md")}
    registered = set(registry.get("skills", {}))
    for name in sorted(disk_skills - registered):
        findings.append({"level": "warning", "check": "unregistered_skill", "path": name})
    for name in sorted(registered - disk_skills):
        findings.append({"level": "warning", "check": "missing_skill", "path": name})
    report = {"ok": not any(item["level"] == "error" for item in findings), "findings": findings}
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("Doctor: {} achado(s)".format(len(findings)))
        for item in findings:
            print("[{}] {}: {}".format(item["level"].upper(), item["check"], item["path"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
