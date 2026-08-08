---
name: safe-deploy
description: Publica com preview, validacao de rotas e aprovacao explicita antes da producao.
user-invokable: true
allowed-tools: Read, Glob, Bash
metadata:
  keywords: [deploy, publicar, preview, producao, vercel, validacao]
---

# Deploy Seguro

Use quando o usuario pedir preview, deploy ou publicacao. O objetivo e evitar
que um deploy substitua uma versao funcional sem validacao.

## Fluxo obrigatorio

1. Leia `AGENTS.md`, `README.md`, `vercel.json` e scripts do projeto para confirmar o diretorio e a plataforma corretos.
2. Rode `git diff --check` e os testes/build aplicaveis.
3. Gere um preview. Nao use producao nesta etapa.
4. Valide a raiz e as rotas criticas definidas no projeto.
5. Mostre URL do preview e resultados ao usuario.
6. Aguarde aprovacao explicita para promover/publicar em producao.
7. Depois da producao, valide novamente raiz e rotas criticas e registre o commit/deploy na memoria da sessao.

## Protecoes

- Nunca execute `--prod`, `promote`, `alias set` ou equivalente sem aprovacao explicita recebida na conversa atual.
- Nunca altere segredos ou mostre valores de `.env`.
- Preserve paginas existentes quando uma nova rota for pedida.
- Use `templates/deploy-checklist.md` como registro de validacao para projetos novos.
