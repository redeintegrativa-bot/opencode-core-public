#!/usr/bin/env bash
set -euo pipefail

# auto-update.sh — Auto-sync com o remote
# Verifica se há atualizações no git e faz pull automático
# Chamado pelo hooks/pre-bootstrap.sh no início de cada sessão

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REMOTE="${1:-origin}"
BRANCH="${2:-master}"

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
DIM='\033[2m'
NC='\033[0m'

cd "$REPO_ROOT"

# Só funciona se for um clone git
if ! git rev-parse --git-dir >/dev/null 2>&1; then
    echo -e "${DIM}Não é um repositório git. Pulando auto-update.${NC}"
    exit 0
fi

# Verifica se remote existe
if ! git remote get-url "$REMOTE" >/dev/null 2>&1; then
    echo -e "${DIM}Remote '$REMOTE' não encontrado. Pulando auto-update.${NC}"
    exit 0
fi

echo -e "${BOLD}🔄 Auto-update: verificando atualizações...${NC}"

# Busca atualizações sem fazer merge
git fetch "$REMOTE" "$BRANCH" 2>&1 || {
    echo -e "${YELLOW}⚠️  Não foi possível buscar atualizações (sem conexão?)${NC}"
    return 0
}

# Compara HEAD com o remote
LOCAL=$(git rev-parse HEAD)
REMOTE_HASH=$(git rev-parse "$REMOTE/$BRANCH" 2>/dev/null || echo "")

if [ -z "$REMOTE_HASH" ]; then
    echo -e "${DIM}Nenhuma referência remota para '$BRANCH'.${NC}"
    exit 0
fi

if [ "$LOCAL" = "$REMOTE_HASH" ]; then
    echo -e "${GREEN}✓ Já está atualizado (${LOCAL:0:8})${NC}"
    exit 0
fi

# Verifica se há mudanças locais não commitadas
if ! git diff --quiet HEAD; then
    echo -e "${YELLOW}⚠️  Mudanças locais detectadas.${NC}"
    echo -e "${DIM}Stashando mudanças locais para fazer pull...${NC}"
    git stash push -m "auto-stash before auto-update $(date +%Y%m%d_%H%M%S)"
fi

# Tenta fast-forward
if git merge --ff-only "$REMOTE/$BRANCH" 2>&1; then
    NEW_HASH=$(git rev-parse HEAD)
    echo -e "${GREEN}✓ Atualizado: ${LOCAL:0:8} → ${NEW_HASH:0:8}${NC}"
    
    # Mostra o que mudou
    LOG=$(git log --oneline "${LOCAL}..${NEW_HASH}" 2>/dev/null)
    if [ -n "$LOG" ]; then
        echo -e "${BOLD}Novidades:${NC}"
        echo "$LOG" | while read -r line; do
            echo -e "  ${DIM}•${NC} $line"
        done
    fi
    
    # Stash pop se tiver stashado
    if git stash list | grep -q "auto-stash before auto-update"; then
        git stash pop 2>/dev/null || true
    fi
else
    echo -e "${RED}❌ Fast-forward falhou. Conflitos locais? Resolva manualmente.${NC}"
fi
