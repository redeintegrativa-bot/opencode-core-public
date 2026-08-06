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

`/debug` · `/plan` · `/review` · `/fix` · `/tdd` · `/refactor` · `/api-design` · `/database` · `/security-scan` · `/clone` · `/onboarding` · `/verification-loop` · `/remember` · `/salvar`

## Auto-Decisões (não pergunto)

- Categoria da tarefa → detecto automaticamente
- Mode (quick/normal/full/critical) → detecto pela complexidade
- Gate MEDIUM/LOW → auto-fixo sem te incomodar
- Revisão adversarial → só rodo em código crítico
- Conhecimento → salvo no knowledge store automaticamente

## Memória Persistente (sessões)

Protocolo obrigatório para evitar retrabalho entre sessões (skill `session-resume`):

- **Início**: `python ~/.config/opencode/memory/session.py show` — carrega o contexto do MEMORY.md e resume onde paramos.
- **Durante**: descobertas/decisões → `python ~/.config/opencode/memory/session.py log "<texto>"`.
- **Final**: `python ~/.config/opencode/memory/session.py end --summary "..." [--decision "..." --file "..."]` ou `/remember <resumo>`.
- **Versionar** (git pessoal): `python ~/.config/opencode/memory/session.py backup --target <repo-pessoal>/memory`.

Storage: global `~/.config/opencode/projects/{hash}/memory/` (sobrevive a updates do repo) ou `--local` para usar `memory/` do repo. **Nunca commitar `MEMORY.md`/sessões no repo público** (`memory/.gitignore` cobre isso). `python3` não existe em Windows — usar sempre `python`.

## GitHub / Auth (setup genérico)

Push exige autenticação. Configure com o script genérico (não grava segredo no repo):

```bash
GH_TOKEN=<token> ./scripts/setup-github-auth.sh <owner> <repo> [<repo>...] [--check]
```

- Usa o token do env `GH_TOKEN` → grava em `~/.git-credentials` (perms 600) + `credential.helper store`.
- `--check` valida permissão de escrita em cada repo (receive-pack HTTP 200).
- Token sugerido: **classic PAT escopo `repo`**. Fine-grained precisa de `Contents: Read and write` + repos selecionados, senão push dá 403.

## Reflexão automática (mini-Hermes)

`scripts/reflect.py` varre as sessões salvas, detecta padrões recorrentes e propõe skills/regras para revisão (nada é ativado sem aprovação):

```bash
python ~/opencode-core/scripts/reflect.py --root <root> --scan   # heurístico (sem LLM)
python ~/opencode-core/scripts/reflect.py --root <root> --deep   # análise semântica via opencode run
python ~/opencode-core/scripts/reflect.py --list                 # listar propostas pendentes
```

Propostas vão para `~/.config/opencode/hermes-staging/<data>/`. Revisar antes de ativar.
- **Nunca commitar tokens** — hooks de segurança bloqueiam padrões tipo `ghp_`.

## Loop de Auto-Melhoria (ativo via plugin)

O plugin `~/.config/opencode/plugins/self-improvement.js` roda automaticamente a cada sessão:

| Gatilho | O que grava |
|---------|-------------|
| `session.idle` | `state/session-history.jsonl` + `state/session-recovery.json` (inclui `memory` do `session.py status --short`) |
| `tool.execute.after` com erro | `state/fallback-log.jsonl` (com keywords p/ roteamento) |
| A cada 10 sessões | Rebuild de `fallback-log.json` → roda `scripts/evolve-agent.py --check` → sugestões em `state/knowledge.jsonl` |
| `session.created` (plugin auto-sync) | `git pull --ff-only` no pessoal → se houve commit, redeploy silencioso do setup |
| `session.idle` 1x/sessão (plugin auto-sync) | `sync-public.py --stage` — espelha melhorias genéricas no repo público + commit local; **push só com aprovação** |

**Uso:** checagens baratas (evolve-agent.py, local, sem LLM) rodam sozinhas.
Auditoria pesada do framework (`/evolve-framework`) permanece sob demanda.
Consulte `state/*.jsonl` para health-check e aprendizado acumulado.

## Auto-Sync Pessoal → Público (auto melhorante)

Sem comandos: o plugin `auto-sync.js` puxa as melhorias no `session.created` e espelha recursos genéricos no público no `session.idle` (`sync-public.py --stage` — commit local, **push só com aprovação**).

- Pendências prontas para push: `~/.config/opencode/state/sync-pending.json` (checar ao iniciar a sessão).
- Auditoria: `state/auto-sync.jsonl`.
- Ferramenta: `python ~/opencode-core/scripts/sync-public.py --check|--stage|--push|--status`.
- Ao salvar (`/salvar`): se houver pendência e o usuário aprovar, rodar `sync-public.py --push`.
