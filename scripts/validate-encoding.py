#!/usr/bin/env python3
"""
Valida encodings de arquivos de texto do repo (pessoal -> publico).

Bloqueia:
  - UTF-8 invalido (bytes que nao decodificam)
  - Mojibake latin-1 -> UTF-8 (texto acentuado re-encodado, ex.: "configura\\u00c3\\u00a7\\u00c3\\u00a3o")

Reporta (sem bloquear):
  - BOM UTF-8 em arquivos que nao deveriam ter (exceto setup.ps1, que precisa
    de BOM para o Windows PowerShell 5.1 ler UTF-8 corretamente)

Uso:
  python scripts/validate-encoding.py [--root <dir>] [--quiet]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SKIP_PARTS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", ".bun", ".cache", ".next"}
TEXT_EXTS = {
    ".md", ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".json", ".yml", ".yaml",
    ".ps1", ".sh", ".toml", ".cfg", ".ini", ".txt", ".template",
}
# BOM obrigatorio por compatibilidade com Windows PowerShell 5.1 (lê sem BOM como ANSI)
BOM_EXCEPTIONS = {"setup.ps1"}

# Mojibake latin-1 -> UTF-8: sequencias de caracteres que so aparecem quando
# bytes UTF-8 (0xC3/0xC2/0xE2...) foram lidos como latin-1 e re-encodados.
# Ex.: "ca" mojibake = 0xC3 0x83 0xC2 0xA7 0xC3 0x83 0xC2 0xA3 (era "ção");
#      seta = 0xC3 0xA2 0xE2 0x80 0xA0 0xE2 0x80 0x99 (era "\u2192").
MOJI_PATTERNS = [
    re.compile(r"[\u00c3][\u00a7\u00a3\u00a9\u00a1\u00aa\u00ae\u00ad\u00b3\u00a8\u00ab\u00ac\u00b0\u00b5\u00ba\u00bb\u00bc\u00bd\u00be\u00bf]"),
    re.compile(r"[\u00c2][\u00a0-\u00bf]"),
    re.compile(r"\u00e2\u20ac[\u0153\u201c\u201d\u2018\u2019\u201a\u201b\u2013\u2014\u2122\u2026]"),
    re.compile(r"\u00e2\u2020[\u2018\u2019\u201a\u201b]"),
    re.compile(r"\u00e2\u2013[\u2010\u2011\u2012\u2013\u2014\u2015]"),
]

def is_mojibake(text: str) -> bool:
    return any(pat.search(text) for pat in MOJI_PATTERNS)


def collect_text_files(root: Path):
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_PARTS for part in p.parts):
            continue
        if p.suffix.lower() not in TEXT_EXTS:
            continue
        yield p


def main() -> int:
    root_arg = None
    quiet = False
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--root" and i + 1 < len(args):
            root_arg = args[i + 1]
        elif arg == "--quiet":
            quiet = True

    root = Path(root_arg).resolve() if root_arg else ROOT
    errors: list[str] = []
    warnings: list[str] = []

    for p in collect_text_files(root):
        rel = p.relative_to(root).as_posix()
        raw = p.read_bytes()
        bom = raw.startswith(b"\xef\xbb\xbf")

        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            errors.append(f"{rel}: UTF-8 inválido ({exc})")
            continue

        if is_mojibake(text):
            errors.append(f"{rel}: mojibake (latin-1 re-encodado) — corrigir acentuação")
            continue

        if bom and rel not in BOM_EXCEPTIONS:
            warnings.append(f"{rel}: BOM UTF-8 desnecessário (remover; exceção: {sorted(BOM_EXCEPTIONS)})")

    if not quiet:
        print(f"Encoding validation: {len(errors)} erros, {len(warnings)} avisos")

    if errors:
        print("Encoding validation failed:", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1

    if warnings and not quiet:
        for w in warnings:
            print(f"WARN: {w}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
