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
#   .\setup.ps1 -Themes      # Apenas temas
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
  [switch]$Themes,
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
$ThemesDir = Join-Path $RepoDir "themes"
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
  Copy-Item -Path "$PluginsDir\*" -Destination $pluginsTarget -Recurse -Force -ErrorAction Stop
  # OpenCode auto-carrega todo .js na raiz; remova helpers deixados por versoes antigas.
  foreach ($legacyHelper in @("notify.js", "python-helper.js")) {
    $legacyPath = Join-Path $pluginsTarget $legacyHelper
    if (Test-Path -LiteralPath $legacyPath) { Remove-Item -LiteralPath $legacyPath -Force }
  }
  Write-Log "Plugins installed → $pluginsTarget"
}

function Install-Themes {
  param($Target)
  if (-not (Test-Path $ThemesDir)) {
    Write-Warn "Sem diretorio themes\ no repo; pulando temas"
    return
  }
  $themesTarget = Join-Path $Target "themes"
  New-Item -ItemType Directory -Path $themesTarget -Force | Out-Null
  Copy-Item -Path "$ThemesDir\*.json" -Destination $themesTarget -Force -ErrorAction SilentlyContinue
  Write-Log "Themes installed → $themesTarget"
}

function Install-Tui {
  param($Target)
  $tuiSrc = Join-Path $RepoDir "tui.json"
  if (-not (Test-Path $tuiSrc)) {
    Write-Warn "Sem tui.json no repo; pulando config TUI"
    return
  }
  Copy-Item -Path $tuiSrc -Destination (Join-Path $Target "tui.json") -Force -ErrorAction SilentlyContinue
  Write-Log "TUI config installed → $(Join-Path $Target 'tui.json')"
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
  $workflowSource = Join-Path $actionsDir "ci.yml"
  if (-not (Test-Path -LiteralPath $workflowSource)) {
    Write-Warn "Workflow CI nao encontrado; pulando GitHub Actions"
    return
  }
  # O workflow ja e versionado no repo; nao o regenere para evitar divergencia.
  Write-Log "GitHub Actions workflow validado"
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
  Write-Host "Uso: .\setup.ps1 [-Skills] [-Agents] [-Rules] [-Hooks] [-Workflows] [-Commands] [-Plugins] [-Themes] [-Memory] [-CI] [-All] [-SkipUpdateCheck]"
  exit 0
}

$target = Get-ConfigDir
$mode = if ($All -or (-not $Skills -and -not $Agents -and -not $Rules -and -not $Hooks -and -not $Workflows -and -not $Commands -and -not $Plugins -and -not $Themes -and -not $Memory -and -not $CI)) { "all" } else { "partial" }

New-Item -ItemType Directory -Path $target -Force | Out-Null

if ($mode -eq "all" -or $Skills)    { Install-Skills $target }
if ($mode -eq "all" -or $Agents)    { Install-Agents $target }
if ($mode -eq "all" -or $Rules)     { Install-Rules $target }
if ($mode -eq "all" -or $Hooks)     { Install-Hooks $target }
if ($mode -eq "all" -or $Workflows) { Install-Workflows $target }
if ($mode -eq "all" -or $Commands)  { Install-Commands $target }
if ($mode -eq "all" -or $Plugins)   { Install-Plugins $target }
if ($mode -eq "all" -or $Themes)    { Install-Themes $target }
if ($mode -eq "all" -or $Memory)    { Install-Memory $target }
if ($mode -eq "all" -or $CI)        { Install-GitHubActions }

# Sempre instala TUI config (tema + toasts) no modo completo
if ($mode -eq "all") {
  Install-Tui $target
  Install-Services $target
  Install-GitHubActions
}

Show-Summary $target
