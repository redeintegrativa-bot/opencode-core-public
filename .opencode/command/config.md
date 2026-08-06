---
description: Revisa ou ajusta permissões e recursos opcionais (recursos opt-in respeitam features.json)
agent: build
---

Revise ou ajuste as permissões do OpenCode e os recursos opcionais do core.

1. **Mostre o estado atual** (somente leitura):
   - Permissões: leia `~/.config/opencode/opencode.json` e mostre o bloco `permission` (ou informe que não há customização).
   - Recursos opcionais: rode `python scripts/features.py list` a partir do repo core (procure em `OPENCODE_CORE_DIR`, `~/opencode-core`, `~/opencode-core-public`) e mostre ativados/desativados.

2. **Aplique o que o usuário pedir:**
   - Mudar permissões: reescreva apenas o bloco `permission` no `opencode.json` preservando o resto do arquivo. Modos disponíveis:
     - **ACESSO TOTAL** → `{"*": "allow"}`
     - **EQUILIBRADO** → básicos (git/pip/npm/node/python/ls/cat/echo) com `allow`, resto `ask`
     - **APROVAR SEMPRE** → `{"*": "ask"}`
   - Ativar/desativar recurso: `python scripts/features.py enable <nome>` ou `disable <nome>`.

3. Confirme ao usuário o que mudou (permissões + recursos) e avise que configurações só valem após reiniciar o OpenCode.

Regras: nunca altere outras chaves do `opencode.json`; se o repo do core não for encontrado, informe e siga só com permissões.
