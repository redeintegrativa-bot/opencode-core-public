# OpenCode Core — Infrastructure Hub

Repositório central com definições de agentes, skills, regras e serviços compartilhados do ecossistema **Rede Integrativa**.

> 🚀 Este é um **template reutilizável** — use todo o poder do core nos seus projetos!  
> 💡 Precisa de controle financeiro? O app **My Money Track** (`/my-money-track`) já está aqui como um template pré-pronto pra você adaptar!

---

## ⚡ Instalação rápida (1 comando)

```bash
git clone --depth 1 https://github.com/redeintegrativa-bot/opencode-core-public.git
cd opencode-core-public
bash setup.sh        # Linux/macOS/Termux
# ou
.\setup.ps1          # Windows PowerShell
```

Isso instala automaticamente skills, agentes, regras e hooks no seu ambiente.

### 🎯 Onboarding — configure o assistente do SEU jeito

Antes de comecar, personalize como o assistente vai falar com voce:

```bash
python onboarding.py
```

**Voce escolhe como quer configurar:**

```
[1] CONSOLE — dialogos passo a passo no terminal (recomendado)
[2] NAVEGADOR — formulario web em http://localhost:8080
```

**Os dois fazem as mesmas 3 perguntas** com exemplos visuais:

```
[1] DIRETO     → "Cria routes/users.js com handler GET."
[2] EQUILIBRADO → "Cria routes/users.js. Recomendo express.Router()."
[3] DIDATICO   → "Passo 1: crie o arquivo... Passo 2: adicione a rota..."
[4] RELAXADO   → "Bora! Cria o arquivo e bota a rota la!"
```

Gera uma config de 2 linhas (~20 tokens).
Pra mudar depois, digite `/config` no chat.

📖 Quer entender a estrutura completa? Veja `docs/estrutura.md`.

### 📊 Dashboard local (web)

Painel completo com status, test drive e onboarding:

```bash
python dashboard/server.py
# Acesse: http://localhost:8080
```

**O que tem no dashboard:**
- **Status** — config atual, stats do sistema, dependencias
- **Test Drive** — monte seu projeto: escolhe opcoes, gera prompt pra copiar e colar no OpenCode
- **Capacidades** — lista completa do que voce pode fazer
- **Onboarding web** — acesse `/onboarding` pra configurar pelo navegador

Funciona no navegador do PC ou do Termux (Android).

### Instalação por plataforma

| Plataforma | Comando |
|-----------|---------|
| **Claude Code** | `claude plugin install redeintegrativa-bot/opencode-core-public` |
| **OpenCode** | Clone + `bash setup.sh` |
| **Codex** | `codex plugin install redeintegrativa-bot/opencode-core-public` |

---

## 📦 O que vem incluído

| Diretório | Finalidade |
|-----------|-----------|
| `agents/` | Definições de 43 agentes (L0 core, L1 experts, L2 especialistas) |
| `skills/` | 33 skills (code-review, debugging, plan, tdd, security, etc.) |
| `rules/` | 110 regras de segurança e boas práticas por linguagem |
| `hooks/` | Scripts de validação e segurança (pré-commit, secrets scan) |
| `workflows/` | Workflows padronizados (bugfix, feature, refactoring) |
| `services/` | Serviços compartilhados (scoring, learning, ranking) |
| `providers/` | Providers de dados DeFi/crypto (CoinGecko, DexScreener, etc.) |
| `memory/` | Camada de persistência de memória |
| `templates/` | Templates reutilizáveis de configuração |
| `terminal-chat/` | Chat TUI em Python (Rich + Prompt Toolkit) |
| `telegram-bot/` | Bot Telegram (desativado — configure seu token) |
| `my-money-track/` | 📊 App de controle financeiro **template** |
| `patterns/` | Padrões de pipeline de conteúdo |
| `.github/` | GitHub Actions CI/CD workflows |
| `.claude-plugin/` | Plugin manifest para Claude Code marketplace |
| `.opencode/` | Configuração do OpenCode |
| `.codex-plugin/` | Plugin manifest para Codex |

---

## 🚀 Como usar

### 1. Instale (já fez? pule)
```bash
bash setup.sh --skills
```

### 2. Explore agentes e skills
```bash
ls agents/core/
ls skills/ | head -20
cat skills/registry.json | python3 -m json.tool | head -30
```

### 3. Terminal chat
```bash
cd terminal-chat
pip install rich prompt_toolkit
python3 opencode_chat.py
```

### 4. My Money Track (opcional)
```bash
cd my-money-track
cp .env.example .env
npm install
npm run dev
```

---

## 🧠 My Money Track — Template Financeiro

App de controle financeiro **pré-pronto** da **Rede Integrativa**.

**Para usar:**
1. Edite `src/data.js` com seus próprios dados financeiros
2. Personalize as categorias de despesas e receitas
3. Faça deploy (Vercel, Netlify, etc.)

💡 Peça ao assistente: *"Me ajuda a configurar o My Money Track com minhas finanças"*

---

## 🔒 Segurança

- **Nunca commite `.env`** — ele está no `.gitignore`
- **Sem tokens hardcoded** — use variáveis de ambiente
- Rode `python3 hooks/validate_security.py .` antes de commitar

---

## 🤝 Rede Integrativa

Este repositório faz parte do ecossistema **Rede Integrativa**.

- GitHub: https://github.com/redeintegrativa-bot
- Mais projetos: AIOS, Crypto Platform, Content Engine, e mais

---

Criado por: **Rede Integrativa** 🚀
