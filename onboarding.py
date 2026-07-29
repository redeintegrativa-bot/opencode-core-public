#!/usr/bin/env python3
import os
import sys
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent
CONFIG_DIR = Path.home() / ".config" / "opencode-core"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def select(question: str, options: list[str]) -> str:
    print(f"\n  \033[36m?\033[0m \033[1m{question}\033[0m")
    for i, opt in enumerate(options, 1):
        print(f"    {i}. {opt}")
    while True:
        try:
            choice = input("  > ").strip()
            if not choice:
                return options[0]
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx]
            print(f"  \033[31mOpcao invalida. Escolha 1-{len(options)}\033[0m")
        except (ValueError, EOFError, KeyboardInterrupt):
            print(f"  \033[31mDigite um numero de 1 a {len(options)}\033[0m")


def main():
    print("")
    print("  \033[1m+----------------------------------+\033[0m")
    print("  \033[1m| OpenCode Core - Onboarding        |\033[0m")
    print("  \033[1m| So 3 perguntas pra comecar!       |\033[0m")
    print("  \033[1m+----------------------------------+\033[0m")
    print("")
    print("  \033[33mIsso leva 10 segundos. Depois e so usar.\033[0m")
    print("")

    style = select(
        "Estilo de resposta?",
        [
            "Direto — vai direto ao ponto, sem rodeios",
            "Equilibrado — explica o necessário",
            "Didático — explica passo a passo",
            "Relaxado — informal, como um parceiro",
        ],
    )
    focus = select(
        "Foco principal?",
        [
            "Web",
            "Backend/API",
            "Automação/CLI",
            "Dados/ML",
            "Geral — um pouco de tudo",
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

    if "Direto" in style:
        tone = "direct"
    elif "Didático" in style:
        tone = "didatic"
    elif "Relaxado" in style:
        tone = "casual"
    else:
        tone = "balanced"

    if "Web" in focus:
        focus_code = "web"
    elif "Backend" in focus:
        focus_code = "backend"
    elif "Automação" in focus:
        focus_code = "cli"
    elif "Dados" in focus:
        focus_code = "data"
    else:
        focus_code = "general"

    verbosity = {"Iniciante": "high", "Intermediário": "medium", "Avançado": "low", "Expert": "low"}.get(level, "medium")

    agents_md = f"# ONBOARDING\nTONE={tone} FOCUS={focus_code} VERBOSITY={verbosity}\n"

    agents_file = CONFIG_DIR / "AGENTS.md"
    agents_file.write_text(agents_md, encoding="utf-8")

    tone_label = {
        "direct": "DIRETO",
        "balanced": "EQUILIBRADO",
        "didatic": "DIDÁTICO",
        "casual": "RELAXADO",
    }[tone]

    focus_label = {
        "web": "Web",
        "backend": "Backend/API",
        "cli": "Automação/CLI",
        "data": "Dados/ML",
        "general": "Geral",
    }[focus_code]

    verbosity_label = {"high": "alto (detalhado)", "medium": "médio", "low": "baixo (conciso)"}[verbosity]

    print("")
    print("  \033[1m+------------------------------------------+\033[0m")
    print("  \033[1m| Onboarding concluido!                     |\033[0m")
    print("  \033[1m+------------------------------------------+\033[0m")
    print(f"  \033[1m| Estilo:    [{tone_label:>11}]\033[0m")
    print(f"  \033[1m| Foco:      {focus_label:35s}\033[0m")
    print(f"  \033[1m| Detalhe:   {verbosity_label:35s}\033[0m")
    print("  \033[1m+------------------------------------------+\033[0m")
    print("")
    print(f"  \033[32mSalvo em: {agents_file}\033[0m")
    print("")
    print("  \033[1mPróximo passo:\033[0m  Rode  bash setup.sh")
    print("")
    print("  \033[33mDica: No chat, use /config pra mudar o estilo quando quiser.\033[0m")
    print("")


if __name__ == "__main__":
    main()
