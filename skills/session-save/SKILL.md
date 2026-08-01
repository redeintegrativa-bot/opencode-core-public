---
name: session-save
description: AUTO-TRIGGER — SEMPRE executar ao final de qualquer conversa ou tarefa. Persiste descobertas no store local E espelha no repositório pessoal (backup + commit + push). Usar também quando houver fatos novos relevantes no meio da conversa.
user-invokable: true
allowed-tools: Bash, Read
metadata:
  keywords: [save, salvar, gatilho, persistir, memory, git, backup, auto-save]
---

# Session Save — Gatilho de Salvamento

Salva a memória da sessão atual em **duas camadas**, sempre:
1. **Store local (canônico)**: `~/.config/opencode/projects/{hash}/memory/` — sobrevive a updates.
2. **Repositório pessoal (git)**: espelho via `backup` + commit + push.

## Quando disparar (OBRIGATÓRIO)

- **Final de qualquer conversa/tarefa** — antes de encerrar o turno.
- Quando houver **descobertas ou decisões não óbvias** no meio da conversa.
- Quando o usuário invocar `/salvar` ou `/remember`.
- Quando o contexto estiver ficando longo (evitar perda por compactação).

## Passos

1. **Registrar descobertas** (fatos retrabalháveis, decisões, mudanças):
   ```
   python3 memory/session.py log "<descoberta/decisão>"
   ```

2. **Encerrar/atualizar sessão**:
   ```
   python3 memory/session.py end --summary "<resumo>" [--decision "<decisão>" --file "<arquivo>"]
   ```

3. **Espelhar no repositório pessoal**:
   ```
   python3 memory/session.py backup --target <caminho-do-repo-pessoal>/memory
   ```

4. **Versionar no git pessoal**:
   ```
   git add memory/MEMORY.md
   git commit -m "Memória: sessão salva via gatilho"
   git push
   ```

5. **Espelhar recursos genéricos no repo público**: se criou/alterou recurso do framework (skill, comando, session.py, template), copiar a versão genérica para o repo público e fazer commit + push.

## Regras

- Nunca terminar uma sessão com descobertas não salvas.
- Nunca commitar segredos ou tokens.
- No repo público, enviar **apenas recursos genéricos** — nunca dados pessoais ou `MEMORY.md` real (ver `memory/.gitignore`).
- Confirmar ao usuário: id da sessão, local do store e o que foi enviado.
