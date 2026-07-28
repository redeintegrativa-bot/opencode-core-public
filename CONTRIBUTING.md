# Contribuindo

Obrigado por contribuir com o **OpenCode Core**! 🚀

## Como contribuir

1. **Fork** o repositório
2. Crie uma **branch** descritiva: `git checkout -b feat/minha-melhoria`
3. Faça suas alterações
4. Rode a validação de segurança: `python3 hooks/validate_security.py .`
5. **Commit** com mensagem clara: `git commit -m "feat: adiciona skill X"`
6. **Push** e abra um **Pull Request**

## Padrões de commit

| Tipo | Uso |
|------|-----|
| `feat:` | Nova skill, agente ou funcionalidade |
| `fix:` | Correção de bug |
| `docs:` | Documentação |
| `chore:` | Manutenção, CI, config |
| `refactor:` | Refatoração sem mudança de comportamento |
| `test:` | Adição ou correção de testes |

## Skills

- Cada skill é um diretório em `skills/` com `SKILL.md`
- Skills user-invocáveis devem ter `slash_command` no `registry.json`
- Skills auto-activadas devem ter `auto_activated` com extensões de arquivo

## Agentes

- Cada agente é um arquivo `.md` em `agents/`
- Agentes L0: `agents/core/`
- Agentes L1: `agents/experts/`
- Agentes L2: `agents/experts/L2/`

## Regras

- Regras comuns: `rules/common/`
- Regras por linguagem: `rules/{python,typescript,go}/`

## Segurança

- **Nunca** commite `.env` ou secrets
- Rode `python3 hooks/validate_security.py .` antes de cada commit
- Todos os tokens e senhas devem vir de variáveis de ambiente

## Dúvidas?

Abra uma [issue](https://github.com/redeintegrativa-bot/opencode-core-public/issues) ou fale com a gente pela **Rede Integrativa**.
