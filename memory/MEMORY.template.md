# MEMORY.md

Memória persistente entre sessões. Este arquivo é carregado no início de cada sessão
e atualizado ao final (via `memory/session.py` ou comando `/remember`).

## Como usar

- Ao iniciar o trabalho: leia este arquivo e verifique a sessão ativa com
  `python ~/.config/opencode/memory/session.py show`.
- Durante: registre descobertas com `python ~/.config/opencode/memory/session.py log "<texto>"`.
- Ao final: finalize com `python ~/.config/opencode/memory/session.py end --summary "..." [--decision ...] [--file ...]`
  e, se quiser versionar, espelhe para o git pessoal com `backup --target <repo>/memory`.
- Fatos duradouros vão para as seções temáticas abaixo; cada sessão vira um bloco em `## Sessões`.

## Ambiente

- <preencha: sistema, plataforma, limitações do ambiente>

## Projetos

| Projeto | Estado |
|---------|--------|
| <preencha> | <preencha> |

## Sessões
