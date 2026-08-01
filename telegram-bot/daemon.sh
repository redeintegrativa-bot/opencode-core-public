#!/bin/bash
# ──────────────────────────────────────────────────────────────
# OpenCode Agent Daemon — start / stop / status / logs
# ──────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="/tmp/opencode-agent.pid"
LOG_FILE="${SCRIPT_DIR}/logs/agent.log"
AGENT_SCRIPT="${SCRIPT_DIR}/opencode_agent.py"

# Usar o Python do venv se existir (senão, o do sistema)
if [ -x "${SCRIPT_DIR}/venv/bin/python" ]; then
    PYTHON_BIN="${SCRIPT_DIR}/venv/bin/python"
else
    PYTHON_BIN="python3"
fi

mkdir -p "${SCRIPT_DIR}/logs"

usage() {
    echo "Usage: $0 {start|stop|status|logs}"
    exit 1
}

is_running() {
    if [ -f "$PID_FILE" ]; then
        local pid
        pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            return 0
        fi
    fi
    return 1
}

cmd_start() {
    if is_running; then
        echo "Agent is already running (PID $(cat "$PID_FILE"))."
        exit 0
    fi

    echo "Starting OpenCode Agent..."
    nohup "$PYTHON_BIN" "$AGENT_SCRIPT" >> "$LOG_FILE" 2>&1 &
    local pid=$!
    echo "$pid" > "$PID_FILE"
    sleep 1

    if kill -0 "$pid" 2>/dev/null; then
        echo "Agent started successfully (PID $pid)."
    else
        echo "ERROR: Agent failed to start. Check logs: $LOG_FILE"
        rm -f "$PID_FILE"
        exit 1
    fi
}

cmd_stop() {
    if ! is_running; then
        echo "Agent is not running."
        rm -f "$PID_FILE" 2>/dev/null
        exit 0
    fi

    local pid
    pid=$(cat "$PID_FILE")
    echo "Stopping Agent (PID $pid)..."
    kill "$pid" 2>/dev/null || true

    for i in $(seq 1 10); do
        if ! kill -0 "$pid" 2>/dev/null; then
            break
        fi
        sleep 1
    done

    if kill -0 "$pid" 2>/dev/null; then
        echo "Force killing..."
        kill -9 "$pid" 2>/dev/null || true
    fi

    rm -f "$PID_FILE"
    echo "Agent stopped."
}

cmd_status() {
    if is_running; then
        local pid
        pid=$(cat "$PID_FILE")
        echo "Agent is RUNNING (PID $pid)."
    else
        echo "Agent is STOPPED."
    fi
}

cmd_logs() {
    if [ ! -f "$LOG_FILE" ]; then
        echo "No log file found at $LOG_FILE"
        exit 0
    fi
    echo "Tailing logs (Ctrl+C to stop)..."
    tail -f "$LOG_FILE"
}

case "${1:-}" in
    start)  cmd_start  ;;
    stop)   cmd_stop   ;;
    status) cmd_status ;;
    logs)   cmd_logs   ;;
    *)      usage      ;;
esac
