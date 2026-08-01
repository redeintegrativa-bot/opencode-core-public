#!/usr/bin/env python3
"""
OpenCode Agent — Autonomous AI agent bridging Telegram to the OpenCode engine.

Each message is a natural-language instruction. The agent perceives the
user's intent, processes it through the same LLM the terminal uses
(opencode/big-pickle via --format json), and responds conversationally.
"""

import asyncio
import json
import logging
import os
import random
import re
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "agent.log"
ENV_FILE = BASE_DIR / ".env"
PID_FILE = Path("/tmp/opencode-agent.pid")

load_dotenv(ENV_FILE)

TOKEN: str = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "",
)
AUTHORIZED_CHAT_ID: Optional[int] = (
    int(os.getenv("AUTHORIZED_CHAT_ID", ""))
    if os.getenv("AUTHORIZED_CHAT_ID", "").strip()
    else None
)

MAX_MSG = 4096
ENGINE_TIMEOUT = 300
TYPING_INTERVAL = 4

ACK_PHRASES = [
    "Deixa comigo! Tô analisando isso aqui...",
    "Hum, boa pergunta! Deixa eu pensar...",
    "Já vou te responder, um segundo...",
    "Certo, processando sua solicitação...",
    "Beleza, tô trabalhando nisso agora...",
    "Interessante! Deixa eu ver isso pra você...",
    "Ok, já já te respondo!",
    "Tô consultando o motor aqui, aguenta aí...",
]

ERROR_PHRASES = [
    "Poxa, tive um probleminha aqui. Pode tentar de novo?",
    "Opa, algo deu errado do meu lado. Tenta mais uma vez?",
    "Eita, deu um nó aqui. Me desculpa! Tenta de novo?",
]

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("agent")

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

_boot: float = time.monotonic()
_last_interaction: Optional[datetime] = None
_typing_task: Optional[asyncio.Task] = None
_sessions: dict[int, str] = {}
_message_count: int = 0

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------


def _load_auth() -> Optional[int]:
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            if line.startswith("AUTHORIZED_CHAT_ID="):
                raw = line.split("=", 1)[1].strip()
                if raw:
                    return int(raw)
    return None


def _save_auth(cid: int) -> None:
    global AUTHORIZED_CHAT_ID
    AUTHORIZED_CHAT_ID = cid
    lines = ENV_FILE.read_text().splitlines() if ENV_FILE.exists() else []
    new, found = [], False
    for l in lines:
        if l.startswith("AUTHORIZED_CHAT_ID="):
            new.append(f"AUTHORIZED_CHAT_ID={cid}")
            found = True
        else:
            new.append(l)
    if not found:
        new.append(f"AUTHORIZED_CHAT_ID={cid}")
    ENV_FILE.write_text("\n".join(new) + "\n")
    log.info("chat_id autorizado: %s", cid)


def _auth(cid: int) -> bool:
    global AUTHORIZED_CHAT_ID
    if AUTHORIZED_CHAT_ID is None:
        AUTHORIZED_CHAT_ID = _load_auth()
    if AUTHORIZED_CHAT_ID is None:
        return True
    return cid == AUTHORIZED_CHAT_ID


# ---------------------------------------------------------------------------
# Typing
# ---------------------------------------------------------------------------


async def _typing_on(chat) -> None:
    global _typing_task

    async def _loop():
        try:
            while True:
                await chat.send_action("typing")
                await asyncio.sleep(TYPING_INTERVAL)
        except asyncio.CancelledError:
            pass

    _typing_task = asyncio.create_task(_loop())


def _typing_off() -> None:
    global _typing_task
    if _typing_task and not _typing_task.done():
        _typing_task.cancel()
        _typing_task = None


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------


def _split_pos(text: str, limit: int) -> int:
    if len(text) <= limit:
        return len(text)
    for pat in ["\n\n", "```", ".\n", "!\n", "?\n", ". ", "! ", "? ", "\n", " "]:
        pos = text.rfind(pat, 0, limit)
        if pos > limit * 0.25:
            return pos + len(pat)
    return limit


def _chunk(text: str) -> list[str]:
    if len(text) <= MAX_MSG:
        return [text]
    out, rem = [], text
    while rem:
        if len(rem) <= MAX_MSG:
            out.append(rem)
            break
        sp = _split_pos(rem, MAX_MSG)
        c = rem[:sp].rstrip()
        if c:
            out.append(c)
        rem = rem[sp:].lstrip("\n")
    return out


async def _reply(update: Update, text: str, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    for part in _chunk(text):
        for att in range(1, 4):
            try:
                await ctx.bot.send_message(
                    chat_id=update.effective_chat.id, text=part, parse_mode=None
                )
                break
            except Exception as e:
                log.warning("send attempt %d failed: %s", att, e)
                if att < 3:
                    await asyncio.sleep(att)


# ---------------------------------------------------------------------------
# OpenCode engine
# ---------------------------------------------------------------------------


async def _think(prompt: str) -> str:
    """Perceive → Process: send prompt to opencode, return the text response."""
    cmd = ["opencode", "run", "--pure", "--format", "json", prompt]
    log.info("think: %s", prompt[:100])

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            start_new_session=True,
        )
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=ENGINE_TIMEOUT
            )
        except asyncio.TimeoutError:
            log.error("engine timeout after %ss — killing", ENGINE_TIMEOUT)
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
            try:
                await proc.communicate()
            except Exception:
                pass
            return "⏰ A resposta demorou demais. Tenta de novo com algo mais simples?"
    except FileNotFoundError:
        return "❌ OpenCode CLI não encontrado."
    except Exception as e:
        return f"❌ Erro: {e}"

    raw = stdout.decode("utf-8", errors="replace").strip()
    if not raw:
        err = stderr.decode("utf-8", errors="replace").strip()
        if err:
            log.error("stderr: %s", err[:300])
        return "🤔 O motor não retornou nada. Tenta reformular?"

    texts = []
    for line in raw.splitlines():
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
                texts.append(t)

    if texts:
        return "\n".join(texts)

    clean = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", raw).strip()
    return clean if clean else "🤔 Resposta vazia do motor."


def _polish(raw: str) -> str:
    """Format response for natural conversation."""
    if not raw:
        return "Resposta vazia. Tenta de novo?"
    if raw.startswith(("⏰", "❌", "🤔")):
        return raw
    clean = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", raw).strip()
    return clean if clean else "Resposta vazia. Tenta de novo?"


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    cid = update.effective_chat.id
    if not _auth(cid):
        if AUTHORIZED_CHAT_ID is None:
            _save_auth(cid)
        else:
            await update.message.reply_text("Acesso negado.")
            return
    await update.message.reply_text(
        "Olá! Eu sou o **Agente OpenCode** — seu assistente de IA autônomo! 🚀\n\n"
        "Cada mensagem que você envia é interpretada como uma instrução "
        "e processada pelo mesmo motor de IA que roda no terminal.\n\n"
        "Exemplos:\n"
        "  • Crie um endpoint REST pra usuários\n"
        "  • Analise esse código e sugira melhorias\n"
        "  • Rode os testes do projeto\n\n"
        "Comandos:\n"
        "  /start — Esta mensagem\n"
        "  /status — Status do agente\n"
        "  /help — Lista de comandos\n\n"
        "É só digitar e mandar! Tô aqui pra ajudar 😄"
    )


async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    cid = update.effective_chat.id
    if not _auth(cid):
        await update.message.reply_text("Acesso negado.")
        return
    up = time.monotonic() - _boot
    h, r = divmod(int(up), 3600)
    m, s = divmod(r, 60)
    sid = _sessions.get(cid, "nenhuma")
    await update.message.reply_text(
        f"📊 Status do Agente\n\n"
        f"⏱ Uptime: {h}h {m}m {s}s\n"
        f"💬 Mensagens processadas: {_message_count}\n"
        f"🔒 Chat autorizado: {AUTHORIZED_CHAT_ID or 'A definir'}\n"
        f"🧠 Sessão: {sid}\n"
        f"📝 Log: {LOG_FILE}"
    )


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    cid = update.effective_chat.id
    if not _auth(cid):
        await update.message.reply_text("Acesso negado.")
        return
    await update.message.reply_text(
        "📖 Comandos Disponíveis\n\n"
        "/start — Mensagem de boas-vindas\n"
        "/status — Status do agente\n"
        "/help — Esta mensagem\n\n"
        "💬 Mensagens de texto\n"
        "Qualquer mensagem será interpretada como uma instrução "
        "e processada pelo motor OpenCode. A resposta vem em "
        "linguagem natural, com código e formatação quando necessário.\n\n"
        "🔒 Segurança: apenas o primeiro chat_id autorizado."
    )


# ---------------------------------------------------------------------------
# Agent handler — Percepção → Processamento → Resposta
# ---------------------------------------------------------------------------


async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Cycle of an autonomous agent:
      1. Perceive  — capture the user's natural-language instruction
      2. Process   — activate typing indicator, forward to OpenCode engine
      3. Respond   — format and deliver the result conversationally
    """
    cid = update.effective_chat.id
    if not _auth(cid):
        await update.message.reply_text("Acesso negado.")
        return

    global _last_interaction, _message_count
    _last_interaction = datetime.now(timezone.utc)

    user_text = update.message.text
    if not user_text or not user_text.strip():
        return

    instruction = user_text.strip()
    _message_count += 1
    log.info("[perceive] chat=%s msg#%d: %s", cid, _message_count, instruction[:120])

    # ── Process ──────────────────────────────────────────────
    _typing_on(update.effective_chat)
    await update.message.reply_text(random.choice(ACK_PHRASES))

    try:
        raw_response = await _think(instruction)
        response = _polish(raw_response)
        log.info("[respond] chat=%s len=%d", cid, len(response))
        await _reply(update, response, ctx)
    except Exception as e:
        log.error("[error] chat=%s: %s", cid, e, exc_info=True)
        await update.message.reply_text(random.choice(ERROR_PHRASES))
    finally:
        _typing_off()


# ---------------------------------------------------------------------------
# Error handler
# ---------------------------------------------------------------------------


async def on_error(update: Optional[Update], ctx: ContextTypes.DEFAULT_TYPE) -> None:
    log.error("unhandled: %s", ctx.error, exc_info=ctx.error)
    _typing_off()
    if update and update.effective_chat:
        try:
            await ctx.bot.send_message(
                chat_id=update.effective_chat.id,
                text="⚠️ Erro interno do agente. Tenta de novo.",
            )
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    if not TOKEN:
        log.critical("No token. Exiting.")
        sys.exit(1)

    log.info("Agent starting (conversational JSON mode)...")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(on_error)

    PID_FILE.write_text(str(os.getpid()))
    log.info("PID %s", os.getpid())

    def shutdown(signum, _):
        log.info("Signal %s, shutting down.", signum)
        _typing_off()
        if PID_FILE.exists():
            PID_FILE.unlink()
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    try:
        app.run_polling(drop_pending_updates=True)
    finally:
        _typing_off()
        if PID_FILE.exists():
            PID_FILE.unlink()


if __name__ == "__main__":
    main()
