#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# OpenCode Core — Setup Script
# =============================================================================
# Instala skills, agentes, regras e hooks no ambiente do usuário.
# Suporta: Claude Code, OpenCode, Codex, Gemini CLI
#
# Uso:
#   ./setup.sh                    # Instalação interativa
#   ./setup.sh --all              # Instala tudo (skills + agents + rules + hooks)
#   ./setup.sh --skills           # Apenas skills
#   ./setup.sh --agents           # Apenas agentes
#   ./setup.sh --rules            # Apenas regras
#   ./setup.sh --hooks            # Apenas hooks
#   ./setup.sh --ci               # Apenas GitHub Actions
#   ./setup.sh --help             # Esta mensagem
# =============================================================================

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$REPO_DIR/skills"
AGENTS_DIR="$REPO_DIR/agents"
RULES_DIR="$REPO_DIR/rules"
HOOKS_DIR="$REPO_DIR/hooks"
WORKFLOWS_DIR="$REPO_DIR/workflows"
SERVICES_DIR="$REPO_DIR/services"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err()  { echo -e "${RED}[✗]${NC} $1"; }
info() { echo -e "${CYAN}[i]${NC} $1"; }

# ---------------------------------------------------------------------------
# Detect AI platform
# ---------------------------------------------------------------------------
detect_platform() {
  if command -v claude &>/dev/null; then
    echo "claude"
  elif command -v opencode &>/dev/null; then
    echo "opencode"
  elif command -v codex &>/dev/null; then
    echo "codex"
  elif command -v gemini &>/dev/null; then
    echo "gemini"
  else
    echo "unknown"
  fi
}

get_config_dir() {
  local platform="$1"
  case "$platform" in
    claude)   echo "$HOME/.claude" ;;
    opencode) echo "$HOME/.config/opencode" ;;
    codex)    echo "$HOME/.codex" ;;
    gemini)   echo "$HOME/.gemini" ;;
    *)        echo "$HOME/.opencode-core" ;;
  esac
}

# ---------------------------------------------------------------------------
# Install functions
# ---------------------------------------------------------------------------
install_skills() {
  local target="$1"
  local skills_target="$target/skills"

  mkdir -p "$skills_target"

  local count=0
  for skill_dir in "$SKILLS_DIR"/*/; do
    local name
    name=$(basename "$skill_dir")
    if [ -f "$skill_dir/SKILL.md" ]; then
      mkdir -p "$skills_target/$name"
      cp -r "$skill_dir"/* "$skills_target/$name/" 2>/dev/null || true
      count=$((count + 1))
    fi
  done

  if [ -f "$SKILLS_DIR/registry.json" ]; then
    cp "$SKILLS_DIR/registry.json" "$skills_target/registry.json"
  fi

  log "$count skills installed → $skills_target"
}

install_agents() {
  local target="$1"
  local agents_target="$target/agents"

  mkdir -p "$agents_target"
  cp -r "$AGENTS_DIR"/* "$agents_target/" 2>/dev/null || true
  log "Agents installed → $agents_target"
}

install_rules() {
  local target="$1"
  local rules_target="$target/rules"

  mkdir -p "$rules_target"
  cp -r "$RULES_DIR"/* "$rules_target/" 2>/dev/null || true
  log "Rules installed → $rules_target"
}

install_hooks() {
  local target="$1"
  local hooks_target="$target/hooks"

  mkdir -p "$hooks_target"
  cp -r "$HOOKS_DIR"/* "$hooks_target/" 2>/dev/null || true

  # Install git hooks if in a git repo
  if git rev-parse --git-dir &>/dev/null; then
    local git_hooks_dir
    git_hooks_dir="$(git rev-parse --git-dir)/hooks"
    if [ -f "$HOOKS_DIR/pre-commit-security.sh" ]; then
      cp "$HOOKS_DIR/pre-commit-security.sh" "$git_hooks_dir/pre-commit"
      chmod +x "$git_hooks_dir/pre-commit"
      log "Git pre-commit hook installed"
    fi
  fi

  log "Hooks installed → $hooks_target"
}

install_workflows() {
  local target="$1"
  local workflows_target="$target/workflows"

  mkdir -p "$workflows_target"
  cp -r "$WORKFLOWS_DIR"/* "$workflows_target/" 2>/dev/null || true
  log "Workflows installed → $workflows_target"
}

install_services() {
  local target="$1"
  local services_target="$target/services"

  mkdir -p "$services_target"
  cp -r "$SERVICES_DIR"/* "$services_target/" 2>/dev/null || true
  log "Services installed → $services_target"
}

install_github_actions() {
  local target="$REPO_DIR"
  mkdir -p "$target/.github/workflows"

  # CI workflow
  cat > "$target/.github/workflows/ci.yml" << 'EOF'
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Security validation
        run: |
          if [ -f hooks/validate_security.py ]; then
            python3 hooks/validate_security.py .
          else
            echo "Security hook not found, skipping"
          fi
      - name: Check SKILL.md files
        run: |
          for skill in skills/*/SKILL.md; do
            if [ -f "$skill" ]; then
              echo "✓ $skill"
            fi
          done
      - name: Validate registry
        run: |
          if [ -f skills/registry.json ]; then
            python3 -m json.tool skills/registry.json > /dev/null && echo "✓ registry.json is valid JSON"
          fi
EOF
  log "GitHub Actions workflow installed"
}

# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------
show_banner() {
  echo ""
  echo "  ╔══════════════════════════════════════════╗"
  echo "  ║      OpenCode Core — Setup               ║"
  echo "  ║      by Rede Integrativa 🚀              ║"
  echo "  ╚══════════════════════════════════════════╝"
  echo ""
}

show_summary() {
  local platform="$1"
  local target="$2"

  echo ""
  echo "  ╔══════════════════════════════════════════╗"
  echo "  ║  Instalação concluída!                    ║"
  echo "  ╠══════════════════════════════════════════╣"
  echo "  ║  Plataforma: $platform"
  echo "  ║  Destino:    $target"
  echo "  ║  Skills:     $(find "$target/skills" -name SKILL.md 2>/dev/null | wc -l)"
  echo "  ║  Agentes:    $(find "$target/agents" -name '*.md' 2>/dev/null | wc -l)"
  echo "  ║  Regras:     $(find "$target/rules" -name '*.md' 2>/dev/null | wc -l)"
  echo "  ╚══════════════════════════════════════════╝"
  echo ""
  info "Pronto! Seu assistente AI está equipado com o OpenCode Core."
  info "Compartilhe: https://github.com/redeintegrativa-bot/opencode-core-public"
  echo ""
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
  show_banner

  local platform
  platform=$(detect_platform)
  local target
  target=$(get_config_dir "$platform")

  local mode="${1:-all}"

  case "$mode" in
    --help|-h)
      echo "Uso: ./setup.sh [--skills|--agents|--rules|--hooks|--workflows|--ci|--all]"
      exit 0
      ;;
    --ci)
      install_github_actions
      exit 0
      ;;
    --skills)     install_skills "$target" ;;
    --agents)     install_agents "$target" ;;
    --rules)      install_rules "$target" ;;
    --hooks)      install_hooks "$target" ;;
    --workflows)  install_workflows "$target" ;;
    --all|*)
      mkdir -p "$target"
      install_skills "$target"
      install_agents "$target"
      install_rules "$target"
      install_hooks "$target"
      install_workflows "$target"
      install_services "$target"
      install_github_actions
      ;;
  esac

  show_summary "$platform" "$target"
}

main "$@"
