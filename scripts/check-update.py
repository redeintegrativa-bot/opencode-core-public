#!/usr/bin/env python3
"""
OpenCode Core (pessoal) — check-update
Compara a versao local deste repo contra o repositorio PUBLICO
(redeintegrativa-bot/opencode-core-public), que e a fonte de verdade
das skills/agents/rules compartilhadas.
"""
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
VERSION_FILE = REPO_DIR / "VERSION"
REPO = "redeintegrativa-bot/opencode-core-public"
GITHUB = f"https://github.com/{REPO}"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO}"
_branch_cache = None

V = '\033[32m'; C = '\033[36m'; A = '\033[33m'; R = '\033[31m'; B = '\033[1m'; S = '\033[0m'; G = '\033[90m'


def get_local_version():
    if not VERSION_FILE.exists():
        return "0.0.0"
    return VERSION_FILE.read_text(encoding="utf-8").strip()


def get_default_branch():
    """Detecta a branch padrao do repo publico (main ou master)."""
    global _branch_cache
    if _branch_cache:
        return _branch_cache
    try:
        r = subprocess.run(
            ["git", "ls-remote", "--symref", f"{GITHUB}.git", "HEAD"],
            capture_output=True, text=True, timeout=10
        )
        for line in r.stdout.splitlines():
            if line.startswith("ref:"):
                branch = line.split("refs/heads/")[-1].split()[0].strip()
                if branch:
                    _branch_cache = branch
                    return _branch_cache
    except Exception:
        pass
    for cand in ("main", "master"):
        try:
            fetch(f"{RAW_BASE}/{cand}/VERSION")
            _branch_cache = cand
            return _branch_cache
        except Exception:
            continue
    _branch_cache = "master"
    return _branch_cache


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "opencode-core/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.read().decode()


def get_remote_version():
    try:
        return fetch(f"{RAW_BASE}/{get_default_branch()}/VERSION").strip()
    except Exception:
        return None


def parse(v):
    try:
        return tuple(int(x) for x in v.split("."))
    except (ValueError, AttributeError):
        return (0, 0, 0)


def get_changelog_sections():
    try:
        text = fetch(f"{RAW_BASE}/{get_default_branch()}/CHANGELOG.md")
    except Exception:
        return []
    blocks = re.split(r'\n(?=## \d+\.\d+\.\d+)', text)
    sections = []
    for block in blocks:
        m = re.match(r'## (\d+\.\d+\.\d+)', block)
        if m:
            sections.append((m.group(1), block.strip()))
    return sections


def get_changelog_diff(local, remote):
    """Blocos do changelog publico entre a versao local (exclusiva) e a remota."""
    sections = get_changelog_sections()
    plocal = parse(local)
    premote = parse(remote)
    out = []
    for ver, block in sections:
        pver = parse(ver)
        if plocal < pver <= premote:
            out.append(block)
    return sorted(out, key=lambda b: parse(re.match(r'## (\d+\.\d+\.\d+)', b).group(1)), reverse=True)


def show_changelog(lines):
    if not lines:
        return
    print(f"  {G}{'='*50}{S}")
    for line in lines.split('\n'):
        if not line.strip():
            continue
        if line.startswith('## '):
            print(f"  {C}{B}{line.strip()}{S}")
        elif line.startswith('### '):
            print(f"  {A}{line.strip()}{S}")
        elif line.startswith('- '):
            print(f"  {G}{line.strip()}{S}")
        else:
            print(f"  {line.strip()}")
    print(f"  {G}{'='*50}{S}")
    print()


def main():
    local = get_local_version()
    remote = get_remote_version()

    if not remote:
        print("  (sem conexao — check-update ignorado)")
        return

    has_update = parse(remote) > parse(local)

    if "--json" in sys.argv:
        changelog_blocks = get_changelog_diff(local, remote) if has_update else []
        changelog_text = "\n\n".join(changelog_blocks) if changelog_blocks else ""
        print(json.dumps({
            "local": local,
            "remote": remote,
            "has_update": has_update,
            "update_available": has_update,
            "changelog": changelog_text,
        }))
        return

    if has_update:
        print()
        print(f"  {A}{B}[!] O repositorio publico tem novidades{S}")
        print(f"  {G}  local: {local}  publico: {remote}{S}")
        print()
        changelog_blocks = get_changelog_diff(local, remote)
        if changelog_blocks:
            print(f"  {G}O que mudou no publico:{S}")
            print()
            for block in changelog_blocks:
                show_changelog(block)
        print(f"  {G}Este repo e personalizado — revisar o changelog acima e mergear")
        print(f"  manualmente o que fizer sentido (skills/agents/rules).{S}")
        print()


if __name__ == "__main__":
    main()
