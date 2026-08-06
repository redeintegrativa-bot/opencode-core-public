# Backup em Nuvem do Setup — sem depender de conta GitHub

## Contexto

Este repositorio é a base do seu setup do OpenCode Core. Ele tem duas "versões":

| Repo | Papel | URL de exemplo |
|------|-------|----------------|
| `~/opencode-core` (pessoal) | Seu setup customizado (agentes, skills, plugins, memoria) | `https://github.com/<seu-usuario>/opencode-core` |
| `~/opencode-core-public` (publico) | Recursos genericos mantidos e atualizados pelo mantenedor | `https://github.com/<mantenedor>/opencode-core-public` |

**Ponto importante:** receber as atualizações do repositório público **não exige conta** — clone
e `git pull` de um repo público funcionam de forma anônima. Conta é necessária apenas para
**backup do seu setup na nuvem** e para **enviar (push)** suas melhorias.

## Opções de backup (escolha 1)

### Opção A — Conta gratuita (recomendada)
Vários serviços oferecem repo privado grátis: **GitHub**, **GitLab**, **Codeberg**, **Bitbucket**.

```bash
cd ~/opencode-core
git remote add origin https://<servico>/<seu-usuario>/opencode-core.git
git push -u origin master

# para continuar recebendo as atualizações do público:
git remote add upstream https://github.com/<mantenedor>/opencode-core-public.git
git pull upstream master
```

### Opção B — Nuvem de arquivos (sem git na nuvem)
Mova `~/opencode-core` para dentro da pasta sincronizada (OneDrive/Google Drive/Dropbox/Mega) e
configure `OPENCODE_CORE_DIR` para o novo caminho. A nuvem faz backup passivo; mantenha um
`git init` local para versionar de verdade.

### Opção C — Zip agendado
Use `/salvar` (session.py backup) e envie o arquivo para a nuvem, ou agende um zip de
`~/.config/opencode` + `~/opencode-core` para OneDrive/Drive.

### Opção D — Nenhum backup
Você continua recebendo as atualizações do público; só corre o risco de perder o setup local se a
máquina for formatada.

## Receber atualizações (funciona sempre, sem conta)

```bash
# sem customizações — clone direto do público:
git clone https://github.com/<mantenedor>/opencode-core-public.git ~/opencode-core

# com customizações — adicione o público como upstream:
git -C ~/opencode-core remote add upstream https://github.com/<mantenedor>/opencode-core-public.git
git -C ~/opencode-core pull upstream master
```

O plugin `auto-sync` detecta a ausência de `remote` no repo pessoal e apenas registra
`skip-no-remote` (sem erro, sem ruído), então o setup funciona normalmente mesmo sem nenhuma conta.

## Autenticação para push (quando houver conta)

Use o script genérico (não grava segredo no repo):

```bash
GH_TOKEN=<token> ./scripts/setup-github-auth.sh <owner> <repo> [<repo>...] [--check]
```

Aplica-se a GitLab/Codeberg trocando a URL do remote; o token é gravado em `~/.git-credentials`
(perms 600).
