# =============================================================================
# OpenCode Core — Setup Script (Windows PowerShell)
# =============================================================================
# Instala skills, agentes, regras e hooks no ambiente do usuário.
#
# Uso:
#   .\setup.ps1              # Instalação completa
#   .\setup.ps1 -Skills      # Apenas skills
#   .\setup.ps1 -Agents      # Apenas agentes
#   .\setup.ps1 -Rules       # Apenas regras
#   .\setup.ps1 -Workflows   # Apenas workflows
#   .\setup.ps1 -Commands    # Apenas comandos
#   .\setup.ps1 -Plugins     # Apenas plugins
#   .\setup.ps1 -Memory      # Apenas infra de memoria (session.py + template)
#   .\setup.ps1 -SkipUpdateCheck  # Não verifica atualizações no início
#   .\setup.ps1 -Help        # Esta mensagem
# =============================================================================

param(
  [switch]$Skills,
  [switch]$Agents,
  [switch]$Rules,
  [switch]$Hooks,
  [switch]$Workflows,
  [switch]$Commands,
  [switch]$Plugins,
  [switch]$Memory,
  [switch]$CI,
  [switch]$All,
  [switch]$SkipUpdateCheck,
  [switch]$Help
)

$RepoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillsDir = Join-Path $RepoDir "skills"
$AgentsDir = Join-Path $RepoDir "agents"
$RulesDir = Join-Path $RepoDir "rules"
$HooksDir = Join-Path $RepoDir "hooks"
$WorkflowsDir = Join-Path $RepoDir "workflows"
$ServicesDir = Join-Path $RepoDir "services"
$CommandsDir = Join-Path $RepoDir ".opencode\command"
$PluginsDir = Join-Path $RepoDir "plugins"
$MemoryDir = Join-Path $RepoDir "memory"

function Write-Log { Write-Host "✓ $($args[0])" -ForegroundColor Green }
function Write-Warn { Write-Host "! $($args[0])" -ForegroundColor Yellow }
function Write-Err { Write-Host "✗ $($args[0])" -ForegroundColor Red }
function Write-Info { Write-Host "i $($args[0])" -ForegroundColor Cyan }

function Get-ConfigDir {
  if (Get-Command opencode -ErrorAction SilentlyContinue) { return "$env:USERPROFILE\.config\opencode" }
  if (Get-Command claude -ErrorAction SilentlyContinue)   { return "$env:USERPROFILE\.claude" }
  return "$env:USERPROFILE\.config\opencode"
}

function Install-Skills {
  param($Target)
  $skillsTarget = Join-Path $Target "skills"
  New-Item -ItemType Directory -Path $skillsTarget -Force | Out-Null

  $count = 0
  Get-ChildItem -Path $SkillsDir -Directory | ForEach-Object {
    $skillMd = Join-Path $_.FullName "SKILL.md"
    if (Test-Path $skillMd) {
      $dest = Join-Path $skillsTarget $_.Name
      New-Item -ItemType Directory -Path $dest -Force | Out-Null
      Copy-Item -Path "$($_.FullName)\*" -Destination $dest -Recurse -Force -ErrorAction SilentlyContinue
      $count++
    }
  }

  $regSrc = Join-Path $SkillsDir "registry.json"
  if (Test-Path $regSrc) {
    Copy-Item -Path $regSrc -Destination (Join-Path $skillsTarget "registry.json") -Force
  }

  Write-Log "$count skills installed → $skillsTarget"
}

function Install-Agents {
  param($Target)
  $agentsTarget = Join-Path $Target "agents"
  New-Item -ItemType Directory -Path $agentsTarget -Force | Out-Null
  Copy-Item -Path "$AgentsDir\*" -Destination $agentsTarget -Recurse -Force -ErrorAction SilentlyContinue
  Write-Log "Agents installed → $agentsTarget"
}

function Install-Rules {
  param($Target)
  $rulesTarget = Join-Path $Target "rules"
  New-Item -ItemType Directory -Path $rulesTarget -Force | Out-Null
  Copy-Item -Path "$RulesDir\*" -Destination $rulesTarget -Recurse -Force -ErrorAction SilentlyContinue
  Write-Log "Rules installed → $rulesTarget"
}

function Install-Hooks {
  param($Target)
  $hooksTarget = Join-Path $Target "hooks"
  New-Item -ItemType Directory -Path $hooksTarget -Force | Out-Null
  Copy-Item -Path "$HooksDir\*" -Destination $hooksTarget -Recurse -Force -ErrorAction SilentlyContinue
  Write-Log "Hooks installed → $hooksTarget"
}

function Install-Workflows {
  param($Target)
  $wfTarget = Join-Path $Target "workflows"
  New-Item -ItemType Directory -Path $wfTarget -Force | Out-Null
  Copy-Item -Path "$WorkflowsDir\*" -Destination $wfTarget -Recurse -Force -ErrorAction SilentlyContinue
  Write-Log "Workflows installed → $wfTarget"
}

function Install-Services {
  param($Target)
  $svcTarget = Join-Path $Target "services"
  New-Item -ItemType Directory -Path $svcTarget -Force | Out-Null
  Copy-Item -Path "$ServicesDir\*" -Destination $svcTarget -Recurse -Force -ErrorAction SilentlyContinue
  Write-Log "Services installed → $svcTarget"
}

function Install-Commands {
  param($Target)
  if (-not (Test-Path $CommandsDir)) {
    Write-Warn "Sem diretorio .opencode\command no repo; pulando comandos"
    return
  }
  $cmdTarget = Join-Path $Target "command"
  New-Item -ItemType Directory -Path $cmdTarget -Force | Out-Null
  Copy-Item -Path "$CommandsDir\*" -Destination $cmdTarget -Recurse -Force -ErrorAction SilentlyContinue
  Write-Log "Commands installed → $cmdTarget"
}

function Install-Plugins {
  param($Target)
  if (-not (Test-Path $PluginsDir)) {
    Write-Warn "Sem diretorio plugins\ no repo; pulando plugins"
    return
  }
  $pluginsTarget = Join-Path $Target "plugins"
  New-Item -ItemType Directory -Path $pluginsTarget -Force | Out-Null
  Copy-Item -Path "$PluginsDir\*.js"  -Destination $pluginsTarget -Force -ErrorAction SilentlyContinue
  Copy-Item -Path "$PluginsDir\*.tsx" -Destination $pluginsTarget -Force -ErrorAction SilentlyContinue

  # TUI plugin config + deps do config dir
  if (Test-Path (Join-Path $RepoDir "tui.json")) {
    Copy-Item -Path (Join-Path $RepoDir "tui.json") -Destination $Target -Force
    Write-Log "TUI config (tui.json) installed"
  }
  if (Test-Path (Join-Path $RepoDir "package.json")) {
    Copy-Item -Path (Join-Path $RepoDir "package.json") -Destination $Target -Force
    Write-Log "package.json (deps TUI) installed → opencode roda bun install no startup"
  }

  Write-Log "Plugins installed → $pluginsTarget"
}

function Install-Memory {
  param($Target)
  if (-not (Test-Path $MemoryDir)) {
    Write-Warn "Sem diretorio memory\ no repo; pulando infra de memoria"
    return
  }
  $memTarget = Join-Path $Target "memory"
  New-Item -ItemType Directory -Path $memTarget -Force | Out-Null
  Copy-Item -Path (Join-Path $MemoryDir "session.py") -Destination $memTarget -Force -ErrorAction SilentlyContinue
  Copy-Item -Path (Join-Path $MemoryDir "MEMORY.template.md") -Destination $memTarget -Force -ErrorAction SilentlyContinue
  Write-Log "Memory infra installed (session.py + template) → $memTarget"
  Write-Info "Inicie a memoria: python $memTarget\session.py --root <projeto> init"
}

function Install-GitHubActions {
  $actionsDir = Join-Path $RepoDir ".github\workflows"
  New-Item -ItemType Directory -Path $actionsDir -Force | Out-Null

  @'
name: CI

on:
  push:
    branches: [master]
  pull_request:
    branches: [master]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Security validation
        run: |
          if [ -f hooks/validate_security.py ]; then
            python3 hooks/validate_security.py .
          fi
      - name: Check SKILL.md files
        run: |
          for skill in skills/*/SKILL.md; do
            if [ -f "$skill" ]; then echo "✓ $skill"; fi
          done
      - name: Validate registry
        run: |
          if [ -f skills/registry.json ]; then
            python3 -m json.tool skills/registry.json > /dev/null && echo "✓ registry.json OK"
          fi
'@ | Out-File -FilePath (Join-Path $actionsDir "ci.yml") -Encoding utf8

  Write-Log "GitHub Actions workflow installed"
}

function Show-Banner {
  Write-Host ""
  Write-Host "  ╔══════════════════════════════════════════╗" -ForegroundColor Cyan
  Write-Host "  ║      OpenCode Core — Setup               ║" -ForegroundColor Cyan
  Write-Host "  ║      by Rede Integrativa 🚀              ║" -ForegroundColor Cyan
  Write-Host "  ╚══════════════════════════════════════════╝" -ForegroundColor Cyan
  Write-Host ""
}

function Check-Update {
  $checker = Join-Path $RepoDir "scripts\check-update.py"
  if (Test-Path $checker) {
    Write-Info "Verificando atualizacoes..."
    try {
      $out = & python $checker 2>$null
      if (-not $out) { $out = & python3 $checker 2>$null }
    } catch {}
  }
}

function Show-Summary {
  param($Target)
  $skillCount = (Get-ChildItem -Path (Join-Path $Target "skills") -Recurse -Filter "SKILL.md" -ErrorAction SilentlyContinue).Count
  $agentCount = (Get-ChildItem -Path (Join-Path $Target "agents") -Recurse -Filter "*.md" -ErrorAction SilentlyContinue).Count
  $ruleCount = (Get-ChildItem -Path (Join-Path $Target "rules") -Recurse -Filter "*.md" -ErrorAction SilentlyContinue).Count

  Write-Host ""
  Write-Host "  ╔══════════════════════════════════════════╗" -ForegroundColor Green
  Write-Host "  ║  Instalação concluída!                    ║" -ForegroundColor Green
  Write-Host "  ╠══════════════════════════════════════════╣" -ForegroundColor Green
  Write-Host "  ║  Destino:    $Target" -ForegroundColor Green
  Write-Host "  ║  Skills:     $skillCount" -ForegroundColor Green
  Write-Host "  ║  Agentes:    $agentCount" -ForegroundColor Green
  Write-Host "  ║  Regras:     $ruleCount" -ForegroundColor Green
  Write-Host "  ╚══════════════════════════════════════════╝" -ForegroundColor Green
  Write-Host ""
  Write-Info "Pronto! Seu assistente AI está equipado com o OpenCode Core."
  Write-Info "Compartilhe: https://github.com/redeintegrativa-bot/opencode-core-public"
  Write-Host ""
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
Show-Banner
if (-not $SkipUpdateCheck) { Check-Update }

if ($Help) {
  Write-Host "Uso: .\setup.ps1 [-Skills] [-Agents] [-Rules] [-Hooks] [-Workflows] [-Commands] [-Plugins] [-Memory] [-CI] [-All] [-SkipUpdateCheck]"
  exit 0
}

$target = Get-ConfigDir
$mode = if ($All -or (-not $Skills -and -not $Agents -and -not $Rules -and -not $Hooks -and -not $Workflows -and -not $Commands -and -not $Plugins -and -not $Memory -and -not $CI)) { "all" } else { "partial" }

New-Item -ItemType Directory -Path $target -Force | Out-Null

if ($mode -eq "all" -or $Skills)    { Install-Skills $target }
if ($mode -eq "all" -or $Agents)    { Install-Agents $target }
if ($mode -eq "all" -or $Rules)     { Install-Rules $target }
if ($mode -eq "all" -or $Hooks)     { Install-Hooks $target }
if ($mode -eq "all" -or $Workflows) { Install-Workflows $target }
if ($mode -eq "all" -or $Commands)  { Install-Commands $target }
if ($mode -eq "all" -or $Plugins)   { Install-Plugins $target }
if ($mode -eq "all" -or $Memory)    { Install-Memory $target }
if ($mode -eq "all" -or $CI)        { Install-GitHubActions }

# Always install services and CI if all
if ($mode -eq "all") {
  Install-Services $target
  Install-GitHubActions
}

Show-Summary $target
