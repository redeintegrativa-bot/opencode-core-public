---
name: clone-on-demand
description: Clone Git repositories on-demand when the orchestrator detects a missing project. Use when a task references code in a repository that doesn't exist locally, or when the user asks to work on a repo that needs to be cloned first.
---

# Clone On-Demand

## Purpose

Automatically clone Git repositories when the orchestrator detects they are needed but not available locally. This avoids pre-cloning all repos and only fetches what's actually used.

## When to Use

- User asks to work on a project that isn't cloned yet
- Orchestrator STEP 1 detects PROJECT_PATH doesn't exist
- A task references code in an external repository
- User provides a GitHub URL or `owner/repo` reference

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `repo` | Yes | - | GitHub URL or `owner/repo` format |
| `branch` | No | `main` | Branch to clone |
| `depth` | No | `1` | Shallow clone depth (1 = fastest) |
| `sparse` | No | - | Comma-separated patterns for sparse checkout |
| `target` | No | - | Target directory name (default: repo name) |

## Algorithm

```
1. PARSE repo parameter
   - If URL: extract owner/repo
   - If owner/repo: construct URL as https://github.com/{owner}/{repo}.git

2. CHECK if already cloned
   - Check if target directory exists and has .git
   - If exists: git fetch --all, return existing path
   - If not: proceed to clone

3. CLONE repository
   - git clone --depth {depth} --branch {branch} {url} {target}
   - If sparse: git sparse-checkout init --cone, then set patterns

4. VALIDATE clone
   - Check .git exists
   - Check at least one file exists
   - Return path to cloned directory

5. UPDATE PROJECT_PATH
   - Set PROJECT_PATH to cloned directory
   - Continue orchestrator workflow
```

## Examples

### Basic Clone
```
User: "Analise o projeto opencode-crypto-platform"
Orchestrator: Detecta que opencode-crypto-platform não está clonado
Action: git clone --depth 1 https://github.com/redeintegrativa-bot/opencode-crypto-platform.git
Result: PROJECT_PATH = /home/user/opencode-crypto-platform
```

### Clone with Branch
```
User: "Trabalhe na branch develop do cybersec-workstation"
Action: git clone --depth 1 --branch develop https://github.com/redeintegrativa-bot/cybersec-workstation.git
```

### Sparse Clone (large repos)
```
User: "Preciso apenas dos arquivos de config do dotfiles"
Action: git clone --depth 1 --sparse https://github.com/redeintegrativa-bot/dotfiles.git
        cd dotfiles && git sparse-checkout set .config .claude
```

## Error Handling

| Error | Action |
|-------|--------|
| Network timeout | Retry once, then ask user |
| Auth required | Ask user for credentials or SSH key |
| Repo not found | Report error, suggest checking name |
| Disk full | Report error, suggest cleanup |

## Integration with Orchestrator

This skill is invoked at **STEP 1** of the orchestrator algorithm:

```
STEP 1 (PATH CHECK + CLONE):
  IF files not in working directory:
    1. Check if PROJECT_PATH is set
    2. If not set, check if user provided a repo reference
    3. IF repo reference detected:
         INVOKE clone-on-demand skill
         SET PROJECT_PATH = cloned directory
    4. ELSE:
         Ask user for PROJECT_PATH via AskUserQuestion
  INCLUDE PROJECT_PATH in every subagent prompt
```

## Windows Notes

- Use `git clone` with full URL (not SCP syntax)
- Paths use backslashes: `C:\Users\<username>\repo-name`
- SSH agents may need `eval $(ssh-agent)` before clone
- For large repos, prefer `--depth 1` to save time and space

## Repository Map

Known repositories in `redeintegrativa-bot` organization:

| Repository | Description | Clone When |
|------------|-------------|------------|
| opencode-core | Infrastructure hub | Always (essential) |
| workstation | Workstation configs | Always (essential) |
| opencode-config | Agent configuration | Always (essential) |
| ai-operating-system | Multi-agent AI OS | Always (essential) |
| opencode-crypto-platform | DeFi platform | When DeFi tasks needed |
| cybersec-workstation | Pentest platform | When security tasks needed |
| dotfiles | Personal configs | When config tasks needed |
| community-link-finder | Link finder utility | When utility tasks needed |
| maia-content-engine | Content engine | When content tasks needed |

