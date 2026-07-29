#!/usr/bin/env python3
import json
import os
import re
import subprocess
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

REPO_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = Path.home() / ".config" / "opencode"
HOST = "0.0.0.0"
PORT = 8080


def get_config():
    agents_file = CONFIG_DIR / "AGENTS.md"
    if not agents_file.exists():
        return {"onboarded": False}
    try:
        text = agents_file.read_text(encoding="utf-8").strip()
        config = {"onboarded": True}
        for line in text.split("\n"):
            if line.startswith("TONE="):
                parts = line.strip().split()
                for p in parts:
                    if "=" in p:
                        k, v = p.split("=", 1)
                        config[k.lower()] = v
        return config
    except Exception:
        return {"onboarded": False, "error": str(sys.exc_info()[1])}


def count_dir(path, ext=None, recursive=True):
    if not path.exists():
        return 0
    if ext == "skill":
        return len([d for d in path.iterdir() if d.is_dir() and (d / "SKILL.md").exists()])
    if ext:
        globber = path.rglob if recursive else path.glob
        return len(list(globber(f"*.{ext}")))
    return len(list(path.iterdir()))


def count_rules_individual(path):
    count = 0
    if not path.exists():
        return 0
    for f in path.rglob("*.md"):
        if f.name == "README.md":
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
            count += len(re.findall(r'^##\s+', text, re.MULTILINE))
        except Exception:
            pass
    return count


def check_command(cmd):
    try:
        subprocess.run([cmd, "--version"], capture_output=True, timeout=5)
        return True
    except Exception:
        return False


def get_capabilities():
    return {
        "categories": [
            {
                "name": "Criar & Gerar",
                "icon": "rocket",
                "items": [
                    {
                        "cmd": "/scaffold",
                        "title": "Criar projeto do zero",
                        "desc": "Gera projetos prontos: Next.js, Vite, FastAPI, Express, CLI Python, HTML/CSS.",
                        "example": 'Você: "Quero um projeto Next.js com TypeScript e Tailwind"\n→ O assistente cria a estrutura completa pra você.',
                        "try": "/scaffold nextjs-ts my-app",
                    },
                    {
                        "cmd": "/clone",
                        "title": "Clonar repositorio",
                        "desc": "Clona repos do GitHub automaticamente quando necessario.",
                        "example": 'Você: "Clona o repo do Express"\n→ O assistente baixa e ja deixa pronto.',
                        "try": "/clone expressjs/express",
                    },
                ],
            },
            {
                "name": "Revisar & Melhorar",
                "icon": "search",
                "items": [
                    {
                        "cmd": "/review",
                        "title": "Revisar codigo",
                        "desc": "Revisao como um staff engineer. Aponta bugs, security holes, e melhorias.",
                        "example": 'Você: "Revisa esse arquivo server.js"\n→ O assistente analisa linha a linha e sugere melhorias.',
                        "try": "/review server.js",
                    },
                    {
                        "cmd": "/refactor",
                        "title": "Refatorar codigo",
                        "desc": "Aplica clean code, solid, design patterns pra deixar o codigo mais limpo.",
                        "example": 'Você: "Refatora esse componente React"\n→ O assistente reestrutura o codigo.',
                        "try": "/refactor src/components/UserList.tsx",
                    },
                    {
                        "cmd": "/simplify",
                        "title": "Simplificar codigo",
                        "desc": "Remove duplicacao, melhora legibilidade e performance.",
                        "example": 'Você: "Simplifica essa funcao"\n→ O assistente deixa mais enxuta.',
                        "try": "/simplify utils/format.js",
                    },
                ],
            },
            {
                "name": "Debug & Corrigir",
                "icon": "bug",
                "items": [
                    {
                        "cmd": "/debug",
                        "title": "Depurar erros",
                        "desc": "Analise sistematica de causa raiz. Segue o erro ate achar a origem.",
                        "example": 'Você: "O app nao roda, da erro 500"\n→ O assistente investiga logs, stack trace e acha a causa.',
                        "try": "/debug",
                    },
                    {
                        "cmd": "/fix",
                        "title": "Corrigir bug",
                        "desc": "Corrige bugs especificos com analise de impacto.",
                        "example": 'Você: "O login quebrou depois da ultima alteracao"\n→ O assistente identifica e corrige.',
                        "try": "/fix O formulario de login nao valida email",
                    },
                    {
                        "cmd": "/build-fix",
                        "title": "Corrigir build",
                        "desc": "Diagnostico e correcao de erros de compilacao e build.",
                        "example": 'Você: "O build quebrou com erro de dependencia"\n→ O assistente resolve o conflito.',
                        "try": "/build-fix",
                    },
                ],
            },
            {
                "name": "Planejar & Projetar",
                "icon": "map",
                "items": [
                    {
                        "cmd": "/plan",
                        "title": "Planejar implementacao",
                        "desc": "Quebra uma feature em etapas, define arquitetura e suggests tecnologias.",
                        "example": 'Você: "Quero um sistema de autenticacao"\n→ O assistente cria o plano completo: rotas, banco, middleware.',
                        "try": "/plan sistema de autenticacao com JWT",
                    },
                    {
                        "cmd": "/multi-plan",
                        "title": "Comparar abordagens",
                        "desc": "Mostra multiplas formas de resolver o mesmo problema com pros e contras.",
                        "example": 'Você: "Qual a melhor forma de cache?"\n→ O assistente compara Redis, in-memory, CDN.',
                        "try": "/multi-plan",
                    },
                ],
            },
            {
                "name": "Seguranca",
                "icon": "lock",
                "items": [
                    {
                        "cmd": "/security-scan",
                        "title": "Auditoria de seguranca",
                        "desc": "Varre o codigo procurando vulnerabilidades OWASP, vazamento de secrets, SQL injection.",
                        "example": 'Você: "Verifica seguranca do projeto"\n→ O assistente escaneia e reporta riscos.',
                        "try": "/security-scan",
                    },
                    {
                        "cmd": None,
                        "title": "Hooks de pre-commit",
                        "desc": "Scripts que rodam automaticamente antes de cada commit para evitar vazamento de tokens.",
                        "example": "Ao rodar git commit, o hook validate_security.py verifica se ha senhas no codigo.",
                        "try": "python hooks/validate_security.py .",
                    },
                ],
            },
            {
                "name": "Testes",
                "icon": "check",
                "items": [
                    {
                        "cmd": "/tdd",
                        "title": "TDD workflow",
                        "desc": "Desenvolvimento orientado a testes: primeiro o teste, depois o codigo.",
                        "example": 'Você: "Faz TDD pra essa funcao de calculo"\n→ O assistente cria os testes primeiro, depois implementa.',
                        "try": "/tdd",
                    },
                    {
                        "cmd": "/test",
                        "title": "Estrategia de testes",
                        "desc": "Sugere cobertura, tipos de teste e ferramentas pro seu projeto.",
                        "example": 'Você: "Preciso de testes pra essa API"\n→ O assistente sugere jest, supertest, mocks.',
                        "try": "/test",
                    },
                ],
            },
            {
                "name": "Banco de Dados",
                "icon": "database",
                "items": [
                    {
                        "cmd": "/database",
                        "title": "Ajuda com banco de dados",
                        "desc": "SQL queries, models, migrations, otimizacao e design de schema.",
                        "example": 'Você: "Cria uma tabela de usuarios com SQLite"\n→ O assistente gera o schema e a migration.',
                        "try": "/database criar tabela usuarios com nome email e senha",
                    },
                ],
            },
            {
                "name": "UI/UX & Design",
                "icon": "palette",
                "items": [
                    {
                        "cmd": "/ui-design",
                        "title": "Design system",
                        "desc": "Componentes com Tailwind, Radix, Framer Motion, acessiveis e responsivos.",
                        "example": 'Você: "Cria um modal de confirmacao"\n→ O assistente gera o componente completo com animacao.',
                        "try": "/ui-design criar um modal de confirmacao",
                    },
                ],
            },
            {
                "name": "Sistema & Utilidades",
                "icon": "tool",
                "items": [
                    {
                        "cmd": "/status",
                        "title": "Status do sistema",
                        "desc": "Mostra metricas da sessao, health check e estatisticas de uso.",
                        "try": "/status",
                    },
                    {
                        "cmd": "/config",
                        "title": "Mudar configuracao",
                        "desc": "Altera estilo, foco ou verbosidade sem refazer o onboarding.",
                        "try": "/config tone=casual",
                    },
                    {
                        "cmd": "/compact",
                        "title": "Economizar tokens",
                        "desc": "Comprime o contexto da sessao pra gastar menos tokens.",
                        "try": "/compact",
                    },
                    {
                        "cmd": "/checkpoint",
                        "title": "Salvar sessao",
                        "desc": "Salva o estado atual pra continuar depois.",
                        "try": "/checkpoint",
                    },
                ],
            },
        ]
    }


def get_status():
    config = get_config()

    agents_core = count_dir(REPO_DIR / "agents" / "core", "md", recursive=False)
    agents_experts = count_dir(REPO_DIR / "agents" / "experts", "md", recursive=False)
    agents_specialists = count_dir(REPO_DIR / "agents" / "experts" / "L2", "md", recursive=False)
    agents_system = count_dir(REPO_DIR / "agents" / "system", "md", recursive=False)
    skills_count = count_dir(REPO_DIR / "skills", "skill")
    rules_count = count_rules_individual(REPO_DIR / "rules")
    hooks_count = count_dir(REPO_DIR / "hooks")

    return {
        "config": config,
        "stats": {
            "agents": {
                "total": agents_core + agents_experts + agents_specialists + agents_system,
                "core": agents_core,
                "experts": agents_experts,
                "specialists": agents_specialists,
                "system": agents_system,
            },
            "skills": skills_count,
            "rules": rules_count,
            "hooks": hooks_count,
        },
        "dependencies": {
            "python": check_command("python3") or check_command("python"),
            "node": check_command("node"),
            "git": check_command("git"),
        },
    }


class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/status":
            self._json(get_status())
            return
        if parsed.path == "/api/capabilities":
            self._json(get_capabilities())
            return
        if parsed.path == "/api/version":
            vf = REPO_DIR / "VERSION"
            version = vf.read_text(encoding="utf-8").strip() if vf.exists() else "0.0.0"
            self._json({"version": version, "repo": "redeintegrativa-bot/opencode-core-public"})
            return

        if parsed.path == "/api/check-update":
            try:
                result = subprocess.run(
                    [sys.executable, str(REPO_DIR / "scripts" / "check-update.py"), "--json"],
                    capture_output=True, text=True, timeout=15
                )
                if result.returncode == 0 and result.stdout.strip():
                    self._json(json.loads(result.stdout))
                else:
                    self._json({"error": "check-update failed", "stderr": result.stderr}, status=500)
            except Exception as e:
                self._json({"error": str(e)}, status=500)
            return

        if parsed.path == "/":
            self.path = "/dashboard/index.html"
        elif parsed.path == "/onboarding":
            self.path = "/dashboard/onboarding-web.html"

        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/config/save":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode()
            try:
                data = json.loads(body)
                tone = data.get("tone", "balanced")
                focus = data.get("focus", "general")
                verbosity = data.get("verbosity", "medium")

                agents_md = f"# ONBOARDING\nTONE={tone} FOCUS={focus} VERBOSITY={verbosity}\n"
                config_file = CONFIG_DIR / "AGENTS.md"
                config_file.parent.mkdir(parents=True, exist_ok=True)
                config_file.write_text(agents_md, encoding="utf-8")

                self._json({"success": True, "file": str(config_file), "config": {"tone": tone, "focus": focus, "verbosity": verbosity}})
            except Exception as e:
                self._json({"success": False, "error": str(e)}, status=400)
            return

        if parsed.path == "/api/update":
            try:
                result = subprocess.run(
                    [sys.executable, str(REPO_DIR / "scripts" / "update.py")],
                    capture_output=True, text=True, timeout=120
                )
                self._json({"success": result.returncode == 0, "stdout": result.stdout, "stderr": result.stderr})
            except Exception as e:
                self._json({"success": False, "error": str(e)}, status=500)
            return

        self._json({"success": False, "error": "Not found"}, status=404)

    def _json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, ensure_ascii=False).encode())

    def log_message(self, format, *args):
        msg = format % args
        print(f"  {msg}")


def check_update_startup():
    try:
        result = subprocess.run(
            [sys.executable, str(REPO_DIR / "scripts" / "check-update.py"), "--json"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            if data.get("has_update"):
                print(f"  [!] Atualizacao disponivel: {data['local']} -> {data['remote']}")
                print(f"      Abra o dashboard ou rode: make update")
                print()
    except Exception:
        pass


def main():
    os.chdir(str(REPO_DIR))
    check_update_startup()

    try:
        server = HTTPServer((HOST, PORT), DashboardHandler)
    except OSError:
        print(f"  Erro: porta {PORT} em uso. Tente:")
        print(f"    python dashboard/server.py --port=8081")
        sys.exit(1)

    print()
    print(f"  +------------------------------------------+")
    print(f"  |  OpenCode Core Dashboard                  |")
    print(f"  |                                          |")
    print(f"  |  Acesse: http://localhost:{PORT}          |")
    print(f"  |  Parar:  Ctrl+C                          |")
    print(f"  +------------------------------------------+")
    print()
    print(f"  Aqui voce ve o status do sistema, explora")
    print(f"  as capacidades e testa comandos.")
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
        print("  Dashboard encerrado.")
        server.server_close()


if __name__ == "__main__":
    if "--port" in sys.argv:
        idx = sys.argv.index("--port")
        PORT = int(sys.argv[idx + 1])
    main()
