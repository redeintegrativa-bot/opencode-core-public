# Changelog

## 1.8.3 (2026-08-06)

### Added
- `scripts/validate-encoding.py`: bloqueia UTF-8 invalido e mojibake latin-1->UTF-8 (bytes 0xC3/0xC2/0xE2 lidos como latin-1 e re-encodados), avisa sobre BOM desnecessario (excecao: `setup.ps1`, que precisa de BOM para o PowerShell 5.1).
- CI valida encoding em arquivos de texto no pessoal e no publico.

### Fixed
- Mojibake no `ROADMAP.md` (double-encoding de `ção` e `→`) corrigido.

## 1.8.2 (2026-08-06)

### Fixed
- CI portavel: o validador de seguranca resolve regras relativamente ao repo e funciona em Python 3.11+.
- Validador de seguranca elimina falsos positivos de definicoes de regex e bloqueia apenas achados HIGH/CRITICAL.
- Auto-sync executa Git e PowerShell com argumentos estruturados, corrigindo `skip-no-remote` incorreto e caminhos com espacos.
- Sync pessoal -> publico compara o conteudo real para reconciliar pushes manuais sem remover adaptacoes exclusivas do publico.
- `setup.ps1` usa o workflow versionado em vez de regenera-lo durante a instalacao.

### CI
- Adicionadas validacoes de sintaxe Python, JavaScript, PowerShell e Shell, layout dos plugins, registro de skills e permissoes somente leitura.
## 1.8.1 (2026-08-06)

### Fixed
- Helpers `notify.js` e `python-helper.js` movidos para `plugins/lib/`, impedindo que o OpenCode 1.18.14 os execute como plugins e quebre a lista de providers com `Unexpected server error`.
- Instaladores Windows/Linux agora preservam `plugins/lib/` e removem helpers legados da raiz da instalacao.
- CI valida que a raiz contem apenas plugins com um unico export, que os helpers existem e que os instaladores mantem as protecoes contra regressao.
## 1.8.0 (2026-08-06)

### Added
- **Canal unificado de notificacoes** (`plugins/notify.js`): uma funcao `notify()` dispara em paralelo o toast da TUI, um som distinto no terminal e um toast do Windows silencioso. Cada canal e independente e controlado ao vivo por `features.json` (sem reiniciar o opencode).
- **Sons por tipo de notificacao** (`scripts/play-sound.ps1`): melodia diferente para tarefa concluida, memoria salva, erro de ferramenta, erro de sessao, update disponivel e push pendente. Tons sine (WAV 44.1k stereo) em memoria via SoundPlayer, sem depender de console.
- **Toast do Windows silencioso** (`scripts/windows-toast.ps1`): notificacao do sistema com audio desligado (o som fica no terminal), AppId "OpenCode", com fallback de balloon.
- **Controle de funcoes pelo dashboard**: endpoints `GET/POST /api/features` no Network Dashboard (127.0.0.1:8080) + secao de toggles no painel para ligar/desligar Monitor de rede, Verificar updates, Notificacoes da sessao, Toast do Windows e Sons no terminal. (dashboard e do projeto local, nao do repo).
- **Flags novas em `features.py`**: `ui_ux_toasts`, `windows_toast`, `toast_sounds` (default ON) alem das existentes `network_watch`/`update_check`.

### Changed
- `ui-ux.js`, `update-check.js`, `auto-sync.js`, `network-watch.js` passam a usar o `notify()`; verificacao de feature movida para dentro dos handlers (toggle ao vivo).
- `update-check.js`: quando ha update do core, notifica (TUI + som + Windows) alem de gravar `update-alert.json`.
- `auto-sync.js`: quando o `--stage` gera mudancas, notifica que ha push pendente de aprovacao.

## 1.7.1 (2026-08-06)

### Added
- **Tema custom `hacker-green`** (`themes/hacker-green.json`): estilo tech-hacker com fundo escuro esverdeado confortável (`#0A120A` → `#1E3322`, sem preto puro), contraste alto, verde-fosforo `#00E070` só em acentos, texto quase-branco `#E8F5EC` — legível em longas sessões. Agora é o tema padrão no `tui.json`; `aguia-azul` e `opencode` continuam disponíveis no seletor (`<leader>t`).

### Fixed
- `python-helper.js`: exports defensivos + plugin no-op `PythonHelper` — eliminado erro `failed to load plugin` que aparecia a cada inicialização (módulo utilitário não era plugin).

## 1.7.0 (2026-08-06)

### Added
- **Tema custom `aguia-azul`** (`themes/aguia-azul.json`): paleta escura azul-elétrico + âmbar suave (Aquário/Urano + sol), contraste alto, com variantes dark/light para text, markdown, syntax e diff.
- **`tui.json`**: configuração de TUI do opencode — tema `aguia-azul`, `scroll_acceleration`, `diff_style: auto`, `mouse`, `attention` (notificação de desktop + som suave em volume 0.3) e keybinds (`<leader>t` temas, `<leader>n` nova sessão, `<leader>l` sessões, cópia com `ctrl+shift+c`).
- **Plugin `ui-ux`** (`plugins/ui-ux.js`): toasts transitórios via `client.tui.showToast` — "Tarefa concluída" (`session.idle`), "Erro na sessão" (`session.error`), "Erro em <ferramenta>" (`tool.execute.after`) e "Memória salva" (`command.executed` salvar/remember). Sem console.log; throttle anti-spam de 30s; desligável por flag `ui_ux_toasts: false` em `features.json`.

### Changed
- `setup.ps1`: novas funções `Install-Themes` (copia `themes/*.json`) e `Install-Tui` (copia `tui.json`) + switch `-Themes`.
- `sync-public.py`: whitelist inclui `themes/` e `tui.json` no espelhamento pessoal → público.
- Agente `gui-super-expert` localizado para PT-BR (estava em italiano).

## 1.6.1 (2026-08-06)

### Added
- Skill `cloud-backup`: guia para usuários sem conta GitHub terem backup em nuvem do setup e continuarem recebendo updates do repo público (GitHub/GitLab/Codeberg/Bitbucket, nuvem de arquivos, zip agendado, ou só updates). Registrada no registry (total 50).
- `docs/backup-sem-github.md`: documentação espelhada no público.

### Fixed
- Plugin `auto-sync`: detecta ausência de `remote` no repo pessoal e loga `skip-no-remote` em vez de `fail` — setup funciona sem nenhuma conta git, sem ruído.

## 1.6.0 (2026-08-06)

### Fixed
- **Plugins quebrados no Windows**: `ctx.$`/`spawn("python", ...)` não achavam `python` no PATH do bun → `bun: command not found: python` em toda sessão (auto-sync falhava 5x seguidas). Novo `plugins/python-helper.js` resolve python robustamente (`OPENCODE_PYTHON` → `python` → `py -3` → caminhos `%LOCALAPPDATA%\Python*`) e roda via `execFile`. Aplicado em `self-improvement`, `auto-sync`, `update-check` e `network-watch`.

### Changed
- **Console limpo**: removidos todos os `client.app.log` dos plugins (não renderizavam toast, mas poluíam logs). Plugins agora gravam só em `state/*.jsonl`.
- **Session-resume silencioso**: protocolo de início passa a usar `session.py status --short` e NÃO despeja o `MEMORY.md` no chat (no máximo 1 linha de resumo). Ajustado AGENTS.md, skill `session-resume` e orquestrador STEP 0.
- `session.error` handler grava mensagem útil (não mais `[object Object]`).

### Cleanup
- `state/session-history.jsonl`: deduplicado (28 → 8, 1 por sessão)
- `state/fallback-log.jsonl`: removidas entradas inválidas
- `state/session-recovery.json`: caracteres corrompidos removidos
- `state/sync-pending.json`: pendência velha `fail` removida

## 1.5.1 (2026-08-05)

### Added
- Memória persistente reativada no Windows: `memory/session.py` instalado via setup (`-Memory`), comandos `/remember` e `/salvar`
- Plugin `auto-sync`: no `session.created` faz `pull --ff-only` no repo pessoal + redeploy silencioso; no `session.idle` (1x/sessão) roda `sync-public.py --stage` (commit local; **push só com aprovação**)
- `scripts/sync-public.py`: espelha recursos genéricos do pessoal no público via manifesto SHA-256 (`--check/--stage/--push/--status`)
- Plugin `self-improvement`: grava status da memória no `session-recovery.json`

### Changed
- session.py: fix `backup --from-target` (cria destino quando o store não existe) + stdout UTF-8; todos os comandos usam `python` (não `python3`)
- AGENTS.md template: nova seção "Auto-Sync Pessoal → Público" + tabela do loop de auto-melhoria atualizada
- sync-public: `AGENTS.md` fora da whitelist (são docs diferentes por repo)

### Fixed
- AGENTS.md do público restaurado (seed havia sobrescrito o template com o doc de estrutura do pessoal)

## 1.5.0 (2026-08-05)

### Added
- skill `update-core`: atualizacao do core por linguagem natural (CONSULTIVA — procura o repo, mostra o changelog e so aplica com aprovacao explicita)
- Comandos `/update` e `/config` agora sao arquivos reais em `.opencode/command/` e sao instalados pelo setup
- setup.sh/setup.ps1: flags `--commands` e `--plugins` + reinstall automatico no modo `--all`
- update.py: auto-install apos atualizar (roda o setup para reaplicar skills/plugins/comandos) + flag `--no-install`
- README: secao "Como atualizar" (via chat, skill `update-core`, ou `python scripts/update.py`)

### Changed
- skills/registry.json: entry `update-core` + routing de "atualizacao/versao/changelog" (total: 42 skills)
- CI: branch padrao corrigida para `master` (repo + heredocs do setup)

## 1.4.0 (2026-08-05)

### Added
- scripts/features.py: gerenciador de recursos opcionais (opt-in) — list/enable/disable/is-enabled
- Onboarding (console + bash) agora tem 5 perguntas: estilo, foco, nivel, PERMISSOES e RECURSOS opcionais
- Modos de permissao: ACESSO TOTAL / EQUILIBRADO / APROVAR SEMPRE (grava no opencode.json preservando o resto)
- `/config` — revisa/ajusta permissoes e recursos a qualquer momento
- `/update` — atualizacao CONSULTIVA: mostra o changelog e so aplica com aprovacao explicita
- check-update.py: `--self-test` (11 testes internos sem rede)

### Changed
- Recursos como monitoramento de rede e check de atualizacoes agora sao OPTO-IN (nada ativa sozinho)
- Plugins network-watch e update-check respeitam ~/.config/opencode/features.json
- update-check.js agora e CONSULTIVO: detecta novidades, registra alerta pendente e NAO aplica nada sem aprovacao

### Fixed
- check-update.py: changelog diff corrigido (comparava por ordem do arquivo, quebrado quando secoes fora de ordem)
- check-update.py: branch detectada via `git ls-remote --symref` (main ou master), sem hardcoded
- update.py: branch dinamica centralizada (git pull e ZIP usam a mesma deteccao)
- setup.ps1: corrigido encoding (UTF-8 com BOM) que quebrava no PowerShell 5.1

## 1.3.0 (2026-07-28)

### Added
- Check-update com changelog diff: mostra o que mudou entre versoes
- Dashboard: badge verde "Nova versao!" com modal de changelog + botao atualizar
- Gatilhos de check-update: onboarding, dashboard, make check-update, make setup

### Changed
- onboarding.py: removeu menu "Console vs Navegador" — inicia direto
- onboarding.py: check_version agora so informa (nunca pergunta)
- check-update.py: nunca mais pergunta "Atualizar agora?" no terminal
- check-update.py: le VERSION direto do raw.githubusercontent.com
- README corrigido: 55 agentes (era 57)
- Dashboard: rules_count agora conta 117 regras individuais (nao 13 arquivos)

### Fixed
- hooks/validate_security.py: DEFAULT_RULES_PATH agora e relativo ao repo
- hooks/validate_security.py: path.walk() > os.walk() (compat Python 3.9+)
- hooks/validate_security.py: removeu falso positivo "Input validation"
- setup.sh: fallback de diretorio corrigido (~/.config/opencode)
- setup.ps1: fallback de diretorio corrigido (~/.config/opencode)
- skills/telegram-bot/: diretorio criado (estava so no registry.json)
- Makefile: help agora usa python como fallback (sem dependencia de awk)

## 1.0.0 (2026-07-28)

### Added
- Initial public release of OpenCode Core Public
- 57 agent definitions (core, experts, L2 specialists, system)
- 35 skills with unified registry.json + slash commands
- 110+ security and language rules
- Validation hooks (Python + Bash)

## 1.1.0 (2026-07-28)

### Added
- Onboarding interativo com exemplos visuais (3 perguntas)
- Suporte a 2 modos: Console e Navegador
- Dashboard web local com test drive interativo
- Test Drive: wizard que gera prompt copiavel pro OpenCode
- `/config` — muda estilo/foco/verbosidade sem refazer onboarding
- Auto-detecção de estilo pela conversa (skill onboarding)
- Config compacta: AGENTS.md de 2 linhas (~20 tokens)

### Changed
- README traduzido para portugues brasileiro
- Onboarding reduzido de 8 para 3 perguntas
- AGENTS.md de 25 linhas para 2 linhas

## 1.2.0 (2026-07-28)

### Added
- Sistema de atualizacao: scripts/check-update.py + update.py
- VERSION file para controle de versao
- `make check-update`, `make update`, `make backup`
- Badge de versao no dashboard
- Endpoint /api/version no servidor
- docs/estrutura.md — guia didatico do repositorio

### Fixed
- Numeros corrigidos no README (57 agentes, 35 skills)
- registry.json: total_skills corrigido de 37 para 35
- CONTRIBUTING.md — encoding corrigido
- Makefile com fallback para Windows (sem find/sed/grep)
- Unicode box-drawing substituido por ASCII (compativel Windows)
- Terminal Chat (Python TUI with Rich + Prompt Toolkit)
- Telegram Bot template (deactivated, requires token setup)
- My Money Track finance app template
- DeFi/Crypto data providers (CoinGecko, DexScreener, DefiLlama)
- Memory persistence layer
- Shared services (ranking, fallback chain, feedback learning)
- Workflows (bugfix, feature, refactoring, security)
- Clone-on-demand skill for auto-cloning repos
- Orchestrator V13 UNIFIED with 6-level fallback system
