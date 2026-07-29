---
name: agent-gen
description: Gera agentes especializados sob demanda. Entrevista o usuario, pesquisa o dominio, gera o arquivo .md e registra no sistema. Use /agent-gen para criar um agente novo.
user-invokable: true
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Task, WebSearch, WebFetch]
metadata:
  keywords: [agent, generate, create, new, especialista, criar]
---

# Agent Gen — Criacao Dinamica de Agentes

## Purpose

Cria agentes especializados sob demanda quando o orquestrador nao encontra match na routing table ou quando o usuario pede explicitamente.

## Activation

- `/agent-gen` — inicia o fluxo interativo
- `/agent-gen "descricao"` — ja com contexto
- Automaticamente quando orchestrator detecta 2+ fallbacks no mesmo dominio

## Flow (6 Fases)

### FASE 1: DIAGNOSE

Use `question` tool para coletar:

1. **Nome do agente** — "Como quer chamar o agente? (ex: media-expert)"
2. **Descricao** — "O que ele vai fazer? Descreva em 1-2 frases."
3. **Keywords** — "Quais palavras-chave ativam ele? (ex: video, ffmpeg, thumbnail, media)"
4. **Nivel** — `L1 Expert` (independente) ou `L2 Specialist` (sub-agente de um expert)
5. **Parent** — Se L2: "Qual expert existente ele complementa?"
6. **Modelo** — Sugira baseado na complexidade: `sonnet` (padrao), `haiku` (rapido/barato), `opus` (complexo)

### FASE 2: PESQUISA

Paralelo com Task tool:

```
Task 1 (Explore): "Varra agents/ existentes procurando 
  duplicatas ou overlaps com as keywords: {keywords}"

Task 2 (Explore): "Leia agents/templates/agent.md para 
  o template do novo agente"

Task 3 (WebSearch): "Busque melhores praticas e 
  padroes para {dominio}"
```

Se ja existir agente similar, pergunte: "Ja existe {agente} que cobre parte disso. Quer criar mesmo assim ou adaptar o existente?"

### FASE 3: GERACAO

Monte o arquivo com Write tool:

```
~/.config/opencode/agents/experts/{nome}.md
```

Formato:

```markdown
---
name: {nome}
description: {descricao}
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Task]
---

# {Nome Formatado}

> Role: {descricao}
> Input: Task description from orchestrator
> Output: {output esperado}
> Model: {modelo}

## Especializacao

{2-3 paragrafos descrevendo o dominio, casos de uso, 
e quando o orchestrator deve delegar para este agente}

## Comportamento

1. {instrucao 1}
2. {instrucao 2}
3. {instrucao 3}

## Regras

- {regra 1}
- {regra 2}

## Keywords

{lista de keywords separadas por virgula}
```

Se L2 Specialist, criar em `agents/experts/L2/{nome}.md`.

### FASE 4: REGISTRO

Execute `python scripts/register-agent.py` para:

1. Adicionar entrada no `agents/core/INDEX.md` (tabela de agentes)
2. Adicionar entrada no `agents/system/AGENT_REGISTRY.md` (routing quick-lookup)
3. Adicionar linha na routing table do `agents/core/orchestrator.md`
4. Se L2: adicionar na secao L2 do parent expert

### FASE 5: VALIDACAO

1. Leia o arquivo gerado com Read
2. Verifique frontmatter YAML basico
3. Teste com: `opencode agent list` se disponivel
4. Pergunte: "Quer testar o agente agora com uma task?"

### FASE 6: CONFIRMACAO

Mostre resumo:

```
AGENT CRIADO
  Nome: {nome}
  Nivel: {L1/L2}
  Arquivo: agents/experts/{nome}.md
  Keywords: {keywords}

  Registrado em:
  - agents/core/INDEX.md
  - agents/system/AGENT_REGISTRY.md
  - agents/core/orchestrator.md

  Proximo passo: chame /{nome} ou faca uma task
  que contenha as keywords para ativar.
```

## Edge Cases

- **Nome duplicado**: Pergunte se quer sobrescrever ou escolher outro nome
- **Diretorio agents/experts/L2 nao existe**: Crie automaticamente
- **Sem template**: Use o template hardcoded no SKILL.md como fallback
- **Usuario cancela**: Nao crie nada, apenas confirme o cancelamento
- **Erro no registro**: Registre manualmente e reporte o erro

## Templates Reference

### Template L1 Expert

```markdown
---
name: $NAME
description: $DESCRIPTION
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Task]
---

# $NAME_READABLE

> Role: $DESCRIPTION
> Input: Task description from orchestrator
> Output: $OUTPUT
> Model: $MODEL

## Especializacao

$SPECIALIZATION

## Comportamento

$BEHAVIOR

## Keywords

$KEYWORDS
```

### Template L2 Specialist

```markdown
---
name: $NAME
description: $DESCRIPTION
allowed-tools: [Read, Write, Edit, Glob, Grep]
---

# $NAME_READABLE

> Parent: $PARENT
> Role: $DESCRIPTION
> Input: Task description from orchestrator
> Output: $OUTPUT

## Especializacao

$SPECIALIZATION

## Comportamento

$BEHAVIOR
```
