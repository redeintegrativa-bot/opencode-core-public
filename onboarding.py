#!/usr/bin/env python3
import os
import sys
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent
CONFIG_DIR = Path.home() / ".config" / "opencode-core"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

V = '\033[32m'   # verde sucesso
C = '\033[36m'   # ciano destaque
A = '\033[33m'   # amarelo informacao
R = '\033[31m'   # vermelho erro
B = '\033[1m'    # negrito
S = '\033[0m'    # reset
G = '\033[90m'   # cinza legenda


def hdr(text, color=C):
    w = 50
    side = w - len(text) - 2
    if side < 2:
        side = 2
    print(f"  {color}{B}+{'-'*w}+{S}")
    print(f"  {color}{B}| {text}{' '*(w-1-len(text))}|{S}")
    print(f"  {color}{B}+{'-'*w}+{S}")
    print()


def feed(text, color=V):
    lines = text.split('\n')
    w = max(len(l) for l in lines) + 4
    print(f"  {color}+{'-'*w}+{S}")
    for l in lines:
        print(f"  {color}|  {l}{' '*(w-2-len(l))}|{S}")
    print(f"  {color}+{'-'*w}+{S}")
    print()


def sep():
    print(f"  {G}{'-'*50}{S}")
    print()


def opt(num, label, desc, example, color=C, tag=''):
    tag_str = f"  {G}{tag}{S}" if tag else ''
    print(f"  {color}{B}[{num}]{S} {B}{label}{S}{tag_str}")
    print(f"    {G}{example}{S}")
    print(f"    {G}| {desc}{S}")
    print()


def ask(options, default=1):
    while True:
        try:
            choice = input(f"\n  {C}>{S} ").strip()
            if not choice:
                return default - 1
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return idx
            print(f"  {R}Opcao invalida. Digite 1-{len(options)} ou Enter pra padrao.{S}")
        except (ValueError, EOFError, KeyboardInterrupt):
            print(f"  {R}Digite um numero de 1 a {len(options)}.{S}")


def main():
    print()
    hdr("OpenCode Core - Onboarding", C)
    cprint("Ola! Vou te fazer 3 perguntas rapidas pra", B)
    cprint("entender como voce gosta de receber ajuda.", B)
    print()
    cprint("Nao tem resposta errada.", A)
    cprint("Da pra mudar depois com /config.", A)
    print()
    input(f"  {C}{B}Pressione ENTER pra começar{S} ".ljust(10))
    print()

    # ── 1. ESTILO ──
    sep()
    cprint("PERGUNTA 1 DE 3", C)
    print()
    cprint("ESTILO DE RESPOSTA", B)
    cprint("Isso define como EU vou falar com voce.", G)
    print()
    print(f"  {A}{B}Voce perguntou:{S}  {G}\"Como criar uma rota GET /users?\"{S}")
    print()
    opt("1", "DIRETO",
        "Vai direto ao ponto, sem rodeios",
        '"Cria routes/users.js com handler GET."', V)
    opt("2", "EQUILIBRADO",
        "Explica o necessario, nem mais nem menos",
        '"Cria routes/users.js. Recomendo express.Router()."', C, "  <<< recomendado")
    opt("3", "DIDATICO",
        "Passo a passo detalhado, como se fosse a primeira vez",
        '"Passo 1: crie routes/users.js. Passo 2: adicione router.get..."', A)
    opt("4", "RELAXADO",
        "Informal, bem tranquilo, como um brother",
        '"Bora! Cria o arquivo e bota a rota la!"', R)
    print()
    cprint("Qual estilo prefere?", B)

    estilos = ["direct", "balanced", "didatic", "casual"]
    rotulos = ["DIRETO", "EQUILIBRADO", "DIDATICO", "RELAXADO"]
    explicacoes = [
        "Vou ser direto e objetivo. Respostas curtas e precisas.",
        "Vou explicar o necessario sem exageros.",
        "Vou explicar passo a passo, como se fosse a primeira vez.",
        "Vou ser informal e relaxado, como um parceiro de codigo.",
    ]
    i = ask(estilos, default=2)
    tone = estilos[i]
    print()
    feed(f"  {rotulos[i]} ativado!\n\n{explicacoes[i]}", V)

    # ── 2. FOCO ──
    sep()
    cprint("PERGUNTA 2 DE 3", C)
    print()
    cprint("FOCO PRINCIPAL", B)
    cprint("Isso ajuda a dar exemplos na SUA area.", G)
    print()
    opt("1", "WEB", "React, HTML, CSS, frontend", "Exemplo: componentes, hooks, estilos", V)
    opt("2", "BACKEND / API", "Servidores, banco de dados, rotas", "Exemplo: APIs REST, SQL, autenticacao", C, "  <<< recomendado")
    opt("3", "AUTOMACAO / CLI", "Scripts, shell, ferramentas de terminal", "Exemplo: scripts bash, pipelines", A)
    opt("4", "DADOS / ML", "Analise, pipelines, machine learning", "Exemplo: pandas, treinar modelo", R)
    opt("5", "GERAL", "Um pouco de tudo", "Exemplo: adapta ao contexto", G)
    print()
    cprint("Qual seu foco principal?", B)

    focos = ["web", "backend", "cli", "data", "general"]
    rotulos_f = ["WEB", "BACKEND / API", "AUTOMACAO / CLI", "DADOS / ML", "GERAL"]
    explicacoes_f = [
        "Vou dar exemplos com React, HTML, CSS e frameworks frontend.",
        "Vou dar exemplos com APIs, servidores, banco de dados e rotas.",
        "Vou dar exemplos com scripts, shell e automacao de terminal.",
        "Vou dar exemplos com analise de dados, pipelines e ML.",
        "Vou adaptar os exemplos ao contexto da conversa.",
    ]
    i = ask(focos, default=2)
    focus = focos[i]
    print()
    feed(f"  {rotulos_f[i]} ativado!\n\n{explicacoes_f[i]}", V)

    # ── 3. NIVEL ──
    sep()
    cprint("PERGUNTA 3 DE 3", C)
    print()
    cprint("NIVEL DE EXPERIENCIA", B)
    cprint("Isso define o nivel de detalhe das respostas.", G)
    print()
    opt("1", "INICIANTE",
        "Explica cada linha como se fosse a primeira vez",
        '"Vamos comecar criando um arquivo... agora dentro dele... "', V)
    opt("2", "INTERMEDIARIO",
        "Explica o necessario, sem exageros",
        '"Crie routes/users.js e adicione a rota..."', A)
    opt("3", "AVANCADO",
        "Vai direto, nao precisa explicar obviedades",
        '"Feito. routes/users.js, linha 12."', C, "  <<< recomendado")
    opt("4", "EXPERT",
        "So o codigo. Explicacao minima.",
        '"routes/users.js:12"', R)
    print()
    cprint("Qual seu nivel?", B)

    niveis = ["iniciante", "intermediario", "avancado", "expert"]
    verb_map = {"iniciante": "high", "intermediario": "medium", "avancado": "low", "expert": "low"}
    rotulos_n = ["INICIANTE", "INTERMEDIARIO", "AVANCADO", "EXPERT"]
    explicacoes_n = [
        "Vou explicar cada detalhe, sem presumir conhecimento previo.",
        "Vou explicar o necessario, sem exagerar.",
        "Vou ser conciso, mostrando o codigo direto.",
        "Vou ser minimalista. Explicacao so quando pedir.",
    ]
    i = ask(list(verb_map.keys()), default=3)
    verbosity = verb_map[niveis[i]]
    print()
    feed(f"  {rotulos_n[i]} ativado!\n\n{explicacoes_n[i]}", V)

    # ── Salvar ──
    agents_md = f"# ONBOARDING\nTONE={tone} FOCUS={focus} VERBOSITY={verbosity}\n"
    (CONFIG_DIR / "AGENTS.md").write_text(agents_md, encoding="utf-8")

    # ── Resumo final ──
    print()
    hdr("Onboarding concluido!", V)

    tone_r = {"direct": "DIRETO", "balanced": "EQUILIBRADO", "didatic": "DIDATICO", "casual": "RELAXADO"}[tone]
    focus_r = {"web": "WEB", "backend": "BACKEND / API", "cli": "AUTOMACAO / CLI", "data": "DADOS / ML", "general": "GERAL"}[focus]
    verb_r = {"high": "Alto (detalhado)", "medium": "Medio", "low": "Baixo (conciso)"}[verbosity]

    print(f"  {V}+{'-'*50}+{S}")
    print(f"  {V}|  ESTILO       [ {tone_r:<12} ]{' ' * 20}|{S}")
    print(f"  {V}|  FOCO         {focus_r:<40}|{S}")
    print(f"  {V}|  DETALHE      {verb_r:<40}|{S}")
    print(f"  {V}+{'-'*50}+{S}")
    print()

    cprint(f"Config salva em: {CONFIG_DIR / 'AGENTS.md'}", G)
    cprint("(2 linhas, ~20 tokens)", G)
    print()
    sep()
    cprint("PROXIMO PASSO:", B)
    cprint("  bash setup.sh", A)
    print()
    cprint("Quer mudar depois?", G)
    cprint("  No chat, digite:  /config", C)
    print()


def cprint(text, color=''):
    print(f"  {color}{text}{S}")


if __name__ == "__main__":
    main()
