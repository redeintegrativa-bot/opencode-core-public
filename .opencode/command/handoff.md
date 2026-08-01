---
description: Gera um handoff markdown do estado atual para continuar numa sessão futura
agent: build
---

Gere um documento de handoff para que o trabalho possa continuar numa sessão futura sem perder contexto.

Use a skill `handoff` como guia de formato. O documento deve preservar:
- **Estado**: o que foi feito, arquivos modificados, decisões tomadas.
- **Próximos passos**: o que falta fazer, em ordem de prioridade.
- **Contexto**: comandos, caminhos e detalhes não óbvios.

Salve em `context/session-handoff.md` se o diretório `context/` existir no projeto; caso contrário, em `HANDOFF.md`.

Depois, informe ao usuário onde foi salvo e resuma em 3-5 linhas o estado e os próximos passos. Não repita histórico: foque no que importa para a próxima sessão.
