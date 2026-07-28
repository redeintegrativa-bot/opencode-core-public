#!/usr/bin/env python3
"""Persistent session management for terminal chat."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field, asdict

SESSION_DIR = Path.home() / ".opencode-chat" / "sessions"

@dataclass
class Message:
    role: str  # "user" or "agent"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    agent: str = "default"
    elapsed: float = 0.0

@dataclass
class Session:
    id: str
    title: str
    created: str
    updated: str
    agent: str = "default"
    messages: list[dict] = field(default_factory=list)

    def add_message(self, msg: Message):
        self.messages.append(asdict(msg))
        self.updated = datetime.now().isoformat()

    def save(self):
        SESSION_DIR.mkdir(parents=True, exist_ok=True)
        path = SESSION_DIR / f"{self.id}.json"
        path.write_text(json.dumps(asdict(self), indent=2, ensure_ascii=False))

    @classmethod
    def load(cls, session_id: str) -> Optional["Session"]:
        path = SESSION_DIR / f"{session_id}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text())
        return cls(**data)

def create_session(title: str = "", agent: str = "default") -> Session:
    sid = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if not title:
        title = f"Sessão {sid}"
    return Session(
        id=sid,
        title=title,
        created=datetime.now().isoformat(),
        updated=datetime.now().isoformat(),
        agent=agent,
    )

def list_sessions() -> list[dict]:
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    sessions = []
    for f in sorted(SESSION_DIR.glob("*.json"), reverse=True):
        try:
            data = json.loads(f.read_text())
            sessions.append({
                "id": data["id"],
                "title": data["title"],
                "agent": data.get("agent", "default"),
                "messages": len(data.get("messages", [])),
                "updated": data["updated"],
            })
        except Exception:
            continue
    return sessions

def delete_session(session_id: str) -> bool:
    path = SESSION_DIR / f"{session_id}.json"
    if path.exists():
        path.unlink()
        return True
    return False
