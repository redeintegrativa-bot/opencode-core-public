#!/usr/bin/env python3
"""
OpenCode Core — Onboarding Interativo (Python)

Faz perguntas para personalizar a experiência do usuário e gera
configurações sob medida. Funciona em Termux, Linux, Windows, macOS.

Uso:
    python onboarding.py
    python3 onboarding.py
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent
CONFIG_DIR = Path.home() / ".config" / "opencode-core"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def ask(question: str, default: str = "") -> str:
    print(f"\n  \033[36m?\033[0m \033[1m{question}\033[0m")
    try:
        answer = input("  \u2192 ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)
    return answer or default


def select(question: str, options: list[str]) -> str:
    print(f"\n  \033[36m?\033[0m \033[1m{question}\033[0m")
    for i, opt in enumerate(options, 1):
        print(f"    {i}. {opt}")
    while True:
        try:
            choice = input("  \u2192 ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx]
            print(f"  \033[31mOpção inválida. Escolha 1-{len(options)}\033[0m")
        except (ValueError, EOFError, KeyboardInterrupt):
            if not choice:
                return options[0]
            print(f"  \033[31mDigite um número de 1 a {len(options)}\033[0m")


def main():
    print("")
    print("  \033[1m╔══════════════════════════════════════════╗\033[0m")
    print("  \033[1m║     OpenCode Core — Onboarding           ║\033[0m")
    print("  \033[1m║     Vamos configurar tudo pra você!      ║\033[0m")
    print("  \033[1m╚══════════════════════════════════════════╝\033[0m")
    print("")
    print("  \033[33mSão 8 perguntas rápidas. Responda como preferir.\033[0m")
    print("")

    # ── Questions ──
    name = ask("Como quer ser chamado?", "Dev")
    lang = select("Idioma preferido?", ["Português", "English", "Español"])
    style = select(
        "Estilo de resposta do assistente?",
        [
            "Direto e seco — vai direto ao ponto",
            "Equilibrado — explica o necessário",
            "Didático — explica passo a passo",
            "Relaxado — informal, como um parceiro",
        ],
    )
    level = select(
        "Seu nível de experiência?",
        [
            "Iniciante — nunca programou",
            "Intermediário — já faz projetos",
            "Avançado — dev profissional",
            "Expert — arquiteto/sênior",
        ],
    )
    focus = select(
        "Foco principal?",
        [
            "Desenvolvimento Web",
            "Backend/API",
            "Automação/CLI",
            "Segurança",
            "Dados/ML",
            "Geral — um pouco de tudo",
        ],
    )
    terminal = select(
        "Onde vai usar o OpenCode?",
        ["Termux (Android)", "Linux", "Windows PowerShell", "macOS"],
    )
    finance = select(
        "Quer usar o app de controle financeiro (My Money Track)?",
        ["Sim, quero organizar minhas finanças", "Talvez depois", "Não, obrigado"],
    )

    # ── Process answers ──
    if "Direto" in style:
        tone = "direct"
        tone_desc = "Seja direto e objetivo. Vá direto ao ponto sem rodeios. Respostas curtas e precisas."
        tone_tag = "DIRETO"
    elif "Didático" in style:
        tone = "didatic"
        tone_desc = "Explique passo a passo. Seja didático e didático. Inclua exemplos."
        tone_tag = "DIDÁTICO"
    elif "Relaxado" in style:
        tone = "casual"
        tone_desc = "Seja informal e relaxado. Use gírias, seja amigável. Trate como um parceiro de código."
        tone_tag = "RELAXADO"
    else:
        tone = "balanced"
        tone_desc = "Explique o necessário sem exageros. Equilíbrio entre ser direto e ser completo."
        tone_tag = "EQUILIBRADO"

    lang_code = {"Português": "pt", "English": "en", "Español": "es"}[lang]
    lang_rule = {
        "Português": "Responda em português.",
        "English": "Respond in English.",
        "Español": "Responde en español.",
    }[lang]

    verbosity = {"Iniciante": "high", "Intermediário": "medium", "Avançado": "low", "Expert": "low"}.get(level, "medium")

    wants_finance = finance.startswith("Sim") or finance == "Talvez depois"

    # ── Generate AGENTS.md ──
    agents_md = f"""# AGENTS.md — Personalizado para {name}

{lang_rule}
{tone_desc}

## Perfil
- **Nome:** {name}
- **Nível:** {level}
- **Foco:** {focus}
- **Terminal:** {terminal}
- **Estilo:** [{tone_tag}] {style}

## Comandos Rápidos
- `/help` — Ajuda
- `/status` — Status do sistema
- `/plan` — Planejar implementação
- `/review` — Revisar código
- `/fix` — Corrigir bug
- `/scaffold` — Criar projeto do zero
- `/database` — Ajuda com banco de dados
- `/security-scan` — Auditoria de segurança
- `/tdd` — Desenvolvimento orientado a testes

## Regras
- Mantenha o estilo de resposta conforme definido acima
- Use a linguagem definida ({lang})
- Adapte o nível de detalhe ao perfil do usuário
- Code primeiro, explicação depois (quando aplicável)
"""

    # ── Generate profile JSON ──
    profile = {
        "name": name,
        "language": lang_code,
        "tone": tone,
        "tone_tag": tone_tag,
        "level": level,
        "focus": focus,
        "terminal": terminal,
        "finance_app": wants_finance,
        "verbosity": verbosity,
        "onboarded_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    # ── Save ──
    agents_file = CONFIG_DIR / "AGENTS.md"
    profile_file = CONFIG_DIR / "profile.json"

    agents_file.write_text(agents_md, encoding="utf-8")
    profile_file.write_text(json.dumps(profile, indent=2, ensure_ascii=False), encoding="utf-8")

    # ── Summary ──
    print("")
    print("  \033[1m╔══════════════════════════════════════════╗\033[0m")
    print("  \033[1m║  Onboarding concluído! 🎉                ║\033[0m")
    print("  \033[1m╠══════════════════════════════════════════╣\033[0m")
    print(f"  \033[1m║  Nome:      {name:35s}\033[0m")
    print(f"  \033[1m║  Idioma:    {lang:35s}\033[0m")
    print(f"  \033[1m║  Estilo:    [{tone_tag}]\033[0m")
    print(f"  \033[1m║  Nível:     {level:35s}\033[0m")
    print(f"  \033[1m║  Foco:      {focus:35s}\033[0m")
    print(f"  \033[1m║  Terminal:  {terminal:35s}\033[0m")
    print("  \033[1m╚══════════════════════════════════════════╝\033[0m")
    print("")
    print(f"  \033[32mConfiguração salva em:\033[0m")
    print(f"    {agents_file}")
    print(f"    {profile_file}")
    print("")
    print("  \033[1mPróximos passos:\033[0m")
    print("")
    print("  1. Rode o setup:  bash setup.sh")
    print("  2. Inicie o chat: cd terminal-chat && python opencode_chat.py")
    if wants_finance:
        print("  3. My Money Track: cd my-money-track && npm install && npm run dev")
    print("")
    print("  \033[33m💡 O AGENTS.md personalizado já guia o OpenCode no seu estilo!\033[0m")
    print("")


if __name__ == "__main__":
    main()
