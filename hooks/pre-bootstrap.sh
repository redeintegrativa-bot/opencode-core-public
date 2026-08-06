#!/usr/bin/env bash
set -euo pipefail

# pre-bootstrap.sh — Auto-load de contexto na inicialização
# Chamado automaticamente no início de cada sessão.
# Instalação: coloque no ~/.config/opencode/hooks/ ou chame do AGENTS.md

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BOOTSTRAP="$REPO_ROOT/scripts/bootstrap.sh"
CONTEXT_DIR="$REPO_ROOT/context"
MEMORY_SCRIPT="$REPO_ROOT/memory/memory.py"

BOLD='\033[1m'
GREEN='\033[0;32m'
DIM='\033[2m'
NC='\033[0m'

# ─── Auto-update ───────────────────────────────────────

if [ -f "$REPO_ROOT/scripts/auto-update.sh" ]; then
    bash "$REPO_ROOT/scripts/auto-update.sh" 2>&1 || true
    echo ""
fi

# ─── Auto-load silencioso (modo non-interactive) ───────

echo -e "${BOLD}🧠 OpenCode Core — Loading context...${NC}"

# 1. Carrega checklist
if [ -f "$CONTEXT_DIR/checklist.md" ]; then
    TOTAL=$(grep -c '\[.\]' "$CONTEXT_DIR/checklist.md" 2>/dev/null || echo 0)
    PENDING=$(grep -c '\[ \]' "$CONTEXT_DIR/checklist.md" 2>/dev/null || echo 0)
    DONE=$(grep -c '\[x\]' "$CONTEXT_DIR/checklist.md" 2>/dev/null || echo 0)
    echo -e "  ${GREEN}📋${NC} Checklist: $TOTAL tasks ($DONE done, $PENDING pending)"
fi

# 2. Carrega roadmap
if [ -f "$CONTEXT_DIR/roadmap.md" ]; then
    MILESTONE=$(grep -m1 '### M[0-9]' "$CONTEXT_DIR/roadmap.md" 2>/dev/null | sed 's/### //')
    if [ -n "$MILESTONE" ]; then
        echo -e "  ${GREEN}🗺️${NC} Milestone ativo: $MILESTONE"
    fi
fi

# 3. Carrega handoff se existir
if [ -f "$CONTEXT_DIR/session-handoff.md" ] && [ -s "$CONTEXT_DIR/session-handoff.md" ]; then
    HANDOFF_LINE=$(grep -m1 'Última tarefa' "$CONTEXT_DIR/session-handoff.md" 2>/dev/null || true)
    if [ -n "$HANDOFF_LINE" ]; then
        echo -e "  ${GREEN}🔄${NC} Handoff: $HANDOFF_LINE"
    fi
fi

# 4. Carrega memórias do agente
if [ -f "$MEMORY_SCRIPT" ]; then
    MEM_FILE="$REPO_ROOT/memory/agents/opencode-core.json"
    if [ -f "$MEM_FILE" ]; then
        MEM_COUNT=$(python3 -c "
import json, sys
try:
    d = json.load(open('$MEM_FILE'))
    print(len(d.get('memories', [])))
except:
    print(0)
" 2>/dev/null || echo 0)
        if [ "$MEM_COUNT" -gt 0 ]; then
            echo -e "  ${GREEN}🧠${NC} Memory: $MEM_COUNT records loaded"
        fi
    fi
fi

echo -e "${BOLD}✅ Context loaded.${NC}"
