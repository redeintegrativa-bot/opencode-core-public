---
name: status
description: Show current orchestrator system status dashboard. Use /status for a quick health overview.
user-invokable: true
allowed-tools: Read, Glob, Bash
metadata:
  keywords: [status, health, metrics, dashboard]
---

# Status

Display a compact system status dashboard for the orchestrator.

## Usage

- `/status` - Show full status dashboard

## Algorithm

1. **Gather data** (in parallel where possible):

   **Agents:** Glob `~/.config/opencode/agents/**/*.md` and count by tier:
   - Core (L0): files directly in agents/
   - Expert (L1): files in agents/experts/
    - Specialist (L2): files in agents/experts/L2/
    - System: files in agents/system/

   **Skills:** Glob `~/.config/opencode/skills/*/SKILL.md` and count

   **Rules:** Glob `~/.config/opencode/rules/*.md` and list names

   **Memory:** Read `~/.config/opencode/projects/*/memory/MEMORY.md` - check if exists, get line count

   **Learnings:** Read `~/.config/opencode/learnings/instincts.json` if exists:
   - Count total instincts
   - Count high-confidence (confidence >= 0.8)

   **MCP Plugins:** Count available MCP tool prefixes (mcp__*) from tool list

   **Sessions:** Glob `~/.config/opencode/sessions/**/*.md` and count

2. **Display dashboard:**

   ```
   ============================================
    OpenCode Core - System Status
   ============================================

    Agents
      Core (L0):       9
      Expert (L1):     22
      Specialist (L2): 15
      System:          9
      Total:           55

    Skills
      Loaded:          {count}
      User-invocable:  {count}

    Rules
      Active sets:     {list}

    Learnings
      Total instincts: {count}
      High confidence: {count}

    MCP Plugins
      Connected:       {count}

    Sessions
      Saved:           {count}

   ============================================
   ```

3. **Health indicators** (append if issues detected):
   - WARN if 0 agents detected
   - WARN if 0 skills detected
   - OK if everything normal

## Notes

- This is a read-only status check; it modifies nothing
- Data is gathered from filesystem, not runtime state
- Agent/skill counts reflect what is on disk, not what is loaded in memory
