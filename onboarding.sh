#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$HOME/.config/opencode-core"
mkdir -p "$CONFIG_DIR"

BOLD='\033[1m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

select_option() {
  local question="$1"
  shift
  local options=("$@")
  echo ""
  echo -e "${CYAN}${BOLD}?${NC} ${BOLD}$question${NC}"
  for i in "${!options[@]}"; do
    echo "  $((i+1)). ${options[$i]}"
  done
  read -p "  > " choice
  echo "${options[$((choice-1))]}"
}

echo ""
echo "  +----------------------------------+"
echo "  | OpenCode Core - Onboarding        |"
echo "  | So 3 perguntas pra comecar!       |"
echo "  +----------------------------------+"
echo ""
echo -e "  ${YELLOW}Isso leva 10 segundos. Depois é só usar.${NC}"
echo ""

STYLE=$(select_option "Estilo de resposta?" "Direto — vai direto ao ponto, sem rodeios" "Equilibrado — explica o necessário" "Didático — explica passo a passo" "Relaxado — informal, como um parceiro")
FOCUS=$(select_option "Foco principal?" "Web" "Backend/API" "Automação/CLI" "Dados/ML" "Geral — um pouco de tudo")
LEVEL=$(select_option "Seu nível de experiência?" "Iniciante — nunca programou" "Intermediário — já faz projetos" "Avançado — dev profissional" "Expert — arquiteto/sênior")

case "$STYLE" in
  *"Direto"*) TONE="direct" ;;
  *"Didático"*) TONE="didatic" ;;
  *"Relaxado"*) TONE="casual" ;;
  *) TONE="balanced" ;;
esac

case "$FOCUS" in
  *"Web"*) FOCUS_CODE="web" ;;
  *"Backend"*) FOCUS_CODE="backend" ;;
  *"Automação"*) FOCUS_CODE="cli" ;;
  *"Dados"*) FOCUS_CODE="data" ;;
  *) FOCUS_CODE="general" ;;
esac

case "$LEVEL" in
  *"Iniciante"*) VERBOSITY="high" ;;
  *"Intermediário"*) VERBOSITY="medium" ;;
  *) VERBOSITY="low" ;;
esac

cat > "$CONFIG_DIR/AGENTS.md" << AGENTS
# ONBOARDING
TONE=$TONE FOCUS=$FOCUS_CODE VERBOSITY=$VERBOSITY
AGENTS

echo ""
echo "  +------------------------------------------+"
echo "  | Onboarding concluido!                     |"
echo "  +------------------------------------------+"
echo "  | Estilo:    [$TONE]"
echo "  | Foco:      $FOCUS_CODE"
echo "  | Detalhe:   $VERBOSITY"
echo "  +------------------------------------------+"
echo ""
echo -e "  ${GREEN}Salvo em: $CONFIG_DIR/AGENTS.md${NC}"
echo ""
echo -e "  ${BOLD}Próximo passo:${NC}  Rode  bash setup.sh"
echo ""
echo -e "  ${YELLOW}Dica: No chat, use /config pra mudar o estilo quando quiser.${NC}"
echo ""
