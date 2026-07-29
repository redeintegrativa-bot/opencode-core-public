---
name: framework-evolve
description: Monitora a saúde do framework pessoal (7 agents, routing, gates) e sugere evoluções. Use /evolve-framework para auditar e melhorar.
user-invokable: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
metadata:
  keywords: [evolve, framework, audit, improve, health, agents, routing, gates]
---

# Framework Evolution Skill

## Purpose

Audita e evolui o framework pessoal (~/.config/opencode) automaticamente:
- Detecta agents com prompts inchados ou desatualizados
- Identifica gaps no routing (palavras-chave não mapeadas)
- Verifica consistência entre registry.json e skills/ reais
- Sugere splits ou merges de skills pouco usadas

## Trigger

- `/evolve-framework` — auditoria completa
- Automático a cada 10 sessões ou quando 3+ erros de routing forem detectados

## Audit Checks (executa em ordem)

### 1. Agent Prompt Size
- Para cada `.md` em `agents/core/`:
  - Se > 200 linhas → sugere split
  - Se < 20 linhas → sugere merge com outro agent ou remoção
  - Se contém seções órfãs (ex: "## L2 agents" sem L2 existir) → sugere limpeza

### 2. Routing Gap Analysis
- Lê `skills/registry.json` → extrai todas as keywords de routing
- Escaneia `AGENTS.md` por comandos/triggers não roteados
- Keywords que aparecem em 3+ tarefas mas não estão no routing → sugere adicionar

### 3. Skill Registry vs Filesystem
- Lista `skills/*/SKILL.md` vs entries em `registry.json["skills"]`
- SKILL.md sem entry → sugere registrar
- Entry sem SKILL.md → sugere remover do registry

### 4. Skill Usage (por logs de sessão)
- Detecta skills com 0 ativações nas últimas 10 sessões
- Skills dormentes: sugere arquivar (mover para `skills/_archive/`)

### 5. Cross-Reference Health
- Verifica se agentes citados em `registry.json["skills"][*]["agent"]` existem como arquivos em `agents/core/`
- Agentes órfãos → sugere criar ou corrigir

## Output Format

```
FRAMEWORK AUDIT — 2026-07-28

[PASS] Agent prompt sizes: 7/7 within limits
[WARN] Routing gaps: 2 keywords não mapeados → "wireframe", "dashboard"
[FAIL] Skills sem entry no registry: image-gen
[INFO] Skills dormentes: telegram-bot (0 usos em 10 sessões)

Recomendações:
1. Adicionar routing para "wireframe" -> ui-ux-system
2. Registrar image-gen no registry.json
3. Arquivar telegram-bot → _archive/ se não for usar
```

## Rules

- NUNCA modifica arquivos sem perguntar (a menos que seja auto-fix de baixo risco, ex: adicionar keyword no routing)
- Gera relatório em markdown e salva em `~/.config/opencode/audits/` com timestamp
- Se o framework ficar > 30 dias sem audit, avisa no início da sessão
- Audit completo = leitura de ~40 arquivos; usa glob/grep em paralelo
