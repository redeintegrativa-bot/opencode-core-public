---
description: Mostra a saude Git dos projetos locais sem modificar nada.
agent: analyzer
---

1. Localize o OpenCode Core em `OPENCODE_CORE_DIR`, `~/opencode-core` ou `~/opencode-core-public`.
2. Execute `python scripts/project-health.py --root ~/projects`.
3. Resuma projetos pendentes, branch e ultimo commit.
4. Nao execute commit, push, pull, testes ou deploy.
