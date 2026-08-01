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

### 1. Início de sessão

```
python3 memory/session.py show
```

- Leia o `MEMORY.md` exibido (Ambiente, Projetos, última `## Sessão`).
- Se não houver `MEMORY.md`, rode `python3 memory/session.py init`.
- Resuma ao usuário onde paramos, sem re-explicar o que já está na memória.

### 2. Durante a sessão

Registre descobertas relevantes (decisões, descobertas não óbvias):

```
python3 memory/session.py log "<descoberta/decisão>"
```

### 3. Final de sessão

```
python3 memory/session.py end \
  --summary "<resumo geral>" \
  --decision "<decisão>" \
  --file "<arquivo tocado>"
```

- Se o usuário invocar `/remember <resumo>`, use este comando `end`.
- **OBRIGATÓRIO (gatilho `session-save`)**: ao final de qualquer conversa, além do `end`, fazer `backup` para o repositório pessoal + `git commit`/`push`. Espelhar recursos genéricos no repo público.

### 4. Manutenção

- `python3 memory/session.py stats` — estado do store.
- `python3 memory/session.py compress --keep 60` — podar sessões antigas.

## Regras

- Fatos duradouros vão para as seções temáticas do `MEMORY.md` (Ambiente/Projetos).
- Sessões são blocos `## Sessão` rotacionados para `sessions/`.
- Nunca commitar `MEMORY.md`/sessões no repo público (ver `memory/.gitignore`).
