#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
import urllib.request
import urllib.error
import json
import shutil
import tempfile
import zipfile
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
REPO = "redeintegrativa-bot/opencode-core-public"
GITHUB = f"https://github.com/{REPO}"
_branch_cache = None


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
    _branch_cache = "master"
    return _branch_cache

V = '\033[32m'; C = '\033[36m'; A = '\033[33m'; R = '\033[31m'; B = '\033[1m'; S = '\033[0m'


def log(msg, color=V):
    print(f"  {color}{msg}{S}")


def check_git():
    try:
        result = subprocess.run(
            ["git", "-C", str(REPO_DIR), "remote", "get-url", "origin"],
            capture_output=True, text=True, timeout=5
        )
        return REPO in result.stdout.strip()
    except Exception:
        return False


def update_via_git():
    branch = get_default_branch()
    log(f"Atualizando via git pull ({branch})...", C)
    try:
        subprocess.run(["git", "-C", str(REPO_DIR), "fetch", "origin", branch],
                       check=True, timeout=30)
        result = subprocess.run(
            ["git", "-C", str(REPO_DIR), "log", "--oneline", f"HEAD..origin/{branch}"],
            capture_output=True, text=True, timeout=10
        )
        if result.stdout.strip():
            log(f"Mudancas pendentes:\n{result.stdout}", A)
            subprocess.run(["git", "-C", str(REPO_DIR), "pull", "origin", branch],
                           check=True, timeout=30)
            log("Atualizado com sucesso via git!", V)
            return True
        else:
            log("Ja esta na versao mais recente.", A)
            return True
    except subprocess.CalledProcessError as e:
        log(f"Erro no git pull: {e}", R)
        return False
    except subprocess.TimeoutExpired:
        log("Git pull excedeu tempo limite.", R)
        return False


def update_via_zip():
    branch = get_default_branch()
    zip_url = f"{GITHUB}/archive/refs/heads/{branch}.zip"
    log(f"Baixando ultima versao do GitHub ({branch})...", C)
    zip_path = Path(tempfile.mkdtemp()) / "update.zip"

    try:
        req = urllib.request.Request(zip_url, headers={"User-Agent": "opencode-core/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            zip_path.write_bytes(resp.read())

        log(f"Download concluido ({zip_path.stat().st_size / 1024:.0f} KB)", V)

        extract_dir = Path(tempfile.mkdtemp())
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_dir)

        inner = extract_dir / f"opencode-core-public-{branch}"
        if not inner.exists():
            inner = extract_dir / f"{REPO.split('/')[1]}-{branch}"

        if not inner.exists():
            log("Estrutura do ZIP inesperada.", R)
            return False

        log("Aplicando atualizacao...", C)
        for item in inner.iterdir():
            target = REPO_DIR / item.name
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
            shutil.move(str(item), str(target))

        shutil.rmtree(extract_dir, ignore_errors=True)
        zip_path.unlink()

        log("Atualizado com sucesso via ZIP!", V)
        return True

    except Exception as e:
        log(f"Erro no download: {e}", R)
        return False


def reinstall_components():
    """Reaplica skills/agentes/regras/hooks/plugins/comandos no config do usuario."""
    setup = REPO_DIR / "setup.sh" if os.name != "nt" else REPO_DIR / "setup.ps1"
    if not setup.exists():
        log("setup nao encontrado; pulando reinstall.", A)
        return True
    log("Reinstalando componentes no seu config...", C)
    try:
        if os.name != "nt":
            subprocess.run(["bash", str(setup), "--skip-update-check", "--all"],
                           check=True, cwd=str(REPO_DIR), timeout=120)
        else:
            subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                 "-File", str(setup), "-All", "-SkipUpdateCheck"],
                check=True, cwd=str(REPO_DIR), timeout=120)
        log("Reinstall concluido.", V)
        return True
    except subprocess.CalledProcessError as e:
        log(f"Falha no reinstall (pode rodar ./setup.sh manualmente): {e}", A)
        return False
    except subprocess.TimeoutExpired:
        log("Reinstall excedeu tempo limite (pode rodar ./setup.sh manualmente).", A)
        return False


def main():
    parser = argparse.ArgumentParser(description="Atualiza o OpenCode Core.")
    parser.add_argument(
        "--no-install", action="store_true",
        help="Apenas baixa/atualiza os arquivos, sem reinstalar componentes no config.")
    args = parser.parse_args()

    print()
    log("OpenCode Core — Atualizacao", C)
    print()

    has_git = check_git()

    if has_git:
        log("Repositorio git detectado.", V)
        ok = update_via_git()
    else:
        log("Repositorio git nao detectado. Usando download ZIP.", A)
        ok = update_via_zip()

    if ok:
        print()
        if not args.no_install:
            reinstall_components()
        else:
            log("--no-install: componentes NAO foram reinstalados.", A)
            log("  Rode ./setup.sh (ou .\\setup.ps1) para aplicar skills/plugins.", C)
        print()
        log("Atualizacao concluida!", V)
        log("Rode novamente o onboarding se quiser.", G)
        log("  python onboarding.py", G)
        print()
    else:
        print()
        log("Falha na atualizacao. Tente manualmente:", R)
        log(f"  git pull origin master", C)
        log(f"  Ou clone novamente: git clone https://github.com/{REPO}.git", C)
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()
