---
name: project-health
description: Diagnostica todos os repositorios locais sem modificar arquivos ou executar testes.
user-invokable: true
allowed-tools: Read, Bash
metadata:
  keywords: [status, saude, diagnostico, projetos, git]
---

# Saude dos Projetos

Execute `python scripts/project-health.py --root ~/projects` para ver branch,
ultimo commit e alteracoes locais de cada repositorio. Use `--json` para
dashboards e automacoes.

Para o resumo diario local, execute `python scripts/daily-summary.py`. Ele
grava apenas em `~/.config/opencode/daily/` e nunca toca nos repositorios.

Nao execute commit, push, pull, testes ou deploy durante este diagnostico.
