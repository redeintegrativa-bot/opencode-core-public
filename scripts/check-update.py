#!/usr/bin/env python3
import json
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
VERSION_FILE = REPO_DIR / "VERSION"
RAW_URL = "https://raw.githubusercontent.com/redeintegrativa-bot/opencode-core-public/master/VERSION"

V = '\033[32m'; C = '\033[36m'; A = '\033[33m'; R = '\033[31m'; B = '\033[1m'; S = '\033[0m'; G = '\033[90m'


def get_local_version():
    if not VERSION_FILE.exists():
        return "0.0.0"
    return VERSION_FILE.read_text(encoding="utf-8").strip()


def get_remote_version():
    try:
        req = urllib.request.Request(RAW_URL, headers={"User-Agent": "opencode-core/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.read().decode().strip()
    except Exception:
        return None


def parse(v):
    try:
        return tuple(int(x) for x in v.split("."))
    except (ValueError, AttributeError):
        return (0, 0, 0)


def ask_update(local, remote):
    print()
    print(f"  {A}{B}[!] Atualizacao disponivel!{S}")
    print(f"  {G}  {local}{S} {C}→{S} {V}{remote}{S}")
    print()
    try:
        choice = input(f"  {C}Deseja atualizar agora?{S} [S/n] ").strip().lower()
        if choice in ("", "s", "sim", "y", "yes"):
            print()
            subprocess.run([sys.executable, str(REPO_DIR / "scripts" / "update.py")])
        else:
            print()
            print(f"  {G}Depois rode:  make update{S}")
            print(f"  {G}Ou:          python scripts/update.py{S}")
            print()
    except (EOFError, KeyboardInterrupt):
        print()


def main():
    local = get_local_version()
    remote = get_remote_version()

    if not remote:
        return

    has_update = parse(remote) > parse(local)

    if "--json" in sys.argv:
        print(json.dumps({
            "local": local,
            "remote": remote,
            "has_update": has_update,
            "update_available": has_update,
        }))
        return

    if has_update:
        ask_update(local, remote)


if __name__ == "__main__":
    main()
