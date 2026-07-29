#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import threading
import time
import urllib.request
import urllib.error
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent
CONFIG_DIR = Path.home() / ".config" / "opencode-core"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

V = '\033[32m'; C = '\033[36m'; A = '\033[33m'
R = '\033[31m'; B = '\033[1m'; S = '\033[0m'; G = '\033[90m'


def cprint(text, color=''):
    print(f"  {color}{text}{S}")


def hdr(text, color=C):
    w = 50
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


def save_config(tone, focus, verbosity):
    agents_md = f"# ONBOARDING\nTONE={tone} FOCUS={focus} VERBOSITY={verbosity}\n"
    (CONFIG_DIR / "AGENTS.md").write_text(agents_md, encoding="utf-8")


def show_summary(tone, focus, verbosity):
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


def onboard_console():
    print()
    hdr("OpenCode Core - Onboarding", C)
    cprint("Vou te fazer 3 perguntas rapidas pra", B)
    cprint("entender como voce gosta de receber ajuda.", B)
    print()
    cprint("Nao tem resposta errada.", A)
    cprint("Da pra mudar depois com /config.", A)
    print()
    input(f"  {C}{B}Pressione ENTER pra comecar{S} ".ljust(10))
    print()

    # 1. ESTILO
    sep()
    cprint("PERGUNTA 1 DE 3", C)
    print()
    cprint("ESTILO DE RESPOSTA", B)
    cprint("Isso define como EU vou falar com voce.", G)
    print()
    print(f"  {A}{B}Voce perguntou:{S}  {G}\"Como criar uma rota GET /users?\"{S}")
    print()
    opt("1", "DIRETO", "Vai direto ao ponto, sem rodeios",
        '"Cria routes/users.js com handler GET."', V)
    opt("2", "EQUILIBRADO", "Explica o necessario, nem mais nem menos",
        '"Cria routes/users.js. Recomendo express.Router()."', C, "  <<< recomendado")
    opt("3", "DIDATICO", "Passo a passo detalhado, como se fosse a primeira vez",
        '"Passo 1: crie routes/users.js. Passo 2: adicione router.get..."', A)
    opt("4", "RELAXADO", "Informal, bem tranquilo, como um brother",
        '"Bora! Cria o arquivo e bota a rota la!"', R)
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

    # 2. FOCO
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

    # 3. NIVEL
    sep()
    cprint("PERGUNTA 3 DE 3", C)
    print()
    cprint("NIVEL DE EXPERIENCIA", B)
    cprint("Isso define o nivel de detalhe das respostas.", G)
    print()
    opt("1", "INICIANTE", "Explica cada linha como se fosse a primeira vez",
        '"Vamos comecar criando um arquivo... agora dentro dele... "', V)
    opt("2", "INTERMEDIARIO", "Explica o necessario, sem exageros",
        '"Crie routes/users.js e adicione a rota..."', A)
    opt("3", "AVANCADO", "Vai direto, nao precisa explicar obviedades",
        '"Feito. routes/users.js, linha 12."', C, "  <<< recomendado")
    opt("4", "EXPERT", "So o codigo. Explicacao minima.",
        '"routes/users.js:12"', R)
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

    save_config(tone, focus, verbosity)
    show_summary(tone, focus, verbosity)


def onboard_browser():
    print()
    hdr("OpenCode Core - Dashboard", A)
    cprint("Vou iniciar o servidor web pra voce configurar", B)
    cprint("pelo navegador.", B)
    print()

    server_script = str(REPO_DIR / "dashboard" / "server.py")
    port = 8080

    try:
        proc = subprocess.Popen(
            [sys.executable, server_script, "--port", str(port)],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )
    except Exception as e:
        cprint(f"Erro ao iniciar servidor: {e}", R)
        cprint("Tente: python dashboard/server.py", A)
        sys.exit(1)

    time.sleep(1.5)

    print(f"  {V}+{'-'*50}+{S}")
    print(f"  {V}|  Servidor rodando!                         |{S}")
    print(f"  {V}|                                          |{S}")
    print(f"  {V}|  Acesse: {C}http://localhost:{port}{V}             |{S}")
    print(f"  {V}|  Clique em 'Configurar' pra fazer o      |{S}")
    print(f"  {V}|  onboarding pelo navegador.               |{S}")
    print(f"  {V}|                                          |{S}")
    print(f"  {V}|  Para parar: pressione ENTER aqui        |{S}")
    print(f"  {V}+{'-'*50}+{S}")
    print()

    try:
        input()
    except (EOFError, KeyboardInterrupt):
        pass
    finally:
        proc.terminate()
        proc.wait(timeout=3)
        cprint("Servidor encerrado.", G)


def check_version():
    vf = REPO_DIR / "VERSION"
    if not vf.exists():
        return
    local = vf.read_text(encoding="utf-8").strip()
    try:
        url = "https://raw.githubusercontent.com/redeintegrativa-bot/opencode-core-public/master/VERSION"
        req = urllib.request.Request(url, headers={"User-Agent": "opencode-core/1.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            remote = resp.read().decode().strip()
        def v(s):
            return tuple(int(x) for x in s.split("."))
        if v(remote) > v(local):
            print()
            cprint(f"[!] Atualizacao disponivel: {local} -> {remote}", A)
            try:
                choice = input(f"  {C}Atualizar agora?{S} [S/n] ").strip().lower()
                if choice in ("", "s", "sim", "y", "yes"):
                    subprocess.run([sys.executable, str(REPO_DIR / "scripts" / "update.py")])
            except (EOFError, KeyboardInterrupt):
                print()
            print()
    except Exception:
        pass


def main():
    check_version()
    print()
    hdr("OpenCode Core - Onboarding", C)
    cprint("Como voce quer configurar o assistente?", B)
    print()
    opt("1", "CONSOLE", "Configurar direto no terminal, com dialogos passo a passo",
        "Recomendado pra primeira vez", V, "  <<< recomendado")
    opt("2", "NAVEGADOR", "Configurar pelo browser com formulario web",
        "Inicia o dashboard em http://localhost:8080", A)
    print()
    cprint("Escolha uma opcao [1-2, Enter=1]:", B)

    i = ask(["console", "browser"], default=1)

    if i == 0:
        onboard_console()
    else:
        onboard_browser()


if __name__ == "__main__":
    main()
