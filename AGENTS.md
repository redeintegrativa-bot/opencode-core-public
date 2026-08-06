# AGENTS.md — OpenCode Core

Infrastructure hub: agent definitions, skills, rules, shared services, and workflows. Not a typical app repo — most files are **markdown definitions** consumed by orchestrators, not executable code.

## Quick Commands

```bash
# Terminal chat (main active project)
cd terminal-chat && python3 opencode_chat.py

# Telegram agent (deactivated)
cd telegram-bot && ./daemon.sh start|stop|status|logs

# Dashboard local da memória (visão no navegador)
cd dashboard && ./run.sh start|stop|status   # http://localhost:8765

# Reflexão automática (mini-Hermes) — propõe skills/regras a partir das sessões
python3 scripts/reflect.py --root /root --scan | --deep | --list

# Install dependencies
pip install rich prompt_toolkit  # terminal chat
pip install python-telegram-bot python-dotenv  # telegram agent

# Validate hooks
python3 hooks/validate_security.py /path/to/dir
python3 hooks/validate_agent.py <agent_name>
python3 hooks/validate_skill.py <skill_name>
```

## Context & Memory (Context Persistence System)

Contexto versionado no repo — **sobrevive a clones, branches e forks**.

### Diretórios

| Dir | O que guarda | Sobrevive a clone? |
|-----|-------------|-------------------|
| `context/` | Checklist, roadmap, decisões, handoff | ✅ Sim (versionado) |
| `scripts/` | Bootstrap, auto-checkpoint, recovery | ✅ Sim (versionado) |
| `.checkpoints/` | Snapshots de estado (auto-save) | ⚠️ Ignorado pelo git |
| `memory/agents/` | Memórias dos agents (JSON) | ⚠️ Ignorado pelo git |
| `memory/MEMORY.md` | Histórico de sessões (git pessoal) | ✅ Sim (versionado) |

### Como usar

```bash
# Após clonar o repo — restaura todo o contexto
./scripts/bootstrap.sh

# Ativar auto-save (salva a cada 5 min) + auto-update
source scripts/auto-checkpoint.sh

# Salvar checkpoint manual agora
./scripts/auto-checkpoint.sh now

# Ver status dos checkpoints
./scripts/auto-checkpoint.sh status

# Checar atualizações do remote manualmente
./scripts/auto-update.sh

# Buscar em checkpoints, contexto e memórias (padrão Déjà Vu)
./scripts/memory-search.sh "query"
```

### Arquivos de contexto

| Arquivo | Propósito |
|---------|-----------|
| `context/checklist.md` | Tarefas com status `[ ]` `[x]` `[~]` `[!]` |
| `context/roadmap.md` | Milestones, OKRs, visão do projeto |
| `context/decisions.md` | ADRs — decisões arquiteturais com rationale |
| `context/session-handoff.md` | Handoff vivo, auto-atualizado |

### Auto-recovery

O `hooks/pre-bootstrap.sh` carrega automaticamente no início de cada sessão:
1. **Auto-update**: checa `origin/master` e faz pull automático (ff-only)
2. Checklist (total, done, pending)
3. Milestone ativo do roadmap
4. Handoff da última sessão
5. Memórias do `memory/memory.py`

O `scripts/auto-checkpoint.sh` também dispara auto-update a cada 3 checkpoints.

## Memory (Sessions)

Memória persistente entre sessões — evita retrabalho. Protocolo (skill `session-resume`):

- **Início**: `python3 memory/session.py show` — carrega o `memory/MEMORY.md` e resume onde paramos.
- **Durante**: descobertas/decisões → `python3 memory/session.py log "<texto>"`.
- **Final**: `python3 memory/session.py end --summary "..." [--decision "..." --file "..."]` ou `/remember <resumo>`.
- **Git pessoal**: o `memory/MEMORY.md` e sessões são versionados AQUI (repo pessoal) — commitar.
- **Store global**: `~/.config/opencode/projects/{hash}/memory/` é o canônico (imune a updates). Espelhar com `python3 memory/session.py backup [--from-target]`.

## Repo Structure

| Dir | What it is | Format |
|-----|-----------|--------|
| `agents/` | Agent definitions (43 total) | **Markdown** (.md), not code |
| `skills/` | Skill definitions (48 total) | Markdown SKILL.md + registry.json |
| `context/` | Checklist, roadmap, decisions, handoff (versionado) | Markdown |
| `scripts/` | Bootstrap, auto-checkpoint, recovery, reflexão (`reflect.py`) | Bash |
| `dashboard/` | Dashboard local da memória (stdlib http.server, port 8765) | Python |
| `rules/` | Security & language rules (110+ rules) | Markdown |
| `hooks/` | Validation, security & bootstrap hooks | Python + Bash |
| `terminal-chat/` | Chat TUI (active) | Python (rich + prompt_toolkit) |
| `telegram-bot/` | Telegram agent (deactivated) | Python (python-telegram-bot) |
| `providers/` | DeFi/crypto data providers | Python |
| `memory/` | Memory persistence layer | Python |
| `services/` | Scoring, learning services | Python |
| `workflows/` | Standard workflows | Markdown + Bash |
| `templates/` | Reusable templates | Markdown |
| `chat/` | Chat and mission matching | Python |
| `patterns/` | Content pipeline patterns | Python |

## Key Facts

- **48 skills** registered in `skills/registry.json` — edit registry when adding/removing skills- **110+ security rules** in `rules/common/security.md` — mandatory for all code
- **Agent definitions are markdown**, not executable — they define behavior for orchestrator routing
- **`.env` is gitignored** — never commit secrets
- **`__pycache__/` is gitignored** — clean with `find . -type d -name __pycache__ -exec rm -rf {} +`

## Security (Mandatory)

All code must pass security validation before commit. Key rules:
- No hardcoded secrets (api_key, password, token, sk-, ghp_, AKIA)
- No eval()/exec(), no shell injection, no SQL injection
- `.env` files must be in `.gitignore`
- CORS: no wildcard `*` in production configs

Run security scan: `python3 hooks/validate_security.py .`

## Best Practices for Working with This Repo

### Skill Writing

Every skill MUST have:
- **Frontmatter**: `name`, `description` (1-1024 chars, specific enough for auto-triggering)
- **When to Activate** section: explicit trigger conditions the agent can match against
- **Core Principle**: one-paragraph north star for the skill
- **Structured body**: sections with clear headings, examples, anti-patterns

### Workflow

- **Plan before Build**: always spec first, code second
- **Use `/grill`** when requirements are vague — pull out the spec before coding
- **Use `/handoff`** when context degrades or switching projects
- **Use `/compact`** in long sessions to compress context
- **Orchestrate** complex tasks via `workflows/orchestration-workflow.md`

### Agent Communication

- Each agent definition (.md) should specify: purpose, tools, delegable sub-tasks
- L2 specialists handle one domain; L1 experts coordinate across domains
- System agents (TASK_TRACKER, PARALLEL_COORDINATOR) manage infrastructure

## Ecosystem Skills Included

| Skill | Category | Purpose |
|-------|----------|---------|
| `handoff` | Utility | Session compression for agent transfer |
| `grill-me` | Workflow | Planning interview before coding |
| `stop-slop` | Utility | Clean AI writing tics from output |
| `orchestrator` | Core | Multi-agent coordination & delegation |
| `firecrawl` | Core | Web scrape/crawl → LLM-ready markdown/JSON |

## Terminal Chat Architecture

```
opencode_chat.py  →  streaming.py  →  opencode run --format json
                       ↓
                    agents.py (6 agents: default, coder, reviewer, architect, security, teacher)
                       ↓
                    session.py (auto-saves to ~/.opencode-chat/sessions/)
                       ↓
                    ui.py (Rich panels, spinner, markdown rendering)
```

Commands: `/help`, `/status`, `/agents`, `/agent <name>`, `/sessions`, `/save`, `/clear`, `/quit`

## Conventions

- Skills: each skill is a directory under `skills/` with `SKILL.md`
- Agents: each agent is a `.md` file under `agents/` (L0 core, L1 experts, L2 specialists)
- Rules: grouped by language under `rules/{common,python,typescript,go}/`
- Hooks: Python scripts in `hooks/` with `validate_` prefix
- All Python: use type hints, no external deps unless necessary
- Telegram bot: daemon mode via `daemon.sh`, PID at `/tmp/opencode-agent.pid`
