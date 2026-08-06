# Estrutura do OpenCode Core

Esse repositorio e um **kit de ferramentas** pro OpenCode.
Pense nele como um canivete suico: tem ferramentas pra tudo que voce precisar.

---

## `agents/` — Os ajudantes

**O que sao:** Cada agente e um "especialista" que o OpenCode chama quando precisa.
Voce nao precisa escolher um agente — o OpenCode escolhe automaticamente.

**Exemplo:** Se voce pedir "revisa esse codigo", o OpenCode ativa o agente **Reviewer**,
que le o codigo e aponta problemas como um colega senior faria.

| Pasta | Pra que serve |
|-------|---------------|
| `agents/core/` | Essenciais: orquestrador, programador, revisor, etc. |
| `agents/experts/` | Especialistas: seguranca, banco de dados, DevOps, etc. |
| `agents/specialists/` | Super especialistas: autenticacao, testes, layout, etc. |

---

## `skills/` — Comandos rapidos

**O que sao:** Atalhos pra tarefas comuns. So digitar `/comando` no chat.

**Exemplo:**
- `/review` — revisa o codigo
- `/debug` — ajuda a encontrar bugs
- `/plan` — planeja uma implementacao
- `/scaffold` — cria projeto do zero
- `/database` — ajuda com banco de dados
- `/update-core` — atualiza o core

**Lista completa e contagem:** `skills/registry.json`

---

## `rules/` — Regras de seguranca

**O que sao:** Instrucoes que o OpenCode segue automaticamente.
Nao precisa fazer nada — elas ja estao ativas.

**Exemplo:** Regra que impede o OpenCode de sugerir codigo inseguro
ou de expor senhas e tokens.

---

## `workflows/` — Receitas prontas

**O que sao:** Passo a passo pra tarefas comuns do dia a dia.

**Exemplo:**
- `bugfix.md` — como corrigir um bug do inicio ao fim
- `feature.md` — como adicionar uma funcionalidade nova
- `refactoring.md` — como melhorar codigo existente

---

## `hooks/` — Seguranca automatica

**O que sao:** Scripts que rodam antes de cada commit pra evitar erros.

**Exemplo:** `hooks/validate_security.py` — varre o codigo procurando
senhas, tokens e chaves vazadas.

---

## `services/` — Funcionalidades extras

**O que sao:** Ferramentas que o OpenCode usa internamente.

- `scoring/` — avalia a qualidade das respostas
- `learning/` — aprende com o uso e melhora com o tempo
- `ranking/` — decide qual agente e melhor pra cada tarefa

---

## `terminal-chat/` — Chat proprio

**O que sao:** Um programa Python que roda no terminal (inclusive Termux!).

**Como usar:**
```bash
cd terminal-chat
pip install rich prompt_toolkit
python opencode_chat.py
```

---

## `my-money-track/` — App financeiro template

**O que sao:** Um aplicativo de controle financeiro pronto pra usar.
So precisa editar os dados.

**Como usar:**
```bash
cd my-money-track
npm install
npm run dev
```

---

## Outras pastas

| Pasta | Pra que serve |
|-------|---------------|
| `.opencode/` | Configuracao do OpenCode |
| `.claude-plugin/` | Plugin pro Claude Code |
| `.codex-plugin/` | Plugin pro Codex |
| `templates/` | Modelos reutilizaveis |
| `providers/` | Dados de criptomoedas e DeFi |
| `memory/` | O OpenCode lembra de sessoes anteriores |

---

## Arquivos importantes

| Arquivo | Pra que serve |
|---------|---------------|
| `setup.sh` | Instala tudo (Linux/Termux) |
| `setup.ps1` | Instala tudo (Windows) |
| `onboarding.py` | Configura o assistente do seu jeito |
| `Makefile` | Atalhos: `make setup`, `make chat`, `make validate` |

---

## Como usar na pratica

**1. Instalar:**
```bash
bash setup.sh
```

**2. Configurar o assistente:**
```bash
python onboarding.py
```

**3. Usar o OpenCode:**
```bash
# O OpenCode ja reconhece skills, agentes e regras automaticamente
# So digitar o que precisa
```

**Dica:** Se tiver duvida sobre algo, me pergunte! Posso explicar
cada parte em detalhe.
