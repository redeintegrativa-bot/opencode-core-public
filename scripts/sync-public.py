#!/usr/bin/env python3
"""Sync generico do OpenCode Core (pessoal -> publico) baseado em manifesto.

Espelha SOMENTE recursos genericos do repo pessoal (~/opencode-core) no repo
publico (~/opencode-core-public). Nunca copia dados pessoais (MEMORY.md real,
sessions/, .env, dashboard, projetos pessoais).

Seguranca com manifesto: registra o hash SHA-256 de cada arquivo ja enviado.
Só espelha um arquivo cujo hash local mudou desde o ultimo push — nunca regride
um arquivo que o publico atualizou sozinho (ex.: scripts/update.py do publico
pode estar a frente do pessoal).

Uso:
  python scripts/sync-public.py --check      # lista pendencias (sem tocar nada)
  python scripts/sync-public.py --stage      # copia+commit local no publico
  python scripts/sync-public.py --push       # push no publico + atualiza manifesto
  python scripts/sync-public.py --status     # estado do espelho
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
TOP_LEVEL_DIRS = [
    "skills", "agents", "rules", "hooks", "templates", "patterns",
    "providers", "services", "workflows", "scripts", ".opencode",
    "plugins", "docs", "knowledge", ".github",
]
TOP_LEVEL_FILES = [
    "CHANGELOG.md", "VERSION", "README.md", "Makefile",
    "opencode.json", "setup.ps1", "setup.sh", ".gitignore",
    "onboarding.py", "onboarding.sh", "pytest.ini", "requirements.txt",
]
MEMORY_GENERIC = ["session.py", "MEMORY.template.md", ".gitignore"]

# Partes de caminho que nunca devem ir para o publico
BLOCKED_PARTS = {".git", "__pycache__", "node_modules", "dist", ".venv", "venv"}
BLOCKED_NAMES = {"MEMORY.md", ".state.json"}
BLOCKED_EXT = {".pyc", ".bak", ".tmp", ".log", ".jsonl", ".lock"}


def manifest_path() -> Path:
    return (
        Path.home() / ".config" / "opencode" / "state" / "sync-manifest.json"
    )


def default_repos():
    home = Path.home()
    return home / "opencode-core", home / "opencode-core-public"


# ---------------------------------------------------------------------------
# Colecao de arquivos genericos (whitelist)
# ---------------------------------------------------------------------------
def collect_generic(root: Path):
    """Mapeia caminho relativo -> arquivo, apenas recursos genericos."""
    out = {}

    for rel in TOP_LEVEL_FILES:
        p = root / rel
        if p.is_file():
            out[rel] = p

    for d in TOP_LEVEL_DIRS:
        base = root / d
        if not base.is_dir():
            continue
        for p in base.rglob("*"):
            if p.is_dir():
                continue
            rel = p.relative_to(root).as_posix()
            if _blocked(rel):
                continue
            out[rel] = p

    # memoria: apenas os arquivos genericos (nunca MEMORY.md real)
    for name in MEMORY_GENERIC:
        p = root / "memory" / name
        if p.is_file():
            out[f"memory/{name}"] = p

    return out


def _blocked(rel: str) -> bool:
    parts = set(rel.split("/"))
    if parts & BLOCKED_PARTS:
        return True
    if rel.startswith(".env") or "/.env" in rel:
        return True
    name = rel.rsplit("/", 1)[-1]
    if name in BLOCKED_NAMES:
        return True
    if any(name.endswith(ext) for ext in BLOCKED_EXT):
        return True
    return False


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def run_git(repo: Path, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, timeout=120,
    )


# ---------------------------------------------------------------------------
# Manifesto
# ---------------------------------------------------------------------------
def load_manifest():
    mp = manifest_path()
    if not mp.exists():
        return {"version": 1, "files": {}, "last_sync": None}
    try:
        return json.loads(mp.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"version": 1, "files": {}, "last_sync": None}


def save_manifest(manifest):
    mp = manifest_path()
    mp.parent.mkdir(parents=True, exist_ok=True)
    tmp = mp.with_suffix(".tmp")
    tmp.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, mp)


# ---------------------------------------------------------------------------
# Pendencia
# ---------------------------------------------------------------------------
def _managed(rel: str) -> bool:
    """True se sync-public e' responsavel por `rel` (whitelist vigente).

    Arquivos fora da whitelist (ex.: AGENTS.md, que e' doc diferente por repo)
    deixam de ser rastreados no manifesto SEM serem apagados do publico.
    """
    if rel in TOP_LEVEL_FILES:
        return True
    name = rel.rsplit("/", 1)[-1]
    if name in MEMORY_GENERIC and rel.startswith("memory/"):
        return True
    return any(rel == d or rel.startswith(d + "/") for d in TOP_LEVEL_DIRS)


def compute_pending(personal: Path, public: Path, manifest):
    local = collect_generic(personal)
    prev = manifest.get("files", {})
    changed, new, deleted = [], [], []
    for rel, p in sorted(local.items()):
        h = sha256_file(p)
        if rel not in prev:
            new.append(rel)
        elif prev[rel] != h:
            changed.append(rel)
    for rel in prev:
        if rel not in local and _managed(rel):
            deleted.append(rel)
    return changed, new, deleted


def describe(pending):
    changed, new, deleted = pending
    return f"{len(changed)} alterados, {len(new)} novos, {len(deleted)} removidos"


# ---------------------------------------------------------------------------
# Acoes
# ---------------------------------------------------------------------------
def cmd_check(personal, public):
    manifest = load_manifest()
    if not public.is_dir():
        print(f"[x] Repo publico nao encontrado em {public} — clone-o com:")
        print(f"    git clone https://github.com/redeintegrativa-bot/opencode-core-public.git {public}")
        return 1
    changed, new, deleted = compute_pending(personal, public, manifest)
    if not (changed or new or deleted):
        print("[=] Espelho em dia (sem pendencias).")
        return 0
    print(f"[!] Pendentes: {describe((changed, new, deleted))}")
    for rel in new:
        print(f"    NOVO    {rel}")
    for rel in changed:
        print(f"    MUDOU   {rel}")
    for rel in deleted:
        print(f"    REMOVER {rel}")
    return 1


def cmd_stage(personal, public):
    manifest = load_manifest()
    if not public.is_dir():
        print(f"[x] Repo publico nao encontrado: {public}")
        return 1
    changed, new, deleted = compute_pending(personal, public, manifest)
    if not (changed or new or deleted):
        print("[=] Nada a espelhar.")
        return 0

    # sync down do publico (ff-only) para nao perder commits que vieram dele
    pull = run_git(public, "pull", "--ff-only")
    if pull.returncode != 0:
        print(f"[!] Pull do publico falhou (nao espelhando): {pull.stderr.strip()[:300]}")
        return 1

    local = collect_generic(personal)
    staged = []
    for rel in new + changed:
        src = local[rel]
        dst = public / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())
        staged.append(rel)
    for rel in deleted:
        target = public / rel
        if target.exists():
            target.unlink()
            staged.append(rel)

    if not staged:
        print("[=] Nada a espelhar.")
        return 0

    r = run_git(public, "add", "-A")
    if r.returncode != 0:
        print(f"[x] git add falhou: {r.stderr.strip()[:300]}")
        return 1
    msg = "Sync do pessoal: " + ", ".join(staged[:8])
    if len(staged) > 8:
        msg += f" (+{len(staged) - 8} arquivos)"
    c = run_git(public, "commit", "-m", msg)
    if c.returncode != 0:
        err = ((c.stderr or "") + "\n" + (c.stdout or "")).strip()
        if "nothing to commit" in err.lower() or "no changes added" in err.lower():
            print("[=] Conteudo ja identico no publico (sem novo commit).")
            return 0
        print(f"[x] git commit falhou: {err[:300]}")
        return 1
    print(f"[+] Stage pronto ({describe((changed, new, deleted))}): {len(staged)} arquivos commitados localmente no publico.")
    print(f"    Commit local: {c.stdout.strip() or c.stderr.strip()}")
    print("    Push PENDENTE de aprovacao -> rode --push")
    return 0


def cmd_push(personal, public):
    manifest = load_manifest()
    if not public.is_dir():
        print(f"[x] Repo publico nao encontrado: {public}")
        return 1
    # garante que o stage local esta commitado antes do push
    st = run_git(public, "status", "--porcelain")
    if st.returncode == 0 and st.stdout.strip():
        print("[i] Ha alteracoes nao commitadas — rodando stage primeiro.")
        if cmd_stage(personal, public) != 0:
            return 1
    r = run_git(public, "push", "origin", "master")
    if r.returncode != 0:
        print(f"[x] Push falhou: {r.stderr.strip()[:300]}")
        return 1
    local_files = collect_generic(personal)
    manifest["files"] = {rel: sha256_file(p) for rel, p in local_files.items()}
    manifest["last_sync"] = datetime.now().isoformat(timespec="seconds")
    save_manifest(manifest)
    print("[+] Push concluido no publico + manifesto atualizado.")
    return 0


def cmd_status(personal, public):
    manifest = load_manifest()
    changed, new, deleted = compute_pending(personal, public, manifest)
    nfiles = len(manifest.get("files", {}))
    print(f"personal: {personal}")
    print(f"public:   {public} (existe: {public.is_dir()})")
    print(f"manifesto: {manifest_path()}")
    print(f"arquivos espelhados: {nfiles}")
    print(f"pendentes: {describe((changed, new, deleted))}")
    if manifest.get("last_sync"):
        print(f"ultimo sync: {manifest['last_sync']}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Sync generico pessoal -> publico")
    parser.add_argument("--root", default=None, help="Repo pessoal (padrao: ~/opencode-core)")
    parser.add_argument("--public", default=None, help="Repo publico (padrao: ~/opencode-core-public)")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("check").set_defaults(func=cmd_check)
    sub.add_parser("stage").set_defaults(func=cmd_stage)
    sub.add_parser("push").set_defaults(func=cmd_push)
    sub.add_parser("status").set_defaults(func=cmd_status)
    for name, fn in (("--check", cmd_check), ("--stage", cmd_stage),
                     ("--push", cmd_push), ("--status", cmd_status)):
        parser.add_argument(name, dest="flag", action="store_const", const=fn,
                            help=argparse.SUPPRESS)

    args = parser.parse_args()
    personal, public = default_repos()
    if args.root:
        personal = Path(args.root)
    if args.public:
        public = Path(args.public)
    func = getattr(args, "func", None) or getattr(args, "flag", None)
    if func is None:
        parser.error("informe um comando: check, stage, push ou status")
    return func(personal, public)


if __name__ == "__main__":
    sys.exit(main())
