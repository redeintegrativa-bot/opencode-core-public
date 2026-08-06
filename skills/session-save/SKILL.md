---
name: session-save
description: AUTO-TRIGGER — SEMPRE executar ao final de qualquer conversa ou tarefa E registrar descobertas no meio da conversa (salvamento contínuo). Persiste no store local E espelha no repositório pessoal (backup + commit + push).
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
- **Após cada resposta importante** (salvamento contínuo): se houve descoberta, decisão ou fato novo relevante, registrar na hora com `log` — não esperar o fim. Assim nada se perde se a conversa morrer no meio.
- Quando o usuário invocar `/salvar` ou `/remember`.
- Quando o contexto estiver ficando longo (evitar perda por compactação).

**Antes de salvar, use a skill `session-triage` para decidir SE e ONDE salvar.** Nem tudo merece memória.

## Salvamento contínuo vs. salvamento final

| Momento | O que fazer |
|---------|-------------|
| **Durante a conversa** (após resposta com fato novo) | `session.py log "<descoberta>"` — só no store local, rápido, sem git |
| **Fim de tarefa/conversa** | Fluxo completo: `end` → `backup` → commit + push pessoal |
| **Milestone/etapa grande** | Fluxo completo (não esperar o fim absoluto) |

No salvamento contínuo, **não** commitar a cada log — isso enche o histórico de git. Commit ocorre no fluxo final (ou a cada milestone).

## Passos

1. **Registrar descobertas** (fatos retrabalháveis, decisões, mudanças):
   ```
   python ~/.config/opencode/memory/session.py log "<descoberta/decisão>"
   ```

2. **Encerrar/atualizar sessão**:
   ```
   python ~/.config/opencode/memory/session.py end --summary "<resumo>" [--decision "<decisão>" --file "<arquivo>"]
   ```

3. **Espelhar no repositório pessoal**:
   ```
   python ~/.config/opencode/memory/session.py backup --target <caminho-do-repo-pessoal>/memory
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
