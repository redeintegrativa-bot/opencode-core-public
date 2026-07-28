# OpenCode Core — Canivete Suíço para OpenCode

43 agentes · 33 skills · 110 regras · hooks · serviços · templates

> Use com OpenCode no **Termux**, **Linux** ou **Windows Shell**.
> Tudo funciona em terminal — sem GUI, sem browser.

## ⚡ Instalação

```bash
# Android (Termux)
pkg install git python3 nodejs
git clone --depth 1 https://github.com/redeintegrativa-bot/opencode-core-public
cd opencode-core-public
bash setup.sh

# Linux
git clone --depth 1 https://github.com/redeintegrativa-bot/opencode-core-public
cd opencode-core-public
bash setup.sh

# Windows (PowerShell)
git clone --depth 1 https://github.com/redeintegrativa-bot/opencode-core-public
cd opencode-core-public
.\setup.ps1
```

Depois de instalar, o OpenCode já reconhece skills, agentes e regras automaticamente.

## 🎯 Comandos Rápidos

```bash
# Terminal chat (funciona no Termux!)
cd terminal-chat
pip install rich prompt_toolkit
python opencode_chat.py         # ou python3 no Linux

# Validar segurança
python hooks/validate_security.py .   # ou python3 no Linux

# Ver agentes disponíveis
ls agents/core/
ls agents/experts/

# Ver skills
ls skills/ | head -20
cat skills/registry.json | python -m json.tool | head -30
```

## 🤖 Agentes (43)

| Nível | Qtd | Descrição |
|-------|-----|-----------|
| **L0 Core** | 8 | orchestrator, analyzer, coder, reviewer, documenter, system_coordinator |
| **L1 Experts** | 20+ | security, devops, database, browser, UI/UX, trading, MQL, n8n... |
| **L2 Specialists** | 15 | auth, db-query, gui-layout, test-unit, trading-risk... |

## 🧠 Skills (33)

Pra usar qualquer skill, o OpenCode roteia automaticamente. Skills principais:

| Skill | O que faz | Atalho |
|-------|-----------|--------|
| `code-review` | Revisão de código como staff engineer | `/review` |
| `debugging` | Debug sistemático com análise de causa raiz | `/debug` |
| `plan` | Planejamento de implementação | `/plan` |
| `tdd-workflow` | Desenvolvimento orientado a testes | `/tdd` |
| `security-scan` | Auditoria de segurança OWASP | `/security-scan` |
| `fix` | Correção de bugs | `/fix` |
| `refactor-clean` | Refatoração e clean code | `/refactor` |
| `testing-strategy` | Estratégia de testes e cobertura | `/test` |
| `orchestrator` | Coordenação multi-agente | `/orchestrator` |
| `clone-on-demand` | Clona repositórios automaticamente | `/clone` |
| `ui-ux-system` | Design system com Tailwind + Radix | `/ui-design` |
| `browser-agent` | Automação de browser | — |

## 📁 Estrutura

```
opencode-core-public/
├── agents/          → 43 agentes (.md)
├── skills/          → 33 skills + registry.json
├── rules/           → 110 regras de segurança
├── hooks/           → scripts de validação
├── workflows/       → bugfix, feature, refactoring
├── services/        → ranking, fallback, learning
├── providers/       → DeFi/crypto data providers
├── memory/          → persistência de memória
├── terminal-chat/   → chat TUI (funciona no Termux!)
├── my-money-track/  → app financeiro template
├── .opencode/       → config + agentes OpenCode
├── .claude-plugin/  → plugin Claude Code
├── .codex-plugin/   → plugin Codex
├── setup.sh         → instalador Linux/Termux
└── setup.ps1        → instalador Windows
```

## 🔒 Segurança (obrigatório)

- Sem tokens hardcoded
- `.env` no `.gitignore`
- Rode `python hooks/validate_security.py .` antes de todo commit

## 🚀 Rede Integrativa

Este repositório faz parte do ecossistema **Rede Integrativa**.

[https://github.com/redeintegrativa-bot](https://github.com/redeintegrativa-bot)
