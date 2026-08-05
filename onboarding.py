#!/usr/bin/env python3
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent
CONFIG_DIR = Path.home() / ".config" / "opencode"
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


# ---------------------------------------------------------------------------
# Modos de permissao e recursos opcionais
# ---------------------------------------------------------------------------

def read_opencode_json():
    path = CONFIG_DIR / "opencode.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_opencode_json(cfg):
    path = CONFIG_DIR / "opencode.json"
    path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


PERMISSION_MODES = {
    "full": {
        "label": "ACESSO TOTAL",
        "desc": "Tudo liberado. Eu executo scans, leio arquivos e instalo coisas sem perguntar a cada acao.",
        "config": {"*": "allow"},
    },
    "balanced": {
        "label": "EQUILIBRADO",
        "desc": "Comandos basicos (git, pip, node) rodam sozinhos; o resto pergunta antes.",
        "config": {
            "*": "ask",
            "bash": {"*": "ask",
                     "git *": "allow",
                     "pip *": "allow",
                     "pip3 *": "allow",
                     "npm *": "allow",
                     "node *": "allow",
                     "python *": "allow",
                     "python3 *": "allow",
                     "ls *": "allow",
                     "pwd": "allow",
                     "cat *": "allow",
                     "echo *": "allow"},
            "read": "allow",
            "glob": "allow",
            "grep": "allow",
            "webfetch": "allow",
            "websearch": "allow",
        },
    },
    "strict": {
        "label": "APROVAR SEMPRE",
        "desc": "Toda acao pede sua aprovacao. Maximo controle, mais interrompido.",
        "config": {"*": "ask"},
    },
}


def apply_permission_mode(mode):
    """Grava o modo de permissao no opencode.json preservando o resto."""
    cfg = read_opencode_json()
    cfg["permission"] = PERMISSION_MODES[mode]["config"]
    write_opencode_json(cfg)
    return cfg


def get_available_features():
    """Lista os recursos opcionais via scripts/features.py --json."""
    checker = REPO_DIR / "scripts" / "features.py"
    if not checker.exists():
        return []
    try:
        r = subprocess.run(
            [sys.executable, str(checker), "list", "--json"],
            capture_output=True, text=True, timeout=15
        )
        if r.returncode == 0 and r.stdout.strip():
            return json.loads(r.stdout)
    except Exception:
        pass
    return []


def toggle_feature(name, enabled):
    checker = REPO_DIR / "scripts" / "features.py"
    action = "enable" if enabled else "disable"
    try:
        subprocess.run([sys.executable, str(checker), action, name],
                       capture_output=True, text=True, timeout=15)
    except Exception:
        pass


def ask_permission_mode():
    sep()
    cprint("PERGUNTA 4 DE 5", C)
    print()
    cprint("COMO QUER QUE EU PERGUNTE?", B)
    cprint("Define quanto eu posso executar sem te incomodar.", G)
    print()
    opt("1", "ACESSO TOTAL", "Executo tudo sozinho: scans de rede, leitura, instalacao",
        '"Pode fazer o que precisar."', V)
    opt("2", "EQUILIBRADO", "Basico rodando sozinho, resto pergunta",
        '"Git e pip liberados; o resto pergunte."', C, "  <<< recomendado")
    opt("3", "APROVAR SEMPRE", "Toda acao pede sua aprovacao",
        '"Me mostra antes de executar."', A)
    cprint("Como prefere?", B)

    modos = list(PERMISSION_MODES.keys())
    i = ask(modos, default=2)
    mode = modos[i]
    apply_permission_mode(mode)
    print()
    feed(f"  {PERMISSION_MODES[mode]['label']} ativado!\n\n{PERMISSION_MODES[mode]['desc']}", V)
    return mode


def ask_optional_features():
    features = get_available_features()
    if not features:
        return []

    sep()
    cprint("PERGUNTA 5 DE 5", C)
    print()
    cprint("RECURSOS OPCIONAIS", B)
    cprint("Ferramentas extras que so ativam com seu consentimento.", G)
    print()

    enabled = []
    for idx, f in enumerate(features, start=1):
        opt(str(idx), f["name"].upper(), f["description"], "", color=V)
        cprint(f"    Ativar? [s/N]", B)
        try:
            resp = input(f"  {C}>{S} ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            resp = "n"
        if resp in ("s", "sim", "y", "yes"):
            toggle_feature(f["key"], True)
            enabled.append(f["key"])
            print(f"  {V}  [+] {f['name']} ativado{S}")
        print()

    if not enabled:
        cprint("Nenhum recurso opcional ativado. Da pra ativar depois com:", G)
        cprint("  python scripts/features.py enable <nome>", C)
        print()
    return enabled


def show_summary(tone, focus, verbosity, mode=None, features=None):
    print()
    hdr("Onboarding concluido!", V)

    tone_r = {"direct": "DIRETO", "balanced": "EQUILIBRADO", "didatic": "DIDATICO", "casual": "RELAXADO"}[tone]
    focus_r = {"web": "WEB", "backend": "BACKEND / API", "cli": "AUTOMACAO / CLI", "data": "DADOS / ML", "general": "GERAL"}[focus]
    verb_r = {"high": "Alto (detalhado)", "medium": "Medio", "low": "Baixo (conciso)"}[verbosity]

    print(f"  {V}+{'-'*50}+{S}")
    print(f"  {V}|  ESTILO       [ {tone_r:<12} ]{' ' * 20}|{S}")
    print(f"  {V}|  FOCO         {focus_r:<40}|{S}")
    print(f"  {V}|  DETALHE      {verb_r:<40}|{S}")
    if mode:
        perm_label = PERMISSION_MODES[mode]["label"]
        print(f"  {V}|  PERMISSAO    {perm_label:<40}|{S}")
    if features:
        feats_r = ", ".join(f.upper() for f in features)
        print(f"  {V}|  RECURSOS     {feats_r:<40}|{S}")
    elif features is not None:
        print(f"  {V}|  RECURSOS     nenhum opcional ativado{' ' * 15}|{S}")
    print(f"  {V}+{'-'*50}+{S}")
    print()
    cprint(f"Config salva em: {CONFIG_DIR / 'AGENTS.md'}", G)
    cprint(f"Permissoes em:   {CONFIG_DIR / 'opencode.json'}", G)
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
    cprint("Vou te fazer 5 perguntas rapidas pra", B)
    cprint("entender como voce gosta de receber ajuda.", B)
    print()
    cprint("Nao tem resposta errada.", A)
    cprint("Da pra mudar depois com /config.", A)
    print()

    # 1. ESTILO
    sep()
    cprint("PERGUNTA 1 DE 5", C)
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
    cprint("PERGUNTA 2 DE 5", C)
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
    cprint("PERGUNTA 3 DE 5", C)
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

    # 4. PERMISSOES
    mode = ask_permission_mode()

    # 5. RECURSOS OPCIONAIS
    enabled = ask_optional_features()

    show_summary(tone, focus, verbosity, mode, enabled)


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
            sep()
            cprint(f"[!] Atualizacao disponivel: {local} -> {remote}", A)
            cprint(f"    Para atualizar: make update", G)
            sep()
    except Exception:
        pass


def main():
    check_version()

    config_file = CONFIG_DIR / "AGENTS.md"
    if config_file.exists():
        print()
        cprint("Ja configurado!", V)
        cprint("Para mudar suas preferencias, mande /config no OpenCode.", G)
        cprint("Ou abra o dashboard:  python dashboard/server.py", G)
        print()
        return

    onboard_console()


if __name__ == "__main__":
    main()
