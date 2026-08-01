---
description: GATILHO DE SALVAMENTO — salva a sessão no store local E no repositório pessoal (git). Use ao final de qualquer interação ou quando o usuário pedir para salvar.
agent: build
---

Execute o gatilho completo de salvamento da sessão atual. Siga SEMPRE estes passos:

1. **Descobertas**: se houve fatos não óbvios na conversa, registre primeiro:
   ```
   python3 memory/session.py log "<descoberta/decisão>"
   ```

2. **Encerrar a sessão** com resumo:
   ```
   python3 memory/session.py end --summary "$ARGUMENTS" [--decision "<decisão>" --file "<arquivo>"]
   ```

3. **Espelhar no repositório pessoal** (o usuário define o caminho com `--target`; se não souber, peça):
   ```
   python3 memory/session.py backup --target <caminho-do-repo-pessoal>/memory
   ```

4. **Versionar no git pessoal** (commitar e enviar):
   ```
   git add memory/MEMORY.md && git commit -m "Memória: sessão salva via gatilho" && git push
   ```

5. **Espelhar recursos genéricos no repo público**: se algum recurso do framework foi criado/alterado (skill, comando, session.py, template), copie a versão genérica para o repo público e faça commit + push.

Depois, confirme ao usuário: id da sessão, local do store e o que foi enviado. Se algo falhar, informe claramente o que ficou pendente.
