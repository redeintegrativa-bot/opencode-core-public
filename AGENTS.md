# ONBOARDING
TONE=balanced FOCUS=backend VERBOSITY=medium
# V14.0 — 7 core agents · category routing · quality gates · knowledge store

## Features Rápidas

| Comando/Trigger | O que acontece |
|----------------|----------------|
| `analyze` / `explore` | Router → analyzer (haiku) — pesquisa, mapeia dependências |
| `implement` / `fix` / `code` | Router → coder (sonnet) — implementa, debuga |
| `review` / `validate` | Router → reviewer (sonnet) — code review + quality gates |
| `document` / `readme` | Router → documenter (haiku) — docs + changelog |
| `deploy` / `ci` / `docker` | Router → coder (haiku) — devops via skill |
| Tarefa crítica (auth, security) | Router → phase=critical → adversarial review automático |
| Erro de sintaxe/import | Quality Gate BLOCKER → re-route automático pra fix |
| Tipos inconsistentes | CQ-03 → auto-fix silencioso |
| Sessão interrompida | Session Recovery → auto-resume sem perguntar |
| Tecnologia nova sem skill | Fallback Log → 3+ ocorrências → auto-cria skill |

## Skills Úteis

`/debug` · `/plan` · `/review` · `/fix` · `/tdd` · `/refactor` · `/api-design` · `/database` · `/security-scan` · `/clone` · `/onboarding` · `/verification-loop`

## Auto-Decisões (não pergunto)

- Categoria da tarefa → detecto automaticamente
- Mode (quick/normal/full/critical) → detecto pela complexidade
- Gate MEDIUM/LOW → auto-fixo sem te incomodar
- Revisão adversarial → só rodo em código crítico
- Conhecimento → salvo no knowledge store automaticamente

## Memória Persistente (sessões)

Protocolo obrigatório para evitar retrabalho entre sessões (skill `session-resume`):

- **Início**: `python3 memory/session.py show` — carrega o contexto do MEMORY.md e resume onde paramos.
- **Durante**: descobertas/decisões → `python3 memory/session.py log "<texto>"`.
- **Final**: `python3 memory/session.py end --summary "..." [--decision "..." --file "..."]` ou `/remember <resumo>`.
- **Versionar** (git pessoal): `python3 memory/session.py backup --target <repo-pessoal>/memory`.

Storage: global `~/.config/opencode/projects/{hash}/memory/` (sobrevive a updates do repo) ou `--local` para usar `memory/` do repo. **Nunca commitar `MEMORY.md`/sessões no repo público** (`memory/.gitignore` cobre isso).
