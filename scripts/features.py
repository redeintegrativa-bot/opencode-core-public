#!/usr/bin/env python3
"""
OpenCode Core — Gerenciador de recursos opcionais (opt-in).

Cada recurso opcional (ex: monitoramento de rede, auto-update) precisa do
consentimento do usuario para funcionar. O estado fica em:
    ~/.config/opencode/features.json

Uso:
  python scripts/features.py list                     # mostra todos e o estado
  python scripts/features.py enable <nome>            # ativa um recurso
  python scripts/features.py disable <nome>           # desativa um recurso
  python scripts/features.py enable all               # ativa todos
  python scripts/features.py disable all              # desativa todos
  python scripts/features.py is-enabled <nome>        # exit 0 se ativo
"""
import json
import sys
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "opencode"
FEATURES_FILE = CONFIG_DIR / "features.json"

# Catalogo de recursos opcionais.
# "requires": componente/arquivo que o recurso precisa estar instalado.
FEATURES = {
    "network_watch": {
        "name": "Monitoramento de rede",
        "description": "Verifica dispositivos e eventos de seguranca na rede local a cada interacao",
        "requires": ["network-dashboard/scanner.py"],
    },
    "update_check": {
        "name": "Verificar atualizacoes",
        "description": "Avisa quando o repositorio publico tem novidades (a cada 6h)",
        "requires": ["opencode-core/scripts/check-update.py", "opencode-core-public/scripts/check-update.py"],
    },
    "ui_ux_toasts": {
        "name": "Notificacoes da sessao",
        "description": "Toasts de tarefa concluida, memoria salva, erros de sessao e ferramenta",
        "requires": ["opencode-core/plugins/ui-ux.js"],
    },
    "windows_toast": {
        "name": "Toast do Windows",
        "description": "Notificacoes tambem como toast do sistema (silencioso) em paralelo ao terminal",
        "requires": ["opencode-core/scripts/windows-toast.ps1"],
    },
    "toast_sounds": {
        "name": "Sons no terminal",
        "description": "Som distinto por tipo de notificacao (melodia de tons)",
        "requires": ["opencode-core/scripts/play-sound.ps1"],
    },
}

DEFAULTS = {
    "network_watch": False,
    "update_check": False,
    "ui_ux_toasts": True,
    "windows_toast": True,
    "toast_sounds": True,
}


def load():
    if FEATURES_FILE.exists():
        try:
            data = json.loads(FEATURES_FILE.read_text(encoding="utf-8"))
            return {**DEFAULTS, **data}
        except Exception:
            pass
    return dict(DEFAULTS)


def save(data):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    FEATURES_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def component_installed(rel):
    """Verifica se um componente esperado existe em ~."""
    home = Path.home()
    parts = rel.split("/")
    path = home.joinpath(*parts)
    return path.exists() or path.is_symlink()


def missing_components(key):
    """Retorna as alternativas de instalacao que faltam (lista de listas)."""
    groups = FEATURES[key].get("requires", [])
    if not groups:
        return []
    # requires pode ser uma lista de caminhos (alternativas: basta 1)
    if isinstance(groups[0], str):
        return [g for g in groups if not component_installed(g)] if not any(component_installed(g) for g in groups) else []
    return [g for g in groups if not any(component_installed(x) for x in g)]


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "list"

    if cmd == "list":
        data = load()
        if "--json" in args:
            payload = []
            for key, meta in FEATURES.items():
                payload.append({
                    "key": key,
                    "name": meta["name"],
                    "description": meta["description"],
                    "enabled": data.get(key, False),
                    "missing": missing_components(key),
                })
            print(json.dumps(payload, ensure_ascii=False))
            return
        print("Recursos opcionais:")
        print()
        for key, meta in FEATURES.items():
            enabled = data.get(key, False)
            marker = "[X]" if enabled else "[ ]"
            missing = missing_components(key)
            nota = f"  (componente ausente: {', '.join(missing)})" if missing else ""
            print(f"  {marker} {key:<15s} {meta['name']}")
            print(f"        {meta['description']}{nota}")
        print()
        ativos = [k for k in FEATURES if data.get(k)]
        print(f"Ativos: {', '.join(ativos) if ativos else 'nenhum'}")
        print(f"Arquivo: {FEATURES_FILE}")
        return

    if len(args) < 2:
        print("Uso: python scripts/features.py [list|enable|disable|is-enabled] <nome>")
        sys.exit(1)

    action, name = args[0], args[1]
    data = load()

    if name == "all":
        keys = list(FEATURES)
    elif name in FEATURES:
        keys = [name]
    else:
        print(f"Recurso desconhecido: {name}")
        print(f"Disponiveis: {', '.join(FEATURES)}")
        sys.exit(1)

    if action == "enable":
        for k in keys:
            missing = missing_components(k)
            if missing and k != "update_check":
                print(f"  [!] {k}: componente ausente ({', '.join(missing)}). Pulando.")
                continue
            data[k] = True
            print(f"  [+] {k} ativado")
        save(data)
    elif action == "disable":
        for k in keys:
            data[k] = False
            print(f"  [-] {k} desativado")
        save(data)
    elif action == "is-enabled":
        sys.exit(0 if data.get(name) else 1)
    else:
        print(f"Acao desconhecida: {action}")
        sys.exit(1)


if __name__ == "__main__":
    main()
