# Changelog

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
