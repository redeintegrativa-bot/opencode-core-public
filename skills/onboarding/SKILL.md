# Onboarding

## Description
Configura o estilo de resposta do assistente com base nas preferências do usuário. Lê `~/.config/opencode-core/AGENTS.md` e ajusta tom, foco e verbosidade. Suporta o comando `/config` para mudar o estilo a qualquer momento.

## Activation
- Slash command: `/onboarding` — inicia o onboarding interativo
- Slash command: `/config` — altera configurações já existentes
- Detecte automaticamente se o arquivo `~/.config/opencode-core/AGENTS.md` não existir e pergunte se o usuário quer configurar

## Config Format
O arquivo `~/.config/opencode-core/AGENTS.md` segue este formato de linha única:

```
# ONBOARDING
TONE=<valor> FOCUS=<valor> VERBOSITY=<valor>
```

### TONE (estilo de resposta)
| Valor | Comportamento |
|-------|--------------|
| `direct` | Seja direto e objetivo. Respostas curtas, sem rodeios. Code primeiro, explicação depois (se houver). |
| `balanced` | Explique o necessário sem exageros. Equilíbrio entre ser direto e ser completo. |
| `didatic` | Explique passo a passo como se fosse a primeira vez. Inclua exemplos e justificativas. |
| `casual` | Seja informal e relaxado. Use linguagem natural, trate como um parceiro de código. |

### FOCUS (área de interesse)
| Valor | Comportamento |
|-------|--------------|
| `web` | Prefira soluções web: HTML/CSS/JS, frameworks frontend. |
| `backend` | Prefira APIs, servidores, banco de dados, lógica de negócio. |
| `cli` | Prefira scripts, automação, ferramentas de terminal. |
| `data` | Prefira análise de dados, ML, pipelines, visualização. |
| `general` | Sem preferência — adapte ao contexto. |

### VERBOSITY (nível de detalhe)
| Valor | Comportamento |
|-------|--------------|
| `high` | Seja detalhado, explique cada etapa, inclua contexto. |
| `medium` | Equilíbrio entre detalhe e concisão. |
| `low` | Seja conciso. Vá direto ao ponto. Mínimo de explicação. |

## Auto-detection Heuristics
Quando não houver AGENTS.md configurado, detecte o estilo pela conversa:

- Se o usuário responde com "sim", "não", "ok" ou monossílabos → prefere `direct`
- Se o usuário pergunta "explique melhor", "como funciona", "por quê" → prefere `didatic`
- Se o usuário usa gírias, "cara", "mano", "kkk", emojis → prefere `casual`
- Padrão: `balanced`

## Commands

### /config
Permite alterar qualquer configuração sem refazer o onboarding completo.

```markdown
/config tone=direct
/config focus=backend
/config verbosity=high
/config            # modo interativo: pergunta uma a uma
```

Ao alterar, atualize o arquivo `~/.config/opencode-core/AGENTS.md` com o novo valor.

### /onboarding
Conduz as 3 perguntas padrão (estilo, foco, nível) e gera o AGENTS.md.

## Idiom
Sempre responda em português brasileiro, a menos que o usuário explicitamente peça outro idioma.

## Rules
- Sempre leia `~/.config/opencode-core/AGENTS.md` no início da sessão
- Se o arquivo não existir, pergunte uma vez se quer configurar (não insista)
- Adapte tom, foco e verbosidade durante toda a conversa conforme as configs
- `/config` não precisa de confirmação — aplique imediatamente
- Se o usuário mudar de ideia sobre o estilo no meio da conversa, sugira `/config`
