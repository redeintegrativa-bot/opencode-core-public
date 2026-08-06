---
name: handoff
description: Compress current session into a markdown handoff document so work can continue in a fresh session or be transferred to a different agent or human teammate.
---

# Handoff — Session Compression & Transfer

## When to Activate

- Session is getting long and context is degrading
- You need to switch to a different agent or model
- A human teammate needs to take over the task
- You want to save a checkpoint before a destructive operation
- You're context-switching between projects

## Core Principle

A good handoff preserves **intent, decisions, and next actions** without dumping raw conversation history. The receiving agent should be able to continue immediately without asking "what was done before?"

## Handoff Template

Generate a markdown document with these sections:

```
# Handoff: <project/task name>
## State
- Current branch/commit:
- Files modified:
- Tests passing/failing:

## What Was Done
- Bullet-list of completed work
- Key decisions made and why
- Dead ends explored (saves re-exploration)

## Current Blockers
- Unresolved issues with context
- Assumptions that need validation

## Next Steps
1. Immediate next action
2. Follow-up items
3. Open questions

## Context
- Relevant files or symbols
- Error messages in play
- External references (docs, issues, PRs)
```

## Output

Write the handoff to a file: `handoff-<project>-<timestamp>.md`

Then reset with: `/compact` or start a fresh session referencing the handoff file.
