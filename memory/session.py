#!/usr/bin/env python3
"""Session memory CLI - persistent cross-session history.

Two-layer persistence:

* Global store (default): ~/.config/opencode/projects/{hash}/memory/
  Survives any repo update, reset or re-clone.
* Local store (--local):  <root>/memory/  (e.g. personal git repo)

Written data:
  * MEMORY.md      - rolling session summary (newest on top)
  * MEMORY.md.bak  - single-file backup taken before every write
  * sessions/      - one log file per session
  * .state.json    - currently active session
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

MEMORY_NAME = "MEMORY.md"
TEMPLATE_NAME = "MEMORY.template.md"
SESSION_DIR = "sessions"
STATE_FILE = ".state.json"
BACKUP_SUFFIX = ".bak"
MAX_SIZE = 50000
COMPRESSION_THRESHOLD = 30000
DEFAULT_KEEP = 60


def project_hash(root: str) -> str:
    """Generate unique hash for a project path (md5, first 12 chars)."""
    normalized = root.lower().replace("\\", "/").rstrip("/")
    return hashlib.md5(normalized.encode()).hexdigest()[:12]


def template_content() -> str:
    """Read the generic MEMORY template shipped next to this script."""
    tpl = Path(__file__).resolve().parent / TEMPLATE_NAME
    if tpl.exists():
        return tpl.read_text(encoding="utf-8")
    return "# MEMORY.md\n\n## Sessões\n\n"


class SessionStore:
    """Manage MEMORY.md, session logs and active session state."""

    def __init__(self, root: str, local: bool = False):
        self.root = Path(root).resolve()
        if local:
            self.base = self.root / "memory"
        else:
            self.base = (
                Path.home() / ".config" / "opencode"
                / "projects" / project_hash(str(self.root)) / "memory"
            )
        self.memory_path = self.base / MEMORY_NAME
        self.sessions_dir = self.base / SESSION_DIR
        self.state_path = self.base / STATE_FILE
        self.backup_path = self.base / (MEMORY_NAME + BACKUP_SUFFIX)

    def ensure_dirs(self):
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def init(self, force: bool = False) -> bool:
        self.ensure_dirs()
        if self.memory_path.exists() and not force:
            print(f"Memory already exists: {self.memory_path}")
            return False
        self.memory_path.write_text(template_content(), encoding="utf-8")
        print(f"Created memory file: {self.memory_path}")
        return True

    def load_state(self) -> dict:
        if not self.state_path.exists():
            return {}
        try:
            return json.loads(self.state_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def save_state(self, state: dict):
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.state_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, self.state_path)

    def active_session(self) -> dict:
        state = self.load_state()
        if state.get("active"):
            return state["active"]
        return None

    def start_session(self) -> dict:
        state = self.load_state()
        if state.get("active"):
            print(f"Session already active: {state['active']['session_id']}")
            return state["active"]
        session = {
            "session_id": datetime.now().strftime("%Y%m%d-%H%M%S"),
            "start": datetime.now().isoformat(timespec="seconds"),
            "project": str(self.root),
            "logs": [],
        }
        state["active"] = session
        self.save_state(state)
        print(f"Session started: {session['session_id']}")
        return session

    def log_entry(self, text: str):
        session = self.active_session()
        if session is None:
            session = self.start_session()
        session["logs"].append({"time": datetime.now().isoformat(timespec="seconds"), "text": text})
        self._persist_active(session)
        print(f"Logged: {text}", flush=True)

    def _persist_active(self, session: dict):
        state = self.load_state()
        state["active"] = session
        self.save_state(state)

    def read_memory(self) -> str:
        return self.memory_path.read_text(encoding="utf-8") if self.memory_path.exists() else ""

    def write_memory(self, content: str):
        self.ensure_dirs()
        self._backup()
        if len(content) > MAX_SIZE:
            content = self._smart_trim(content, DEFAULT_KEEP)
            content += "\n<!-- auto-trimmed: sessões antigas resumidas -->\n"
        tmp = self.memory_path.with_suffix(".tmp")
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, self.memory_path)

    def _smart_trim(self, content: str, keep: int = DEFAULT_KEEP) -> str:
        """Resume sessões antigas mantendo o cabeçalho (perfil/ambiente) e as K recentes completas."""
        blocks = re.split(r"(?m)^## Sessão ", content)
        if len(blocks) <= keep + 1:
            return content
        head = blocks[0]
        old_blocks = blocks[1:-keep] if keep > 0 else blocks[1:]
        recent = blocks[-keep:] if keep > 0 else []
        summary = []
        for block in old_blocks:
            lines = block.splitlines()
            title = lines[0].strip() if lines else "?"
            m = re.search(r"\*\*Resumo:\*\*\s*(.+)", block)
            one_line = m.group(1).strip() if m else ""
            if not one_line:
                one_line = next((l.strip() for l in lines if l.strip() and not l.strip().startswith("#")), "")
            summary.append(f"- {title}: {one_line[:140]}")
        new = head
        if summary:
            new += "\n".join(summary) + "\n"
        for block in recent:
            new += "## Sessão " + block
        return new

    def _backup(self):
        if self.memory_path.exists():
            shutil.copy2(self.memory_path, self.backup_path)

    def end_session(self, summary: str, decisions, files) -> dict:
        session = self.active_session()
        if session is None:
            print("No active session — nothing to end (use 'log' to start one).", flush=True)
            return None
        end = datetime.now()
        session["end"] = end.isoformat(timespec="seconds")
        session["summary"] = summary

        lines = [f"## Sessão {end.strftime('%Y-%m-%d')}\n"]
        if summary:
            lines.append(f"**Resumo:** {summary}")
        if decisions:
            lines.append("\n**Decisões:**")
            for d in decisions:
                lines.append(f"- {d}")
        if files:
            lines.append("\n**Arquivos:**")
            for f in files:
                lines.append(f"- {f}")
        if session.get("logs"):
            lines.append("\n**Log:**")
            for entry in session["logs"]:
                lines.append(f"- {entry['text']}")
        block = "\n".join(lines)

        content = self.read_memory()
        match = re.search(r"(?m)^## Sessões\s*$", content)
        if match:
            before = content[: match.end()]
            after = content[match.end():].lstrip("\n")
            content = before + "\n\n" + block + "\n\n" + after
        else:
            content = content.rstrip() + "\n\n## Sessões\n\n" + block + "\n"

        self.write_memory(content)
        self._save_session_file(session, block)
        state = self.load_state()
        state.pop("active", None)
        self.save_state(state)
        print(f"Session ended: {session['session_id']}", flush=True)
        return session

    def _save_session_file(self, session: dict, block: str):
        self.ensure_dirs()
        stamp = session["session_id"]
        path = self.sessions_dir / f"session-{stamp}.md"
        header = f"# Session {stamp}\n\n- start: {session.get('start')}\n- end: {session.get('end')}\n- project: {session.get('project')}\n\n"
        path.write_text(header + block + "\n", encoding="utf-8")

    def show(self):
        print(f"Store: {self.base}")
        print(f"Memory file: {self.memory_path}")
        session = self.active_session()
        if session:
            print(f"Active session: {session['session_id']} (started {session['start']}, {len(session.get('logs', []))} log(s))")
        else:
            print("Active session: none")
        if self.memory_path.exists():
            print("\n" + self.read_memory())

    def stats(self) -> dict:
        sessions = list(self.sessions_dir.glob("session-*.md")) if self.sessions_dir.exists() else []
        size = self.memory_path.stat().st_size if self.memory_path.exists() else 0
        metas = self.sessions_meta()
        return {
            "store": str(self.base),
            "sessions": len(sessions),
            "memory_bytes": size,
            "active": bool(self.active_session()),
            "last_session": metas[-1] if metas else None,
        }

    def sessions_meta(self) -> list:
        """Return metadata (id, date, summary) for every saved session, oldest first."""
        metas = []
        if not self.sessions_dir.exists():
            return metas
        for f in sorted(self.sessions_dir.glob("session-*.md")):
            text = f.read_text(encoding="utf-8")
            m = re.search(r"(?m)^\*\*Resumo:\*\*\s*(.+)", text)
            summary = m.group(1).strip() if m else ""
            sid = f.stem.replace("session-", "")
            metas.append({"id": sid, "date": sid[:8], "summary": summary[:200]})
        return metas

    def status(self) -> dict:
        active = self.active_session()
        metas = self.sessions_meta()
        return {
            "store": str(self.base),
            "memory_file": str(self.memory_path),
            "sessions_total": len(metas),
            "memory_bytes": self.memory_path.stat().st_size if self.memory_path.exists() else 0,
            "active": bool(active),
            "active_session": active,
            "last_session": metas[-1] if metas else None,
            "sessions": metas,
        }

    def compress(self, keep: int = DEFAULT_KEEP):
        if self.sessions_dir.exists():
            files = sorted(self.sessions_dir.glob("session-*.md"))
            for old in files[:-keep] if keep > 0 else files:
                old.unlink()
        content = self.read_memory()
        trimmed = self._smart_trim(content, keep)
        if trimmed != content:
            self.write_memory(trimmed)
            print(f"Comprimido: sessões antigas viraram resumo; mantidas as {keep} mais recentes completas. Perfil preservado.")
        else:
            print(f"Nada a comprimir (há {keep} ou menos sessões).")

    def backup(self, target: str = None, from_target: bool = False):
        if target is None:
            target = str(self.root / "memory")
        target = Path(target)
        target.mkdir(parents=True, exist_ok=True)
        if from_target:
            src, dst = target, self.base
        else:
            src, dst = self.base, target
        src.mkdir(parents=True, exist_ok=True)
        dst.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src / MEMORY_NAME, dst / MEMORY_NAME)
        for rel in [STATE_FILE, MEMORY_NAME + BACKUP_SUFFIX]:
            s = src / rel
            if s.exists():
                shutil.copy2(s, dst / rel)
        sdir = src / SESSION_DIR
        if sdir.exists():
            shutil.copytree(sdir, dst / SESSION_DIR, dirs_exist_ok=True)
        direction = "target -> store" if from_target else "store -> target"
        print(f"Backed up {direction}: {dst}")


def cmd_init(args):
    return 0 if SessionStore(args.root, args.local).init(args.force) else 1


def cmd_start(args):
    SessionStore(args.root, args.local).start_session()
    return 0


def cmd_log(args):
    SessionStore(args.root, args.local).log_entry(" ".join(args.text))
    return 0


def cmd_end(args):
    store = SessionStore(args.root, args.local)
    store.end_session(args.summary, args.decision, args.file)
    return 0


def cmd_show(args):
    SessionStore(args.root, args.local).show()
    return 0


def cmd_stats(args):
    stats = SessionStore(args.root, args.local).stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    return 0


def cmd_status(args):
    data = SessionStore(args.root, args.local).status()
    if args.short:
        s = data
        print(f"store: {s['store']}", flush=True)
        print(f"sessions_total: {s['sessions_total']}", flush=True)
        print(f"memory_bytes: {s['memory_bytes']}", flush=True)
        print(f"active: {s['active']}", flush=True)
        if s.get("last_session"):
            print(f"last_session: {s['last_session']['id']} — {s['last_session']['summary'][:80]}", flush=True)
        return 0
    print(json.dumps(data, ensure_ascii=False, indent=2), flush=True)
    return 0


def cmd_compress(args):
    SessionStore(args.root, args.local).compress(args.keep)
    return 0


def cmd_backup(args):
    SessionStore(args.root, args.local).backup(args.target, args.from_target)
    return 0


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Session memory CLI - persistent cross-session history")
    parser.add_argument("--root", default=os.getcwd(), help="Project root used for hashing/store location")
    parser.add_argument("--local", action="store_true", help="Use <root>/memory/ instead of the global store")

    sub = parser.add_subparsers(dest="command", required=True)

    init_p = sub.add_parser("init", help="Create MEMORY.md from template")
    init_p.add_argument("--force", action="store_true")
    init_p.set_defaults(func=cmd_init)

    sub.add_parser("start", help="Start a session").set_defaults(func=cmd_start)

    log_p = sub.add_parser("log", help="Append a log entry to the active session")
    log_p.add_argument("text", nargs="+")
    log_p.set_defaults(func=cmd_log)

    end_p = sub.add_parser("end", help="Finalize the session and update MEMORY.md")
    end_p.add_argument("--summary", default="", help="Session summary")
    end_p.add_argument("--decision", action="append", default=[], help="Decision taken (repeatable)")
    end_p.add_argument("--file", action="append", default=[], help="File modified (repeatable)")
    end_p.set_defaults(func=cmd_end)

    sub.add_parser("show", help="Show memory and active session").set_defaults(func=cmd_show)
    sub.add_parser("stats", help="Show store statistics").set_defaults(func=cmd_stats)

    status_p = sub.add_parser("status", help="Show full store status (JSON by default)")
    status_p.add_argument("--short", action="store_true", help="Compact text summary")
    status_p.set_defaults(func=cmd_status)

    comp_p = sub.add_parser("compress", help="Prune old sessions and trim MEMORY.md")
    comp_p.add_argument("--keep", type=int, default=DEFAULT_KEEP)
    comp_p.set_defaults(func=cmd_compress)

    bup_p = sub.add_parser("backup", help="Mirror store <-> target (default: <root>/memory)")
    bup_p.add_argument("--target", default=None, help="Target directory (e.g. personal repo memory/)")
    bup_p.add_argument("--from-target", action="store_true", help="Copy from target into the store")
    bup_p.set_defaults(func=cmd_backup)

    args = parser.parse_args()
    try:
        return args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
