#!/usr/bin/env bash
set -euo pipefail

# bootstrap.sh — Recovery pós-clone + restauração de contexto
# Uso: ./scripts/bootstrap.sh
# Detecta automaticamente se é clone fresco e pergunta se quer restaurar

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONTEXT_DIR="$REPO_ROOT/context"
CHECKLIST="$CONTEXT_DIR/checklist.md"
ROADMAP="$CONTEXT_DIR/roadmap.md"
HANDOFF="$CONTEXT_DIR/session-handoff.md"
MEMORY_DIR="$REPO_ROOT/memory"
MEMORY_FILE="$MEMORY_DIR/agents/opencode-core.json"

BOLD='\033[1m'
DIM='\033[2m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BOLD}╔═══════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║   OpenCode Core — Context Bootstrap      ║${NC}"
echo -e "${BOLD}╚═══════════════════════════════════════════╝${NC}"
echo ""

# Detecta se é clone fresco (sem sessões salvas localmente)
is_fresh_clone() {
    # Se context/ existe com arquivos, pode ser clone ou sessão existente
    if [ -f "$CHECKLIST" ]; then
        # Verifica se há algo além do template inicial
        local task_count
        task_count=$(grep -c '\[.\]' "$CHECKLIST" 2>/dev/null || echo 0)
        [ "$task_count" -le 3 ] && return 0 || return 1
    fi
    return 0
}

restore_from_checkpoint() {
    local checkpoint_dir="${REPO_ROOT}/.checkpoints"
    if [ -d "$checkpoint_dir" ]; then
        local latest
        latest=$(ls -t "$checkpoint_dir"/*.md 2>/dev/null | head -1)
        if [ -n "$latest" ]; then
            echo -e "${CYAN}📦 Último checkpoint encontrado:${NC} $(basename "$latest")"
            echo -e "${DIM}Conteúdo:${NC}"
            head -30 "$latest"
            echo ""
            echo -e "${YELLOW}Quer restaurar este checkpoint?${NC} (s/N)"
            read -r resp
            if [[ "$resp" =~ ^[sSyY] ]]; then
                cp "$latest" "$HANDOFF"
                echo -e "${GREEN}✓ Checkpoint restaurado como handoff ativo${NC}"
                return 0
            fi
        fi
    fi
    echo -e "${DIM}Nenhum checkpoint encontrado.${NC}"
    return 1
}

restore_from_handoff() {
    if [ -f "$HANDOFF" ] && [ -s "$HANDOFF" ]; then
        echo -e "${CYAN}📄 Handoff ativo encontrado:${NC}"
        head -20 "$HANDOFF"
        echo ""
        echo -e "${YELLOW}Quer carregar este handoff?${NC} (s/N)"
        read -r resp
        if [[ "$resp" =~ ^[sSyY] ]]; then
            echo -e "${GREEN}✓ Handoff carregado como contexto ativo${NC}"
            return 0
        fi
    fi
    return 1
}

load_context_files() {
    echo ""
    echo -e "${BOLD}📋 Contexto carregado:${NC}"
    
    if [ -f "$CHECKLIST" ]; then
        local total pending done blocked
        total=$(grep -c '\[.\]' "$CHECKLIST" 2>/dev/null || echo 0)
        pending=$(grep -c '\[ \]' "$CHECKLIST" 2>/dev/null || echo 0)
        done_count=$(grep -c '\[x\]' "$CHECKLIST" 2>/dev/null || echo 0)
        blocked=$(grep -c '\[!\]' "$CHECKLIST" 2>/dev/null || echo 0)
        echo -e "  ${CYAN}📝 Checklist:${NC} $total tarefas ($done_count ✅, $pending ⏳, $blocked 🚫)"
    fi
    
    if [ -f "$ROADMAP" ]; then
        local milestones
        milestones=$(grep -c '### M[0-9]' "$ROADMAP" 2>/dev/null || echo 0)
        echo -e "  ${CYAN}🗺️  Roadmap:${NC} $milestones milestones"
    fi
    
    if [ -f "$MEMORY_FILE" ]; then
        local mem_count
        mem_count=$(python3 -c "import json; d=json.load(open('$MEMORY_FILE')); print(len(d.get('memories',[])))" 2>/dev/null || echo 0)
        echo -e "  ${CYAN}🧠 Memórias:${NC} $mem_count registros carregados"
    fi
    
    echo ""
    echo -e "${GREEN}✓ Contexto pronto. Trabalhando em:${NC}"
    grep -m1 '### M[0-9]' "$ROADMAP" 2>/dev/null | sed 's/### //'
}

# ─── Main ───────────────────────────────────────────────

echo -e "${DIM}Repo: $REPO_ROOT${NC}"
echo ""

if is_fresh_clone; then
    echo -e "${YELLOW}⚠️  Clone fresco detectado ou poucas tarefas encontradas.${NC}"
    echo ""
    echo -e "Opções:"
    echo -e "  ${CYAN}1${NC} — Restaurar do último checkpoint"
    echo -e "  ${CYAN}2${NC} — Carregar handoff salvo"
    echo -e "  ${CYAN}3${NC} — Começar do zero (manter template)"
    echo -e "  ${CYAN}q${NC} — Sair"
    echo ""
    echo -e "${BOLD}Escolha:${NC} "
    read -r choice
    
    case "$choice" in
        1) restore_from_checkpoint || restore_from_handoff || true ;;
        2) restore_from_handoff || true ;;
        3|"") echo -e "${DIM}Começando do zero.${NC}" ;;
        q) echo -e "${DIM}Saindo.${NC}"; exit 0 ;;
    esac
else
    echo -e "${GREEN}✓ Sessão existente detectada.${NC}"
fi

load_context_files

echo ""
echo -e "${DIM}Dica: execute 'source scripts/auto-checkpoint.sh' para ativar auto-save.${NC}"
