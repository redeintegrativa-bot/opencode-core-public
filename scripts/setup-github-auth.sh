#!/usr/bin/env bash
set -euo pipefail

# setup-github-auth.sh — Configura credencial GitHub no ~/.git-credentials
# Uso: GH_TOKEN=<token> ./scripts/setup-github-auth.sh [--check]
# O token NÃO é gravado no repo — apenas no store local de credenciais (perms 600).

CRED_FILE="${HOME}/.git-credentials"
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
DIM='\033[2m'
NC='\033[0m'

if [ -n "${GH_TOKEN:-}" ]; then
    printf '%s\n' "https://x-access-token:${GH_TOKEN}@github.com" > "$CRED_FILE"
    chmod 600 "$CRED_FILE"
    git config --global credential.helper store
    echo -e "${GREEN}✓ Credencial configurada em ${BOLD}$CRED_FILE${NC} (perms 600)"
elif [ -f "$CRED_FILE" ]; then
    echo -e "${YELLOW}⚠  GH_TOKEN vazio — usando credencial já existente em $CRED_FILE${NC}"
else
    echo -e "${RED}✗ GH_TOKEN não definido e nenhuma credencial existente.${NC}" >&2
    echo -e "${YELLOW}Gere um classic token com escopo 'repo' e rode:${NC}"
    echo "  GH_TOKEN=<token> ./scripts/setup-github-auth.sh"
    exit 1
fi

if [ "${1:-}" = "--check" ]; then
    echo -e "${BOLD}Verificando acesso à org redeintegrativa-bot...${NC}"
    for repo in opencode-core opencode-core-public; do
        code=$(curl -s -o /dev/null -w "%{http_code}" \
            -u "x-access-token:$(git credential fill <<< $'protocol=https\nhost=github.com\n' 2>/dev/null | sed -n 's/^password=//p')" \
            "https://github.com/redeintegrativa-bot/${repo}.git/info/refs?service=git-receive-pack")
        if [ "$code" = "200" ]; then
            echo -e "  ${GREEN}✓ ${repo}: push permitido${NC}"
        else
            echo -e "  ${RED}✗ ${repo}: HTTP $code (sem permissão de escrita)${NC}"
        fi
    done
fi

echo -e "${DIM}Dica: nunca commit o token no repo — o hook validate_security.py bloqueia.${NC}"
