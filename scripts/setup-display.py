#!/usr/bin/env python3
"""
setup-display.py — Ajusta fonte do terminal e layout do opencode conforme a tela.

A fonte renderizada pelo opencode vem do emulador de terminal, nao do proprio
opencode. Este script detecta a tela (resolucao, DPI, modelo do monitor) e:
  - Windows Terminal: escreve profiles.defaults.font.size no settings.json
  - opencode: ajusta prompt.max_width/max_height e diff_style no tui.json

Uso:
  python setup-display.py --detect     # Coleta dados da tela e salva perfil
  python setup-display.py --apply      # Aplica fonte + layout baseado no perfil
  python setup-display.py --undo       # Restaura backups
  python setup-display.py --profile    # Mostra o perfil detectado
  python setup-display.py --dry-run    # Mostra o que faria sem escrever

Backups:
  - settings.json   -> settings.json.bak
  - tui.json        -> tui.json.bak
  O primeiro backup e preservado (nunca sobrescrito) para garantir restauracao.
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "opencode"
STATE_DIR = CONFIG_DIR / "state"
PROFILE_FILE = STATE_DIR / "display-profile.json"
TUI_FILE = CONFIG_DIR / "tui.json"

WT_SETTINGS_CANDIDATES = [
    Path.home()
    / "AppData"
    / "Local"
    / "Packages"
    / "Microsoft.WindowsTerminal_8wekyb3d8bbwe"
    / "LocalState"
    / "settings.json",
    Path.home()
    / "AppData"
    / "Local"
    / "Packages"
    / "Microsoft.WindowsTerminalPreview_8wekyb3d8bbwe"
    / "LocalState"
    / "settings.json",
]


def log(msg):
    print(msg)


def err(msg):
    print(f"ERRO: {msg}", file=sys.stderr)


def load_json(path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def run_ps(script):
    """Executa um comando PowerShell e retorna a saida stdout."""
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            capture_output=True,
            text=True,
            timeout=60,
        )
        return proc.stdout.strip() or proc.stderr.strip()
    except (subprocess.SubprocessError, OSError):
        return ""


def detect_screen():
    """Detecta resolucao, DPI e modelo do monitor primario."""
    res = run_ps(
        "Add-Type -AssemblyName System.Windows.Forms; "
        "Add-Type -AssemblyName System.Drawing; "
        "$s=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds; "
        "$d=[System.Drawing.Graphics]::FromHwnd([IntPtr]::Zero).DpiX; "
        "Write-Output \"$($s.Width)x$($s.Height)|$d\""
    )
    width, height, dpi = 0, 0, 96
    if "|" in res:
        parts = res.split("|")
        reso = parts[0]
        if "x" in reso:
            try:
                width, height = (int(v) for v in reso.split("x"))
            except ValueError:
                pass
        try:
            dpi = int(float(parts[1]))
        except (ValueError, IndexError):
            pass

    monitor = run_ps(
        "Get-CimInstance -Namespace 'root\\wmi' -ClassName WmiMonitorBasicDisplayParams "
        "| Select-Object -First 1 | ForEach-Object { $_.InstanceName }"
    )

    profile = {
        "version": 1,
        "resolution": {"width": width, "height": height},
        "dpi": dpi,
        "dpi_scale": round(dpi / 96.0, 2),
        "monitor": monitor,
        "detected_at": None,
    }
    return profile


def recommend(profile):
    """Calcula fonte recomendada e ajustes de layout a partir do perfil."""
    width = profile["resolution"]["width"]
    height = profile["resolution"]["height"]
    dpi_scale = profile.get("dpi_scale", 1.0)

    # Base pela altura (espaco vertical disponivel em pixels).
    # Nunca reduz abaixo de 12 (default do Windows Terminal): o caso tipico
    # de reclamacao e fonte PEQUENA em telas grandes, nao o contrario.
    # O Windows Terminal ja escala a fonte por DPI sozinho, entao nao
    # multiplicamos por dpi_scale aqui (evita super-correcao).
    if height >= 2160:
        base = 16
    elif height >= 1440:
        base = 14
    elif height >= 1080:
        base = 12
    else:
        base = 12

    font_size = max(12, min(16, base))

    # Layout do opencode em colunas do terminal (aproximado)
    approx_cols = max(80, int(width / 8 * dpi_scale))

    return {
        "font_size": font_size,
        "prompt_max_width": 120,
        "prompt_max_height": 10,
        "diff_style": "auto" if approx_cols >= 140 else "stacked",
        "approx_cols": approx_cols,
    }


def find_wt_settings():
    for path in WT_SETTINGS_CANDIDATES:
        if path.exists():
            return path
    return None


def backup(path):
    """Cria backup .bak preservando o primeiro (nunca sobrescreve)."""
    if not path.exists():
        return None
    bak = path.with_suffix(path.suffix + ".bak")
    if not bak.exists():
        shutil.copy2(path, bak)
    return bak


def apply_wt_font(font_size, dry_run=False):
    settings = find_wt_settings()
    if not settings:
        err("Windows Terminal nao encontrado. A fonte fica como esta.")
        return False

    data = load_json(settings)
    if data is None:
        err(f"Nao consegui ler {settings} (JSON invalido?).")
        return False

    data.setdefault("profiles", {})
    data["profiles"].setdefault("defaults", {})
    old = data["profiles"]["defaults"].get("font", {}).get("size")

    if old and old != font_size:
        log(f"  Aviso: font.size ja definido como {old} (perfil do usuario). "
            f"Sera trocado para {font_size} — use --undo para reverter.")
    elif old == font_size:
        log(f"  font.size ja e {font_size} — nada a fazer.")

    data["profiles"]["defaults"]["font"] = {
        **data["profiles"]["defaults"].get("font", {}),
        "size": font_size,
    }

    if dry_run:
        log(f"  [dry-run] {settings}")
        log(f"  [dry-run] profiles.defaults.font.size = {font_size}")
        return True

    backup(settings)
    save_json(settings, data)
    log(f"  Fonte do Windows Terminal ajustada para {font_size}pt em {settings}")
    return True


def apply_tui_layout(rec, dry_run=False):
    if not TUI_FILE.exists():
        err(f"tui.json nao encontrado em {TUI_FILE}. Criando novo...")

    data = load_json(TUI_FILE, {}) or {}
    data["prompt"] = {
        "max_width": rec["prompt_max_width"],
        "max_height": rec["prompt_max_height"],
    }
    data["diff_style"] = rec["diff_style"]

    if dry_run:
        log(f"  [dry-run] {TUI_FILE}")
        log(f"  [dry-run] prompt.max_width = {rec['prompt_max_width']}, "
            f"max_height = {rec['prompt_max_height']}, diff_style = {rec['diff_style']}")
        return True

    backup(TUI_FILE)
    save_json(TUI_FILE, data)
    log(f"  Layout do opencode ajustado em {TUI_FILE}")
    return True


def do_detect():
    profile = detect_screen()
    profile["detected_at"] = "now"
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    save_json(PROFILE_FILE, profile)
    log(f"Perfil salvo em {PROFILE_FILE}")
    print(json.dumps(profile, indent=2, ensure_ascii=False))
    rec = recommend(profile)
    log(f"Recomendacao: fonte {rec['font_size']}pt, "
        f"prompt {rec['prompt_max_width']}x{rec['prompt_max_height']}, "
        f"diff {rec['diff_style']}")
    return 0


def do_apply(dry_run=False):
    profile = load_json(PROFILE_FILE)
    if not profile:
        err("Perfil nao encontrado. Rode primeiro: python setup-display.py --detect")
        return 1

    rec = recommend(profile)
    log(f"Tela: {profile['resolution']['width']}x{profile['resolution']['height']} "
        f"@ {profile.get('dpi_scale', 1.0)}x ({profile.get('monitor') or 'desconhecido'})")
    log(f"Recomendacao: fonte {rec['font_size']}pt, "
        f"diff_style {rec['diff_style']}, prompt {rec['prompt_max_width']} col")

    ok_wt = apply_wt_font(rec["font_size"], dry_run=dry_run)
    ok_tui = apply_tui_layout(rec, dry_run=dry_run)

    if ok_wt or ok_tui:
        log("Concluido. Reinicie o opencode para o novo layout valer; a fonte do terminal aplica ao vivo.")
    return 0 if (ok_wt or ok_tui) else 1


def do_undo():
    restored = []
    for path in [TUI_FILE, find_wt_settings()]:
        if not path:
            continue
        bak = path.with_suffix(path.suffix + ".bak")
        if bak.exists():
            shutil.copy2(bak, path)
            restored.append(str(path))
    if restored:
        log("Backups restaurados:")
        for r in restored:
            log(f"  {r}")
    else:
        log("Nenhum backup encontrado para restaurar.")
    return 0


def do_profile():
    profile = load_json(PROFILE_FILE)
    if not profile:
        err("Perfil nao encontrado. Rode: python setup-display.py --detect")
        return 1
    print(json.dumps(profile, indent=2, ensure_ascii=False))
    return 0


def main():
    parser = argparse.ArgumentParser(description="Ajusta fonte do terminal e layout do opencode conforme a tela.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--detect", action="store_true", help="Detecta a tela e salva o perfil")
    group.add_argument("--apply", action="store_true", help="Aplica fonte + layout baseado no perfil")
    group.add_argument("--undo", action="store_true", help="Restaura backups")
    group.add_argument("--profile", action="store_true", help="Mostra o perfil detectado")
    group.add_argument("--dry-run", action="store_true", help="Mostra o que faria sem escrever")
    args = parser.parse_args()

    if args.detect:
        return do_detect()
    if args.apply:
        return do_apply(dry_run=False)
    if args.dry_run:
        return do_apply(dry_run=True)
    if args.undo:
        return do_undo()
    if args.profile:
        return do_profile()
    return 0


if __name__ == "__main__":
    sys.exit(main())
