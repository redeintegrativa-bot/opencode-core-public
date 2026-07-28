# AGENTS.md — OpenCode Core

Infrastructure hub: agent definitions, skills, rules, shared services. Not a typical app repo — most files are **markdown definitions** consumed by orchestrators, not executable code.

## Quick Commands

```bash
# Terminal chat (main active project)
cd terminal-chat && python3 opencode_chat.py

# Telegram agent (deactivated)
cd telegram-bot && ./daemon.sh start|stop|status|logs

# Install dependencies
pip install rich prompt_toolkit  # terminal chat
pip install python-telegram-bot python-dotenv  # telegram agent

# Validate hooks
python3 hooks/validate_security.py /path/to/dir
python3 hooks/validate_agent.py <agent_name>
python3 hooks/validate_skill.py <skill_name>
```

## Repo Structure

| Dir | What it is | Format |
|-----|-----------|--------|
| `agents/` | Agent definitions (43 total) | **Markdown** (.md), not code |
| `skills/` | Skill definitions (33 total) | Markdown SKILL.md + registry.json |
| `rules/` | Security & language rules (110 rules) | Markdown |
| `hooks/` | Validation & security scripts | Python + Bash |
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

- **33 skills** registered in `skills/registry.json` — edit registry when adding/removing skills
- **110 security rules** in `rules/common/security.md` — mandatory for all code
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
