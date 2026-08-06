#!/usr/bin/env bash
set -euo pipefail

# memory-search.sh — Busca local em checkpoints, contexto e memórias
# Inspirado no Déjà Vu (CLI de memória pesquisável): indexa os logs de
# sessão passados pra que nada se perca entre sessões.
# Uso: ./scripts/memory-search.sh "query" [--max N]
#   --max N  limita o número de resultados por fonte (default: 5)

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
QUERY="${1:-}"
MAX=5

BOLD='\033[1m'
CYAN='\033[0;36m'
DIM='\033[2m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

# Parsing: QUERY [--max N]
if [[ "$2" == "--max" ]] && [[ -n "${3:-}" ]]; then
    MAX="$3"
fi

if [[ -z "$QUERY" ]]; then
    echo "Uso: $0 \"query\" [--max N]" >&2
    exit 1
fi

search_source() {
    local label="$1" dir="$2" pattern="$3"
    if [[ ! -d "$dir" ]]; then return 0; fi
    local hits
    hits=$(grep -ril --include="*$pattern" "$QUERY" "$dir" 2>/dev/null | head -n "$MAX" || true)
    if [[ -z "$hits" ]]; then return 0; fi
    echo -e "\n${BOLD}${CYAN}── $label ──${NC}"
    local f
    while IFS= read -r f; do
        local rel context_line
        rel="${f#"$REPO_ROOT"/}"
        context_line=$(grep -ri --include="*$pattern" -m1 -n "$QUERY" "$f" 2>/dev/null | head -1 || true)
        local line_num=""
        local snippet=""
        if [[ -n "$context_line" ]]; then
            line_num="${context_line%%:*}"
            snippet="${context_line#*:}"
            snippet="${snippet:0:120}"
        fi
        echo -e "  ${GREEN}•${NC} ${rel}${DIM}${line_num:+:$line_num}${NC}"
        if [[ -n "$snippet" ]]; then
            echo -e "    ${DIM}${snippet//$'\n'/ }${NC}"
        fi
    done <<< "$hits"
}

echo -e "${BOLD}🔎 Buscando \"${QUERY}\"...${NC}"

search_source "Checkpoints" "$REPO_ROOT/.checkpoints" ".md"
search_source "Contexto (versionado)" "$REPO_ROOT/context" ".md"
search_source "Memórias de agents" "$REPO_ROOT/memory/agents" ".json"
search_source "Docs e skills" "$REPO_ROOT/skills" ".md"

echo -e "\n${DIM}Dica: use context/session-handoff.md pra continuar de onde a última sessão parou.${NC}"
