---
name: session-resume
description: Auto-resume between sessions using persistent MEMORY.md. Use at the start of a session to load prior context and at the end to record a session summary via /remember.
user-invokable: true
allowed-tools: Read, Bash, Glob
metadata:
  keywords: [resume, session, memory, continue, retomar, histórico]
---

# Session Resume

Mantém continuidade entre sessões usando a memória persistente (`memory/session.py`).
Previne retrabalho: ao abrir uma sessão, carrega o contexto anterior; ao fechar, grava o que foi feito.

## Local da memória

- Global (padrão): `~/.config/opencode/projects/{hash}/memory/` — sobrevive a qualquer update do repo.
- Local (repo): `<root>/memory/` — usado com `--local` (ex.: git pessoal).

## Protocolo

### 1. Início de sessão (SILENCIOSO)

```
python ~/.config/opencode/memory/session.py status --short
```

- Leia o status e o `MEMORY.md` internamente (via Read/Bash) **sem despejar o conteúdo no chat**.
- Se não houver `MEMORY.md`, rode `python ~/.config/opencode/memory/session.py init` silenciosamente.
- Não imprima o MEMORY.md completo nem blocos longos. No máximo, uma linha: "Retomando de <projeto>: <tema da última sessão>".
- Console deve permanecer limpo, no formato padrão do opencode.

### 2. Durante a sessão

Registre descobertas relevantes (decisões, descobertas não óbvias):

```
python ~/.config/opencode/memory/session.py log "<descoberta/decisão>"
```

### 3. Final de sessão

```
python ~/.config/opencode/memory/session.py end \
  --summary "<resumo geral>" \
  --decision "<decisão>" \
  --file "<arquivo tocado>"
```

- Se o usuário invocar `/remember <resumo>`, use este comando `end`.
- **OBRIGATÓRIO (gatilho `session-save`)**: ao final de qualquer conversa, além do `end`, fazer `backup` para o repositório pessoal + `git commit`/`push`. Espelhar recursos genéricos no repo público.

### 4. Manutenção

- `python ~/.config/opencode/memory/session.py stats` — estado do store.
- `python ~/.config/opencode/memory/session.py compress --keep 60` — podar sessões antigas.

## Regras

- Fatos duradouros vão para as seções temáticas do `MEMORY.md` (Ambiente/Projetos).
- Sessões são blocos `## Sessão` rotacionados para `sessions/`.
- Nunca commitar `MEMORY.md`/sessões no repo público (ver `memory/.gitignore`).
