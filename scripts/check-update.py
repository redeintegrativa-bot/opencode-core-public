#!/usr/bin/env python3
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
    """Detecta a branch padrao do repo (main ou master) via git ls-remote."""
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
    """Retorna blocos do changelog entre a versao local (exclusiva) e a remota.

    As secoes do changelog podem nao vir ordenadas, entao comparamos por
    versao em vez de depender da ordem do arquivo.
    """
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


def self_test():
    """Testes internos sem rede (valida parse, diff e branch)."""
    ok = True

    def check(name, cond):
        nonlocal ok
        status = "OK" if cond else "FAIL"
        print(f"  [{status}] {name}")
        if not cond:
            ok = False

    check("parse normal", parse("1.2.3") == (1, 2, 3))
    check("parse com prefixo", parse("v2.0.0") == (0, 0, 0))
    check("parse invalido", parse("abc") == (0, 0, 0))
    check("compare maior", parse("1.3.0") > parse("1.2.9"))
    check("compare igual", parse("1.2.0") == parse("1.2.0"))

    # Changelog fora de ordem (como o CHANGELOG.md real: 1.3.0, 1.0.0, 1.1.0, 1.2.0)
    fake_sections = [
        ("1.3.0", "## 1.3.0\n- feature A"),
        ("1.0.0", "## 1.0.0\n- old stuff"),
        ("1.1.0", "## 1.1.0\n- fix B"),
        ("1.2.0", "## 1.2.0\n- feature C"),
    ]

    def _filter(local, remote):
        plocal = parse(local)
        premote = parse(remote)
        out = []
        for ver, block in fake_sections:
            pver = parse(ver)
            if plocal < pver <= premote:
                out.append(block)
        return sorted(out, key=lambda b: parse(re.match(r'## (\d+\.\d+\.\d+)', b).group(1)), reverse=True)

    check("diff 1.0.0->1.3.0 pega 3", len(_filter("1.0.0", "1.3.0")) == 3)
    check("diff 1.2.0->1.3.0 pega 1", len(_filter("1.2.0", "1.3.0")) == 1)
    check("diff igual vazio", len(_filter("1.3.0", "1.3.0")) == 0)
    check("diff downgrade vazio", len(_filter("1.3.0", "1.0.0")) == 0)
    check("diff 1.1.0->1.2.0 pega 1", len(_filter("1.1.0", "1.2.0")) == 1)

    check("branch resolve", get_default_branch() in ("main", "master"))

    print()
    return 0 if ok else 1


def main():
    if "--self-test" in sys.argv:
        sys.exit(self_test())

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
