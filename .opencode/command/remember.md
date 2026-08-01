---
description: Grava o resumo da sessão na memória persistente (MEMORY.md) via memory/session.py
agent: build
---

Registre a sessão atual na memória persistente.

Execute, a partir da raiz do projeto:

```
python3 memory/session.py end --summary "$ARGUMENTS"
```

Se a sessão tiver decisões ou arquivos relevantes, inclua `--decision "<decisão>"` e `--file "<path>"`.

Se o projeto usar o store local (git pessoal), adicione `--local`.

Depois, confirme ao usuário o id da sessão gravada e o local do store
(`python3 memory/session.py stats`).
