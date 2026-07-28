#!/usr/bin/env python3
"""
OpenCode Terminal Chat — Interface de chat com streaming ao vivo,
sessões persistentes, multi-agente e animações.
"""

import sys
import time
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory

from agents import get_agent, list_agents, agent_names, DEFAULT_AGENT
from session import Session, create_session, list_sessions, Message
from streaming import stream_opencode
from ui import (
    console, print_banner, print_user, print_agent_start,
    print_agent_chunk, print_agent_end, print_system,
    print_error, print_status, print_agents, print_sessions,
    Spinner,
)

# ── State ─────────────────────────────────────────────────────
_msg_count = 0
_start_time = time.monotonic()
_current_agent = DEFAULT_AGENT
_session: Session = create_session(agent=DEFAULT_AGENT)
_history = InMemoryHistory()
_prompt_session = PromptSession(history=_history)


# ── Commands ──────────────────────────────────────────────────
def handle_command(cmd: str) -> bool:
    global _current_agent, _session, _msg_count
    c = cmd.strip().lower()

    if c in ("/quit", "/exit", "/q"):
        _session.save()
        console.print()
        print_system("Sessão salva. Até logo! 👋")
        console.print()
        return False

    if c == "/help":
        console.print()
        console.print(
            "[cmd]/help[/cmd]       — Mostra esta ajuda\n"
            "[cmd]/status[/cmd]     — Status do agente\n"
            "[cmd]/agents[/cmd]     — Lista de agentes\n"
            "[cmd]/agent <nome>[/cmd] — Trocar de agente\n"
            "[cmd]/sessions[/cmd]   — Sessões salvas\n"
            "[cmd]/clear[/cmd]      — Limpa a tela\n"
            "[cmd]/save[/cmd]       — Salva sessão atual\n"
            "[cmd]/quit[/cmd]       — Sair do chat\n"
        )
        console.print()
        return True

    if c == "/status":
        agent = get_agent(_current_agent)
        print_status(
            agent.display_name, agent.icon, _msg_count,
            time.monotonic() - _start_time, _session.id,
        )
        return True

    if c == "/agents":
        print_agents(list_agents(), _current_agent)
        return True

    if c.startswith("/agent"):
        parts = c.split(maxsplit=1)
        if len(parts) < 2:
            print_system("Uso: /agent <nome>")
            print_system(f"Disponíveis: {', '.join(agent_names())}")
            return True
        name = parts[1].strip()
        if name not in agent_names():
            print_error(f"Agente '{name}' não encontrado.")
            print_system(f"Disponíveis: {', '.join(agent_names())}")
            return True
        _current_agent = name
        agent = get_agent(name)
        _session.agent = name
        _session.save()
        print_system(f"{agent.icon} Agente alterado para: {agent.display_name}")
        return True

    if c == "/sessions":
        print_sessions(list_sessions())
        return True

    if c == "/save":
        _session.save()
        print_system(f"Sessão salva: {_session.id}")
        return True

    if c == "/clear":
        console.clear()
        agent = get_agent(_current_agent)
        print_banner(agent.display_name, agent.icon)
        return True

    print_system(f"Comando desconhecido: {cmd}")
    return True


# ── Main loop ─────────────────────────────────────────────────
def main():
    global _msg_count, _session

    agent = get_agent(_current_agent)
    print_banner(agent.display_name, agent.icon)

    while True:
        try:
            user_input = _prompt_session.prompt(
                [("class:user", f"{agent.icon} Você ➜ ")],
                auto_suggest=AutoSuggestFromHistory(),
            )
        except (EOFError, KeyboardInterrupt):
            _session.save()
            console.print()
            print_system("Sessão salva. Até logo! 👋")
            break

        text = user_input.strip()
        if not text:
            continue

        if text.startswith("/"):
            if not handle_command(text):
                break
            continue

        # ── Perceive ──
        _msg_count += 1
        print_user(text)

        # ── Process (streaming) ──
        agent = get_agent(_current_agent)
        print_agent_start(agent.icon, agent.display_name)

        spinner = Spinner("Processando")
        spinner.start()

        t0 = time.monotonic()
        full_response = []
        first_chunk = True

        for chunk in stream_opencode(text, agent.system_prompt):
            if first_chunk:
                spinner.stop()
                first_chunk = False
            print_agent_chunk(chunk)
            full_response.append(chunk)

        spinner.stop()
        elapsed = time.monotonic() - t0

        if first_chunk:
            spinner.stop()
            print_agent_chunk("🤔 Resposta vazia do motor.")

        print_agent_end()
        print_system(f"({elapsed:.1f}s · msg #{_msg_count})")
        console.print()

        # ── Save to session ──
        response_text = "".join(full_response)
        _session.add_message(Message(role="user", content=text, agent=_current_agent))
        _session.add_message(Message(
            role="agent", content=response_text,
            agent=_current_agent, elapsed=elapsed,
        ))
        _session.title = text[:60]
        _session.save()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print()
        print_system("Até logo! 👋")
