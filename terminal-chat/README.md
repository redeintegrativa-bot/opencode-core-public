# Terminal Chat — OpenCode Core

Chat TUI que conecta direto ao motor OpenCode. Funciona em **Termux**, **Linux** e **Windows**.

## Instalação

```bash
# Termux (Android)
pkg install python
pip install rich prompt_toolkit
python opencode_chat.py

# Linux
pip3 install rich prompt_toolkit
python3 opencode_chat.py

# Windows
pip install rich prompt_toolkit
python opencode_chat.py
```

## Comandos

| Comando | Ação |
|---------|------|
| `/help` | Lista de comandos |
| `/status` | Status do agente |
| `/agents` | Lista e troca de agentes |
| `/agent <nome>` | Troca para agente específico |
| `/sessions` | Sessões salvas |
| `/save` | Salva sessão |
| `/clear` | Limpa a tela |
| `/quit` | Sair |

## Funciona em qualquer terminal

- Android (Termux) ✅
- Linux ✅
- macOS ✅
- Windows PowerShell ✅
