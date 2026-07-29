# OpenCode Core — Comandos úteis
# Funciona em: Linux, macOS, Termux (Android), Windows (WSL/Git Bash)

.PHONY: help setup install validate chat clean

help:  ## Mostra esta ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup:  ## Instala skills, agents, rules e hooks no ambiente
	@bash setup.sh

install:  ## Instala dependências Python do terminal-chat
	pip install rich prompt_toolkit 2>/dev/null || pip3 install rich prompt_toolkit

validate:  ## Valida segurança de todo o repositório
	python hooks/validate_security.py . 2>/dev/null || python3 hooks/validate_security.py .

chat:  ## Inicia o terminal chat
	@cd terminal-chat && python opencode_chat.py 2>/dev/null || cd terminal-chat && python3 opencode_chat.py

skills:  ## Lista todas as skills disponíveis
	@python3 -c "
import json
with open('skills/registry.json') as f:
    reg = json.load(f)
for name, skill in reg['skills'].items():
    cmd = skill.get('slash_command', '')
    cmd_str = f' ({cmd})' if cmd else ''
    print(f'  {name:35s} {skill[\"category\"]:15s}{cmd_str}')
print(f'\nTotal: {reg[\"total_skills\"]} skills')
"

agents:  ## Lista todos os agentes disponíveis
	@echo "Core agents:"
	@ls agents/core/*.md 2>/dev/null | sed 's/.*\///' | sed 's/\.md$$//' | while read a; do echo "  $$a"; done
	@echo ""
	@echo "Expert agents:"
	@ls agents/experts/*.md 2>/dev/null | sed 's/.*\///' | sed 's/\.md$$//' | while read a; do echo "  $$a"; done

dashboard:  ## Inicia dashboard web local (http://localhost:8080)
	python dashboard/server.py 2>/dev/null || python3 dashboard/server.py

clean:  ## Limpa caches Python
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; echo "✓ Cache limpo"
