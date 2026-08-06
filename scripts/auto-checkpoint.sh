#!/usr/bin/env bash
set -euo pipefail

# auto-checkpoint.sh — Salva estado automaticamente
# Uso: source scripts/auto-checkpoint.sh [intervalo_segundos]
#   (default: 300 segundos = 5 minutos)
# Modo manual: ./scripts/auto-checkpoint.sh now
# Ver status:  ./scripts/auto-checkpoint.sh status

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONTEXT_DIR="$REPO_ROOT/context"
CHECKLIST="$CONTEXT_DIR/checklist.md"
HANDOFF="$CONTEXT_DIR/session-handoff.md"
CHECKPOINT_DIR="$REPO_ROOT/.checkpoints"
MEMORY_SCRIPT="$REPO_ROOT/memory/memory.py"

BOLD='\033[1m'
GREEN='\033[0;32m'
DIM='\033[2m'
YELLOW='\033[0;33m'
NC='\033[0m'

mkdir -p "$CHECKPOINT_DIR"

save_checkpoint() {
    local timestamp
    timestamp=$(date +%Y%m%d_%H%M%S)
    local checkpoint_file="$CHECKPOINT_DIR/checkpoint_${timestamp}.md"
    
    echo -e "${DIM}💾 Salvando checkpoint ${timestamp}...${NC}"
    
    # Determina branch e últimos commits
    local branch="unknown"
    local last_commit=""
    if git -C "$REPO_ROOT" rev-parse --git-dir >/dev/null 2>&1; then
        branch=$(git -C "$REPO_ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
        last_commit=$(git -C "$REPO_ROOT" log --oneline -3 2>/dev/null || echo "")
    fi
    
    # Monta checkpoint
    cat > "$checkpoint_file" << EOF
# Checkpoint ${timestamp}

**Branch:** ${branch}
**Auto-save:** $(date "+%Y-%m-%d %H:%M:%S")

## Task Snapshot
$(grep '\[.\]' "$CHECKLIST" 2>/dev/null || echo "(no tasks)")

## Últimos Commits
${last_commit}

## Handoff Ativo
$(head -15 "$HANDOFF" 2>/dev/null || echo "(no handoff)")
EOF
    
    # Atualiza handoff com timestamp
    sed -i "s/^> ⚡ Auto-save ativo.*/> ⚡ Auto-save ativo | Último checkpoint: ${timestamp}/" "$HANDOFF" 2>/dev/null || true
    
    # Salva memória se disponível
    if [ -f "$MEMORY_SCRIPT" ]; then
        python3 "$MEMORY_SCRIPT" consolidate 2>/dev/null || true
    fi
    
    echo -e "${GREEN}✓ Checkpoint salvo:${NC} $(basename "$checkpoint_file")"
    
    # Limpa checkpoints antigos (>7 dias)
    find "$CHECKPOINT_DIR" -name 'checkpoint_*.md' -mtime +7 -delete 2>/dev/null || true
    
    # Mantém só os 20 mais recentes
    local count
    count=$(ls -1 "$CHECKPOINT_DIR"/*.md 2>/dev/null | wc -l)
    if [ "$count" -gt 20 ]; then
        ls -t "$CHECKPOINT_DIR"/*.md | tail -n +21 | xargs rm -f 2>/dev/null || true
    fi
}

auto_save_loop() {
    local interval="${1:-300}"
    echo -e "${BOLD}⏰ Auto-checkpoint ativado${NC} (a cada ${interval}s)"
    echo -e "${DIM}PID: $$ | Ctrl+C para parar${NC}"
    echo ""
    
    # Salva imediatamente
    save_checkpoint
    
    local counter=0
    while true; do
        sleep "$interval"
        save_checkpoint
        counter=$((counter + 1))
        # A cada 3 checkpoints, checa se há atualizações no remote
        if [ $((counter % 3)) -eq 0 ] && [ -f "$REPO_ROOT/scripts/auto-update.sh" ]; then
            bash "$REPO_ROOT/scripts/auto-update.sh" 2>&1 || true
        fi
    done
}

# ─── Main ───────────────────────────────────────────────

case "${1:-}" in
    now)
        save_checkpoint
        ;;
    status)
        echo -e "${BOLD}📊 Checkpoints disponíveis:${NC}"
        local count
        count=$(ls -1 "$CHECKPOINT_DIR"/*.md 2>/dev/null | wc -l || echo 0)
        echo -e "  Total: ${count} checkpoints"
        echo -e "  Diretório: ${CHECKPOINT_DIR}"
        if [ "$count" -gt 0 ]; then
            echo ""
            echo -e "${DIM}Últimos:${NC}"
            ls -lt "$CHECKPOINT_DIR"/*.md 2>/dev/null | head -5
        fi
        ;;
    *)
        auto_save_loop "${1:-300}"
        ;;
esac
