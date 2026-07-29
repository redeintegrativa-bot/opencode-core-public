# Onboarding

## Description
Conduz o usuário por uma série de perguntas para personalizar a experiência do OpenCode Core. Gera AGENTS.md e profile.json com as preferências.

## Activation
Slash command: `/onboarding` ou quando o usuário parece estar usando o sistema pela primeira vez.

Detecte automaticamente se o arquivo `~/.config/opencode-core/profile.json` não existir — pergunte se o usuário quer fazer o onboarding.

## Questions

### 1. Como quer ser chamado?
Nome ou apelido do usuário.

### 2. Idioma preferido?
- Português
- English
- Español

### 3. Estilo de resposta?
- **Direto e seco** — vai direto ao ponto, sem rodeios
- **Equilibrado** — explica o necessário
- **Didático** — explica passo a passo
- **Relaxado** — informal, como um parceiro

### 4. Nível de experiência?
- **Iniciante** — nunca programou
- **Intermediário** — já faz projetos
- **Avançado** — dev profissional
- **Expert** — arquiteto/sênior

### 5. Foco principal?
- Desenvolvimento Web
- Backend/API
- Automação/CLI
- Segurança
- Dados/ML
- Geral

### 6. Onde vai usar o OpenCode?
- Termux (Android)
- Linux
- Windows PowerShell
- macOS

### 7. Quer usar o app de controle financeiro (My Money Track)?
- Sim
- Talvez depois
- Não

## Output
Gere o arquivo `~/.config/opencode-core/profile.json` e `~/.config/opencode-core/AGENTS.md` com as respostas.

O AGENTS.md gerado deve começar com:

```markdown
# AGENTS.md — Personalizado para {nome}
```

E conter as regras de estilo, idioma e perfil.

## Rules
- Faça uma pergunta de cada vez
- Espere a resposta antes de prosseguir
- Seja amigável e acolhedor na primeira pergunta
- Ao final, mostre um resumo do que foi configurado
- Sugira os próximos passos (setup.sh, terminal-chat, My Money Track)
