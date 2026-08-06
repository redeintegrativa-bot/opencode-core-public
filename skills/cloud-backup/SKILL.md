---
name: cloud-backup
description: Guia o usuario a ter backup em nuvem do setup do OpenCode Core (skills, agentes, plugins, memoria) e continuar recebendo as atualizacoes do repositorio publico, mesmo sem conta GitHub. Use quando o usuario perguntar sobre backup, conta, git, nuvem, ou como guardar o setup fora da maquina.
user-invokable: true
metadata:
  keywords: [backup, nuvem, cloud, git, github, conta, sync, atualizar, sem conta, alternativa]
---

# Cloud Backup do Setup (sem depender de conta GitHub)

## Objetivo

Garantir que o setup do usuario (repositorio pessoal + memoria) tenha backup em nuvem e continue
recebendo as atualizacoes do repositorio publico que o mantenedor envia — mesmo se o usuario nao
tiver (ou nao quiser criar) conta no GitHub.

## Como o framework funciona (contexto)

- **Pessoal** (`~/opencode-core`): clone local onde mora o setup customizado do usuario.
- **Publico** (`~/opencode-core-public`): espelho do pessoal com os recursos genericos, que o
  mantenedor atualiza. Receber atualizacoes do publico e' um **pull** — nao exige conta nem login.
- **Plugin auto-sync**: no inicio de cada sessao faz `git pull --ff-only` no pessoal. Se o repo
  pessoal nao tiver `remote` configurado, o plugin loga `skip-no-remote` (sem ruido, sem erro).

## Ponto chave

**Receber atualizacoes do publico NAO exige conta.** Repo publico permite clone/pull anonimo.
O que exige conta e' apenas: (1) backup do seu setup na nuvem, e (2) envio (push) das suas
melhorias. Sao coisas separadas — da pra ter update automatico sem backup na nuvem, e vice-versa.

## Opcoes (em ordem de recomendacao)

### Opcao A — Criar conta gratuita (recomendada)
Contas gratuitas existem em varios servicos de git, nao so GitHub:

| Servico | Conta gratuita | Privado grátis |
|---------|----------------|----------------|
| GitHub | Sim | Sim (repos privados ilimitados) |
| GitLab | Sim | Sim |
| Codeberg | Sim | Sim (sem fins lucrativos, aberto) |
| Bitbucket | Sim | Sim (ate 5 usuarios) |

Fluxo (mesmo para GitHub, GitLab ou Codeberg):
1. Crie a conta e um repo privado vazio (ex.: `opencode-core`).
2. `git remote add origin https://<servico>/<usuario>/opencode-core.git`
3. `git push -u origin master`
4. Daqui em diante o auto-sync puxa atualizacoes do publico se voce adicionar o remote upstream:
   `git remote add upstream https://github.com/<mantenedor>/opencode-core-public.git`

### Opcao B — Sincronizar pasta com nuvem de arquivos (sem git na nuvem)
Se a maquina ja tem OneDrive / Google Drive / Dropbox / Mega:

1. Mova o repo pessoal para dentro da pasta sincronizada:
   `C:\Users\voce\OneDrive\opencode-core` (ou mude o caminho no plugin `OPENCODE_CORE_DIR`).
2. A nuvem sincroniza o conteudo automaticamente (backup passivo).
3. Limitacoes: nao e' versionado no servidor como git; se a pasta for apagada na nuvem, perde.
   Recomendo manter um `git init` local igualmente.

### Opcao C — Backup agendado via zip + nuvem
- Use o comando `/salvar` (session.py backup) e envie o arquivo gerado para a nuvem.
- Ou crie um script simples que zipa `~/.config/opencode` + `~/opencode-core` para OneDrive/Drive.

### Opcao D — Nenhum backup (so atualizacoes)
Perfeitamente viavel: voce continua recebendo updates do publico; so perde o setup local se a
maquina for formatada. Se aceitar esse risco, nao precisa fazer nada.

## Sempre disponivel: receber atualizacoes do publico

Independente da opcao de backup, para continuar recebendo as melhorias do mantenedor:

```bash
# uma vez, se o repo pessoal veio do publico ou esta desatualizado:
git -C ~/opencode-core remote add upstream https://github.com/<mantenedor>/opencode-core-public.git
git -C ~/opencode-core pull upstream master
```

Ou clone direto do publico se nao tiver customizacoes:

```bash
git clone https://github.com/<mantenedor>/opencode-core-public.git ~/opencode-core
```

## Perguntas de triagem

- "Como eu guardo meu setup na nuvem sem GitHub?" → apresente Opcoes A/B/C.
- "Como continuo recebendo suas atualizacoes?" → explique que pull anonimo do publico nao exige conta.
- "Quero backup mas nao quero conta" → Opcao B (nuvem de arquivos) ou C (zip agendado).
- "Ja tenho conta em GitLab/Codeberg" → Opcao A, trocando a URL do remote.
- "Nao quero nada disso" → Opcao D + garantir que auto-sync pule sem erro (ja faz).

## Regras

- Nunca criar conta no lugar do usuario — sempre guiar.
- Nunca pedir senha/token. Se precisar de push, use `~/.git-credentials` via `setup-github-auth.sh`
  (aplica-se tambem a GitLab/Codeberg trocando a URL).
- Preservar as customizacoes do usuario: backup e update nunca sobrescrevem arquivos locais sem
  `git merge` explicito.
