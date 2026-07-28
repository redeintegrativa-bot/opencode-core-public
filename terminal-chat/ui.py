#!/usr/bin/env python3
"""UI components for terminal chat."""

import sys
import time
from datetime import datetime

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.spinner import Spinner
from rich.text import Text
from rich.theme import Theme

THEME = Theme({
    "user":      "bold cyan",
    "agent":     "bold green",
    "system":    "dim white",
    "error":     "bold red",
    "header":    "bold magenta",
    "timestamp": "dim",
    "cmd":       "bold yellow",
    "code":      "bold white on grey11",
})

console = Console(theme=THEME, highlight=False)

def print_banner(agent_name: str = "OpenCode", agent_icon: str = "🤖"):
    console.print()
    console.print(Panel(
        f"[header]{agent_icon} {agent_name} Terminal Chat[/header]\n"
        "[system]Mesmo motor do terminal · big-pickle · --format json[/system]\n"
        "[system]Digite [cmd]/help[/cmd] para comandos, [cmd]/quit[/cmd] para sair[/system]",
        border_style="magenta",
        padding=(0, 2),
    ))
    console.print()

def print_user(msg: str):
    ts = datetime.now().strftime("%H:%M")
    console.print(f"[timestamp]{ts}[/timestamp] [user]Você:[/user] {msg}")

def print_agent_start(agent_icon: str = "🤖", agent_name: str = "Agente"):
    ts = datetime.now().strftime("%H:%M")
    console.print(f"[timestamp]{ts}[/timestamp] [agent]{agent_icon} {agent_name}:[/agent]")

def print_agent_chunk(text: str):
    """Print a chunk of streaming text without newline."""
    console.print(text, end="", highlight=False)

def print_agent_end():
    """End the agent response block."""
    console.print()
    console.print()

def print_system(msg: str):
    console.print(f"[system]{msg}[/system]")

def print_error(msg: str):
    console.print(f"[error]{msg}[/error]")

def print_status(agent_name: str, agent_icon: str, msg_count: int, uptime: float, session_id: str):
    h, r = divmod(int(uptime), 3600)
    m, s = divmod(r, 60)
    console.print()
    console.print(Panel(
        f"[agent]Agente:[/agent]       {agent_icon} {agent_name}\n"
        f"[agent]Uptime:[/agent]       {h}h {m}m {s}s\n"
        f"[agent]Mensagens:[/agent]    {msg_count}\n"
        f"[agent]Sessão:[/agent]       {session_id}\n"
        f"[agent]Motor:[/agent]        opencode/big-pickle\n"
        f"[agent]Formato:[/agent]      JSON streaming",
        title="[header]Status[/header]",
        border_style="green",
    ))
    console.print()

def print_agents(agents: list, current: str):
    console.print()
    lines = []
    for a in agents:
        marker = " ✓" if a.name == current else ""
        lines.append(f"{a.icon} [cmd]{a.name}[/cmd] — {a.description}{marker}")
    console.print(Panel(
        "\n".join(lines),
        title="[header]Agentes Disponíveis[/header]",
        border_style="cyan",
    ))
    console.print()

def print_sessions(sessions: list):
    console.print()
    if not sessions:
        console.print("[system]Nenhuma sessão salva.[/system]")
        console.print()
        return
    lines = []
    for i, s in enumerate(sessions, 1):
        lines.append(f"  [cmd]{i}[/cmd]. {s['title']} — {s['messages']} msgs ({s['agent']})")
    console.print(Panel(
        "\n".join(lines),
        title="[header]Sessões Anteriores[/header]",
        border_style="yellow",
    ))
    console.print()

class Spinner:
    """Animated spinner for typing indicator."""
    
    def __init__(self, text: str = "Pensando"):
        self.text = text
        self._running = False
        self._thread = None
    
    def start(self):
        self._running = True
        import threading
        def _spin():
            chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
            i = 0
            while self._running:
                sys.stdout.write(f"\r\033[K  {chars[i % len(chars)]} {self.text}...")
                sys.stdout.flush()
                time.sleep(0.1)
                i += 1
        self._thread = threading.Thread(target=_spin, daemon=True)
        self._thread.start()
    
    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=0.5)
        sys.stdout.write("\r\033[K")
        sys.stdout.flush()
