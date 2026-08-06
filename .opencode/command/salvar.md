---
description: GATILHO DE SALVAMENTO — salva a sessão no store local E no repositório pessoal (git). Use ao final de qualquer interação ou quando o usuário pedir para salvar.
agent: build
---
# OpenCode Core - /salvar (gatilho session-save)
Salve as descobertas da conversa atual e finalize a sessão (salvamento contínuo + versão).

1. **Registre descobertas pendentes** com `python ~/.config/opencode/memory/session.py log "<texto>"` para cada fato novo não salvo (decisões, mudanças, erros corrigidos). Use a skill `session-triage` para decidir o que merece memória.
2. **Finalize a sessão**:
   `python ~/.config/opencode/memory/session.py end --summary "<resumo geral>" [--decision "<decisão>" ...] [--file "<arquivo>" ...]`
3. **Espelhe no repo pessoal** (`~/opencode-core`):
   `python ~/.config/opencode/memory/session.py backup --target ~/opencode-core/memory`
4. **Versionar**:
   `git -C ~/opencode-core add memory/MEMORY.md memory/sessions && git -C ~/opencode-core commit -m "Memória: sessão salva via gatilho" && git -C ~/opencode-core push`
5. **Recursos genéricos** (se criou/alterou skill, comando ou script do framework): espelhar a versão genérica no repo público (nunca MEMORY.md real):
   - `python ~/opencode-core/scripts/sync-public.py --check` (ver pendências)
   - Se houver e o usuário aprovar: `python ~/opencode-core/scripts/sync-public.py --push`
   - Caso contrário: `python ~/opencode-core/scripts/sync-public.py --stage` (deixa pronto, push depois)

Regras:
- Não commitar a cada `log` — apenas no fluxo final (ou milestone).
- Nunca commitar tokens/segredos nem `MEMORY.md` no repo público.
- Usar sempre `python`, nunca `python3` (não existe neste Windows).
