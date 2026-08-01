---
name: session-triage
description: Decide SE e ONDE salvar uma informação. Classifica em camadas (perfil, sessão, git pessoal, público) com critérios claros. Usar antes de cada session.py log/end e sempre que o usuário perguntar o que deve ser salvo.
user-invokable: true
allowed-tools: Bash, Read
metadata:
  keywords: [save, salvar, decidir, triage, critérios, o que salvar, memory]
---

# Session Triage — Decidir o que salvar

Antes de salvar qualquer coisa, classificar a informação. Nem tudo merece memória.

## Roda rápida (3 perguntas)

1. **Vai ser óbvio na próxima sessão sem salvar?** → **NÃO salvar** (é ruído).
2. **É retrabalhável e não óbvio?** → **SALVAR** (decisão, descoberta, preferência, mudança).
3. **É sensível?** (senha, token, dado pessoal que o usuário NÃO pediu para guardar) → **NUNCA salvar**.

## Onde salvar (classificação por camada)

| Camada | O que vai | Onde |
|--------|-----------|------|
| **Perfil** | Fatos duradouros do usuário (quem é, identidade, preferências, kin, datas) | MEMORY.md de boot + store |
| **Sessão** | Decisões, descobertas, progresso, erros corrigidos, mudanças feitas | `session.py log` / `end` |
| **Git pessoal** | Tudo acima, espelhado | `backup --target` + commit + push |
| **Público** | APENAS recursos genéricos do framework (skills, comandos, scripts, templates) | repo público + commit + push |

## Regras de ouro

- **Dúvida?** Salva na sessão (é barato) — não no perfil.
- **Fato que muda pouco** (nascimento, nome, kin, preferências) → perfil.
- **Estado temporário** (`.bak`, `.state.json`, cache) → **nunca** no git.
- **Recurso do framework** → sempre pessoal **e** público, em par.
- **Dado pessoal sensível** → só com pedido explícito do usuário.
- **Palpite/opinião não confirmada** → não salvar como fato.

## Se for borderline

- Salvar na sessão e **avisar o usuário**: "salvei X, não salvei Y porque...".
- Deixar claro o que ficou de fora — o usuário decide se quer forçar.

## Anti-regras (exemplos de NÃO salvar)

- "Oi", "ok", "obrigado" e ruído de conversa.
- Código que já está versionado no próprio repo.
- Erros temporários que já se resolveram sozinhos.
- Info que o usuário pediu explicitamente para esquecer.
