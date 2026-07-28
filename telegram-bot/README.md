# OpenCode Agent — Telegram Interface

Agente de IA autônomo que conecta Telegram ao motor OpenCode.

Cada mensagem é interpretada como uma instrução em linguagem natural
e processada pelo mesmo LLM que roda no terminal (big-pickle).

## Quick Start

```bash
pip install python-telegram-bot python-dotenv  # dependências
cp .env.example .env                            # configurar token
./daemon.sh start                               # iniciar agente
```

## Comandos do daemon

| Comando | Ação |
|---------|------|
| `./daemon.sh start` | Inicia o agente em background |
| `./daemon.sh stop` | Para o agente |
| `./daemon.sh status` | Verifica se está rodando |
| `./daemon.sh logs` | Acompanha logs em tempo real |

## Comandos no Telegram

| Comando | Ação |
|---------|------|
| `/start` | Mensagem de boas-vindas |
| `/status` | Status do agente (uptime, mensagens, sessão) |
| `/help` | Lista de comandos |
| Qualquer texto | Processado pelo motor OpenCode |

## Fluxo do Agente

```
1. Perceber  → Captura a mensagem do usuário
2. Processar → Ativa typing, envia para opencode --format json
3. Responder → Formata e envia a resposta conversacional
```

## Segurança

O primeiro `chat_id` que interagir é automaticamente autorizado.
Mensagens de outros usuários são ignoradas.

Configure manualmente no `.env`:
```
AUTHORIZED_CHAT_ID=seu_chat_id
```

## Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `opencode_agent.py` | Script principal do agente |
| `daemon.sh` | Gerenciador de daemon (start/stop/status/logs) |
| `.env` | Configuração (token, chat_id) |
| `.env.example` | Template de configuração |
| `logs/agent.log` | Logs do agente |
| `requirements.txt` | Dependências Python |
