# OpenCode Core — Infrastructure Hub

Repositório central com definições de agentes, skills, regras e serviços compartilhados do ecossistema **Rede Integrativa**.

> 🚀 Este é um **template reutilizável** — use todo o poder do core nos seus projetos!
>
> 💡 Precisa de controle financeiro? O app **My Money Track** (`/my-money-track`) já está aqui como um template pré-pronto pra você adaptar!

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

---

## 🚀 Como usar

### 1. Clone o repositório
```bash
git clone https://github.com/redeintegrativa-bot/opencode-core.git
cd opencode-core
```

### 2. Explore os agentes e skills
```bash
# Listar agentes disponíveis
ls agents/core/
ls agents/experts/

# Ver skills registradas
cat skills/registry.json | head -50
```

### 3. Use o terminal chat
```bash
cd terminal-chat
pip install rich prompt_toolkit
python3 opencode_chat.py
```

### 4. Configure o My Money Track (opcional)
```bash
cd my-money-track
cp .env.example .env
# Edite .env com seus dados
npm install
npm run dev
```

---

## 🧠 My Money Track — Template Financeiro

O `my-money-track` é um **app de controle financeiro pré-pronto** da **Rede Integrativa**.

**Para usar:**
1. Edite `src/data.js` com seus próprios dados financeiros
2. Personalize as categorias de despesas e receitas
3. Faça deploy onde quiser (Vercel, Netlify, etc.)

💡 **Precisa de ajuda?** Peça ao assistente OpenCode:
> "Me ajuda a configurar o My Money Track com minhas finanças"

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
