#!/usr/bin/env python3
"""Live streaming from OpenCode engine."""

import json
import re
import subprocess
import sys
from typing import Generator

ENGINE_TIMEOUT = 120

def strip_ansi(s: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", s)

def stream_opencode(prompt: str, agent_prompt: str = "") -> Generator[str, None, None]:
    """
    Stream text events from opencode --format json.
    Yields text chunks as they arrive.
    """
    cmd = ["opencode", "run", "--pure", "--format", "json"]
    if agent_prompt:
        cmd.extend(["--command", agent_prompt])
    cmd.append(prompt)
    
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        
        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                evt = json.loads(line)
            except json.JSONDecodeError:
                continue
            
            if evt.get("type") == "text":
                t = evt.get("part", {}).get("text", "")
                if t:
                    yield t
            
            if evt.get("type") == "step_finish":
                break
        
        proc.wait(timeout=ENGINE_TIMEOUT)
        
    except subprocess.TimeoutExpired:
        proc.kill()
        yield "\n\n⏰ Timeout — motor não respondeu em 2 minutos."
    except FileNotFoundError:
        yield "\n\n❌ OpenCode CLI não encontrado."
    except Exception as e:
        yield f"\n\n❌ Erro: {e}"

def call_opencode(prompt: str, agent_prompt: str = "") -> str:
    """
    Non-streaming: collect all text and return at once.
    """
    return "".join(stream_opencode(prompt, agent_prompt))
