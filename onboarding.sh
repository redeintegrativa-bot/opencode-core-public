#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# OpenCode Core — Onboarding Interativo
# =============================================================================
# Faz perguntas para personalizar a experiência do usuário.
# Gera AGENTS.md personalizado + configurações sob medida.
#
# Uso:
#   bash onboarding.sh
# =============================================================================

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$HOME/.config/opencode-core"
mkdir -p "$CONFIG_DIR"

# Cores
BOLD='\033[1m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

ask() {
  local question="$1"
  local default="$2"
  echo ""
  echo -e "${CYAN}${BOLD}?${NC} ${BOLD}$question${NC}"
  read -p "  → " answer
  echo "${answer:-$default}"
}

select_option() {
  local question="$1"
  shift
  local options=("$@")
  echo ""
  echo -e "${CYAN}${BOLD}?${NC} ${BOLD}$question${NC}"
  for i in "${!options[@]}"; do
    echo "  $((i+1)). ${options[$i]}"
  done
  read -p "  → " choice
  echo "${options[$((choice-1))]}"
}

echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║     OpenCode Core — Onboarding           ║"
echo "  ║     Vamos configurar tudo pra você!      ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""
echo -e "  ${YELLOW}São 8 perguntas rápidas. Responda como preferir.${NC}"
echo ""

# ── Perguntas ───────────────────────────────────────────────

NAME=$(ask "Como quer ser chamado?" "Dev")
LANG=$(select_option "Idioma preferido?" "Português" "English" "Español")
STYLE=$(select_option "Estilo de resposta do assistente?" "Direto e seco — vai direto ao ponto" "Equilibrado — explica o necessário" "Didático — explica passo a passo" "Relaxado — informal, como um parceiro")
LEVEL=$(select_option "Seu nível de experiência?" "Iniciante — nunca programou" "Intermediário — já faz projetos" "Avançado — dev profissional" "Expert — arquiteto/sênior")
FOCUS=$(select_option "Foco principal?" "Desenvolvimento Web" "Backend/API" "Automação/CLI" "Segurança" "Dados/ML" "Geral — um pouco de tudo")
TERMINAL=$(select_option "Onde vai usar o OpenCode?" "Termux (Android)" "Linux" "Windows PowerShell" "macOS")
FINANCE=$(select_option "Quer usar o app de controle financeiro (My Money Track)?" "Sim, quero organizar minhas finanças" "Talvez depois" "Não, obrigado")

# ── Gerar configuração ─────────────────────────────────────

# Define personality based on answers
case "$STYLE" in
  *"Direto"*)
    TONE="direct"
    TONE_DESC="Seja direto e objetivo. Vá direto ao ponto sem rodeios. Respostas curtas e precisas."
    ;;
  *"Didático"*)
    TONE="didatic"
    TONE_DESC="Explique passo a passo. Seja didático e ensino como se fosse a primeira vez. Inclua exemplos."
    ;;
  *"Relaxado"*)
    TONE="casual"
    TONE_DESC="Seja informal e relaxado. Use gírias, seja amigável. Trate como um parceiro de código."
    ;;
  *)
    TONE="balanced"
    TONE_DESC="Explique o necessário sem exageros. Equilíbrio entre ser direto e ser completo."
    ;;
esac

# Set language
case "$LANG" in
  "English") LANG_CODE="en"; LANG_RULE="Respond in English." ;;
  "Español") LANG_CODE="es"; LANG_RULE="Responde en español." ;;
  *) LANG_CODE="pt"; LANG_RULE="Responda em português." ;;
esac

# Set verbosity based on level
case "$LEVEL" in
  *"Iniciante"*) VERBOSITY="high" ;;
  *"Intermediário"*) VERBOSITY="medium" ;;
  *"Avançado"*) VERBOSITY="low" ;;
  *) VERBOSITY="low" ;;
esac

# ── Gerar AGENTS.md personalizado ─────────────────────────

cat > "$CONFIG_DIR/AGENTS.md" << AGENTS
# AGENTS.md — Personalizado para $NAME

$LANG_RULE
$TONE_DESC

## Perfil
- **Nome:** $NAME
- **Nível:** $LEVEL
- **Foco:** $FOCUS
- **Terminal:** $TERMINAL
- **Estilo:** $STYLE

## Comandos Rápidos
- \`/help\` — Ajuda
- \`/status\` — Status do sistema
- \`/plan\` — Planejar implementação
- \`/review\` — Revisar código
- \`/fix\` — Corrigir bug
- \`/scaffold\` — Criar projeto do zero
- \`/database\` — Ajuda com banco de dados
- \`/security-scan\` — Auditoria de segurança
- \`/tdd\` — Desenvolvimento orientado a testes

## Regras
- Mantenha o estilo de resposta conforme definido acima
- Use a linguagem definida ($LANG)
- Adapte o nível de detalhe ao perfil do usuário
- Code primeiro, explicação depois (quando aplicável)
AGENTS

# ── Gerar onboarding completo ──────────────────────────────

ONBOARDING_FILE="$CONFIG_DIR/profile.json"
cat > "$ONBOARDING_FILE" << PROFILE
{
  "name": "$NAME",
  "language": "$LANG_CODE",
  "tone": "$TONE",
  "level": "$LEVEL",
  "focus": "$FOCUS",
  "terminal": "$TERMINAL",
  "finance_app": $([ "$FINANCE" = "Sim*" ] || [ "$FINANCE" = "Talvez depois" ] && echo "true" || echo "false"),
  "verbosity": "$VERBOSITY",
  "onboarded_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo 'now')"
}
PROFILE

# ── Resumo final ──────────────────────────────────────────

echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║  Onboarding concluído! 🎉                ║"
echo "  ╠══════════════════════════════════════════╣"
echo "  ║  Nome:      $NAME"
echo "  ║  Idioma:    $LANG"
echo "  ║  Estilo:    $STYLE"
echo "  ║  Nível:     $LEVEL"
echo "  ║  Foco:      $FOCUS"
echo "  ║  Terminal:  $TERMINAL"
echo "  ╚══════════════════════════════════════════╝"
echo ""
echo -e "  ${GREEN}Configuração salva em:${NC}"
echo "    $CONFIG_DIR/AGENTS.md"
echo "    $CONFIG_DIR/profile.json"
echo ""

# ── Next steps ────────────────────────────────────────────
echo -e "  ${BOLD}Próximos passos:${NC}"
echo ""
echo "  1. Rode o setup:  bash setup.sh"
echo "  2. Inicie o chat: cd terminal-chat && python opencode_chat.py"
if [ "$FINANCE" = "Sim*" ] || [ "$FINANCE" = "Talvez depois" ]; then
  echo "  3. Configure o My Money Track: cd my-money-track && npm install && npm run dev"
fi
echo ""
echo -e "  ${YELLOW}💡 Dica: O arquivo AGENTS.md personalizado guia o OpenCode"
echo "     no seu estilo preferido. É só apontar o OpenCode pra ele!"
echo ""
