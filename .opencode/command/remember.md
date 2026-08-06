---
description: Grava o resumo da sessão na memória persistente (MEMORY.md) via memory/session.py
agent: build
---
# OpenCode Core - /remember <resumo>
Salve a sessão atual na memória persistente e versione no git pessoal.

1. Rode `python ~/.config/opencode/memory/session.py status --short` para conferir a sessão ativa.
2. Finalize a sessão:
   `python ~/.config/opencode/memory/session.py end --summary "<resumo>" [--decision "<decisão>" ...] [--file "<arquivo>" ...]`
3. Espelhe no repo pessoal (`~/opencode-core`):
   `python ~/.config/opencode/memory/session.py backup --target ~/opencode-core/memory`
4. Commit + push no repo pessoal:
   `git -C ~/opencode-core add memory/MEMORY.md memory/sessions && git -C ~/opencode-core commit -m "Memória: sessão salva via gatilho" && git -C ~/opencode-core push`
5. Confirme ao usuário: id da sessão, store e o que foi versionado.

Regras:
- Nunca commitar tokens/segredos.
- Se a sessão estiver vazia (sem summary), apenas informe — não forçar `end`.
- Usar sempre `python`, nunca `python3` (não existe neste Windows).
