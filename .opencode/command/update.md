---
description: Atualiza o OpenCode Core (consultivo — mostra o changelog e só aplica com aprovação)
agent: build
---

Verifique e, se aprovado, aplique atualizações do OpenCode Core (repo `redeintegrativa-bot/opencode-core-public`).

1. Localize o repositório na ordem: variável `OPENCODE_CORE_DIR`, depois `~/opencode-core`, `~/opencode-core-public`, ou qualquer diretório com `VERSION` + pasta `scripts/`. Se não achar, pergunte ao usuário.
2. Rode `python scripts/check-update.py --json` (somente leitura) a partir da raiz do repo.
   - Se `has_update: false` → informe "Core atualizado (versão X)" e pare.
   - Se `has_update: true` → mostre o changelog (`local -> remote`) e PEÇA aprovação explícita.
3. Somente com aprovação: rode `python scripts/update.py` (faz git pull/ZIP e reinstala skills/agents/rules/hooks/commands/plugins).
4. Confirme o resultado com `python scripts/check-update.py --json` e resuma a versão nova.

Regras: nunca aplique sem aprovação; nunca adivinhe o caminho do repo — pergunte.
