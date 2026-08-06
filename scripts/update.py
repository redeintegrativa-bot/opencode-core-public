#!/usr/bin/env python3
"""
OpenCode Core (pessoal) — update seletivo
Este repo e personalizado (customizacoes locais em agents/skills/rules).
Em vez de sobrescrever tudo, este script:
  1. Baixa o ZIP do repo publico para uma pasta temporaria
  2. Mostra o diff entre o publico e o local para cada componente
  3. Copia arquivos NOVOS (que nao existem localmente) automaticamente
  4. Para arquivos EXISTENTES, mostra o caminho para revisao manual

Uso:
  python scripts/update.py --check      # so mostra o diff, nao copia
  python scripts/update.py              # copia arquivos novos + relatorio
"""
import filecmp
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
REPO = "redeintegrativa-bot/opencode-core-public"
GITHUB = f"https://github.com/{REPO}"

# Componentes compartilhados que valem sincronizar com o publico.
# (NAO inclui: memory/, terminal-chat/, telegram-bot/, my-money-track/
#  que sao pessoais ou templates.)
COMPONENTS = ["skills", "agents", "rules", "hooks", "templates", "patterns", "providers", "services"]

_branch_cache = None


def get_default_branch():
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
                _branch_cache = line.split("refs/heads/")[-1].split()[0].strip()
                if _branch_cache:
                    return _branch_cache
    except Exception:
        pass
    _branch_cache = "master"
    return _branch_cache


def download_public():
    branch = get_default_branch()
    zip_url = f"{GITHUB}/archive/refs/heads/{branch}.zip"
    tmp = Path(tempfile.mkdtemp())
    zip_path = tmp / "public.zip"
    req = urllib.request.Request(zip_url, headers={"User-Agent": "opencode-core/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        zip_path.write_bytes(resp.read())
    extract = tmp / "pub"
    extract.mkdir()
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract)
    inner = extract / f"opencode-core-public-{branch}"
    if not inner.exists():
        inner = extract / f"{REPO.split('/')[1]}-{branch}"
    if not inner.exists():
        raise FileNotFoundError("Estrutura do ZIP inesperada")
    return inner


def collect_files(root: Path):
    """Mapeia caminho relativo -> arquivo, ignorando .git, __pycache__, memory."""
    out = {}
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        rel = p.relative_to(root)
        parts = rel.parts
        if any(x in (".git", "__pycache__") or str(x).endswith(".pyc") for x in parts):
            continue
        if parts[0] == "memory":
            continue
        out[rel.as_posix()] = p
    return out


def main():
    check_only = "--check" in sys.argv
    print()
    print("  OpenCode Core (pessoal) — update seletivo")
    print()
    try:
        pub = download_public()
    except Exception as e:
        print(f"  [x] Falha ao baixar publico: {e}")
        sys.exit(1)

    for comp in COMPONENTS:
        pub_comp = pub / comp
        loc_comp = REPO_DIR / comp
        if not pub_comp.exists():
            continue
        pub_files = collect_files(pub_comp)
        new_files = []
        changed_files = []
        for rel, pub_file in sorted(pub_files.items()):
            target = loc_comp / rel
            if not target.exists():
                new_files.append((rel, pub_file))
            elif not filecmp.cmp(pub_file, target, shallow=False):
                changed_files.append((rel, pub_file))

        if not new_files and not changed_files:
            print(f"  [=] {comp}: identico ao publico")
            continue

        print(f"  [!] {comp}: {len(new_files)} novos, {len(changed_files)} alterados")

        if check_only:
            for rel, _ in new_files:
                print(f"      NOVO   {rel}")
            for rel, _ in changed_files:
                print(f"      MUDOU  {rel}")
        else:
            for rel, pub_file in new_files:
                target = loc_comp / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(pub_file, target)
                print(f"      + copiado {rel}")
            for rel, _ in changed_files:
                print(f"      ~ revisar {rel}")

    print()
    if check_only:
        print("  Use 'python scripts/update.py' para copiar os arquivos novos.")
    else:
        print("  Novos arquivos copiados. Alterados: revisar manualmente.")
    print()


if __name__ == "__main__":
    main()
