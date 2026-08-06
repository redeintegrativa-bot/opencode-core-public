---
name: update-core
description: Verifica e aplica atualizações do OpenCode Core. Dispara quando o usuário pergunta em linguagem natural sobre atualizações do repositório/framework (ex: "tem atualização do core?", "atualiza o framework", "update do repositório", "versão nova", "novidades do opencode-core", "atualizar", "check-update", "make update", "como atualizo o core"). Fluxo consultivo: mostra o changelog e só aplica com aprovação explícita.
user-invokable: true
allowed-tools: Read, Glob, Grep, Bash
metadata:
  keywords: [update, atualizar, atualização, core, framework, versão, novidades, changelog, opencode-core, update-core]
---

# Update Core Skill

## Purpose

Atualiza o **OpenCode Core** (repo `redeintegrativa-bot/opencode-core-public`) de forma segura e consultiva: nunca aplica nada sem aprovação explícita do usuário.

## Localização do repositório

O repositório pode estar em vários lugares. Procure nesta ordem:

1. Variável de ambiente `OPENCODE_CORE_DIR`
2. `~/opencode-core`
3. `~/opencode-core-public`
4. Qualquer diretório que contenha um arquivo `VERSION` e a pasta `scripts/`

Se não encontrar, **pergunte ao usuário** onde o repo está clonado antes de prosseguir.

## Fluxo (executa em ordem)

### 1. Localizar o repo
```bash
python -c "import os;print(next((d for d in [os.environ.get('OPENCODE_CORE_DIR'),os.path.expanduser('~/opencode-core'),os.path.expanduser('~/opencode-core-public')] if d and os.path.exists(os.path.join(d,'VERSION'))),''))"
```
Se vazio, pergunte o caminho.

### 2. Verificar atualizações (somente leitura)
```bash
python scripts/check-update.py --json
```
Interpretar o JSON:
- `has_update: false` → informar "Core atualizado (versão X)" e encerrar.
- `has_update: true` → **mostrar o changelog** (`local -> remote`) ao usuário.

### 3. Aprovação (obrigatória)
NÃO aplicar automaticamente. Apresente o que mudou e pergunte explicitamente:
> "Há uma atualização disponível (X -> Y). Quer que eu aplique?"

Só prossiga se o usuário aprovar. Se negar, informe que nada foi alterado.

### 4. Aplicar atualização
```bash
python scripts/update.py
```
O `update.py` faz `git pull` (ou baixa ZIP) e reexecuta o setup automaticamente (instala skills/agents/rules/hooks/commands/plugins). Para pular a reinstalação:
```bash
python scripts/update.py --no-install
```

### 5. Confirmar resultado
```bash
python scripts/check-update.py --json
```
Confirmar que a nova versão foi aplicada e resumir ao usuário o que mudou.

## Regras

- **Sempre consultivo** — nunca `update.py` sem aprovação.
- **Mostrar changelog antes** — o usuário decide com informação.
- **Confirmar no final** — reportar a versão nova aplicada.
- Se o repo não for encontrado, não adivinhar caminhos — perguntar.
