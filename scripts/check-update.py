#!/usr/bin/env python3
import json
import re
import sys
import urllib.request
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
VERSION_FILE = REPO_DIR / "VERSION"
BASE = "https://raw.githubusercontent.com/redeintegrativa-bot/opencode-core-public/master"
VERSION_URL = f"{BASE}/VERSION"
CHANGELOG_URL = f"{BASE}/CHANGELOG.md"

V = '\033[32m'; C = '\033[36m'; A = '\033[33m'; R = '\033[31m'; B = '\033[1m'; S = '\033[0m'; G = '\033[90m'


def get_local_version():
    if not VERSION_FILE.exists():
        return "0.0.0"
    return VERSION_FILE.read_text(encoding="utf-8").strip()


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "opencode-core/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.read().decode()


def get_remote_version():
    try:
        return fetch(VERSION_URL).strip()
    except Exception:
        return None


def parse(v):
    try:
        return tuple(int(x) for x in v.split("."))
    except (ValueError, AttributeError):
        return (0, 0, 0)


def get_changelog_sections():
    try:
        text = fetch(CHANGELOG_URL)
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
    sections = get_changelog_sections()
    all_vers = [s[0] for s in sections]
    plocal = parse(local)
    premote = parse(remote)
    in_range = False
    out = []
    for ver, block in sections:
        pver = parse(ver)
        if pver == premote:
            in_range = True
        if in_range:
            out.append(block)
        if pver == plocal:
            in_range = False
    return out


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
        print(f"  {A}{B}[!] Atualizacao disponivel{S}")
        print(f"  {G}  {local}{S} {C}->{S} {V}{remote}{S}")
        print()
        changelog_blocks = get_changelog_diff(local, remote)
        if changelog_blocks:
            print(f"  {G}O que mudou desde sua versao:{S}")
            print()
            for block in changelog_blocks:
                show_changelog(block)
        print(f"  {G}Para atualizar:  make update{S}")
        print(f"  {G}Ou:            python scripts/update.py{S}")
        print()


if __name__ == "__main__":
    main()
