#!/usr/bin/env python3
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
VERSION_FILE = REPO_DIR / "VERSION"
REPO = "redeintegrativa-bot/opencode-core-public"
API_URL = f"https://api.github.com/repos/{REPO}/releases/latest"
BRANCH_URL = f"https://api.github.com/repos/{REPO}/git/ref/heads/master"

V = '\033[32m'; C = '\033[36m'; A = '\033[33m'; R = '\033[31m'; B = '\033[1m'; S = '\033[0m'


def get_local_version():
    if not VERSION_FILE.exists():
        return "0.0.0"
    return VERSION_FILE.read_text(encoding="utf-8").strip()


def get_remote_version():
    try:
        req = urllib.request.Request(API_URL, headers={"User-Agent": "opencode-core/1.0", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            return data.get("tag_name", "").lstrip("v")
    except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError):
        pass

    try:
        req = urllib.request.Request(BRANCH_URL, headers={"User-Agent": "opencode-core/1.0", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            sha = data.get("object", {}).get("sha", "")
            return f"dev-{sha[:7]}" if sha else None
    except Exception:
        return None


def compare_versions(local, remote):
    def parse(v):
        try:
            parts = v.split(".")
            return tuple(int(p) for p in parts)
        except (ValueError, AttributeError):
            return (0, 0, 0)

    return parse(remote) > parse(local)


def main():
    local = get_local_version()
    remote = get_remote_version()

    if not remote:
        return

    has_update = compare_versions(local, remote)

    result = {
        "local": local,
        "remote": remote,
        "has_update": has_update,
        "update_available": has_update,
    }

    if "--json" in sys.argv:
        print(json.dumps(result))
        return

    if has_update:
        print(f"\n  {A}{B}[!] Atualizacao disponivel!{S}")
        print(f"  {G}{local}{S} → {C}{remote}{S}")
        print(f"  {G}Rode: make update{S}")
        print(f"  {G}Ou:   python scripts/update.py{S}")
        print()

    return result


if __name__ == "__main__":
    G = '\033[90m'
    main()
