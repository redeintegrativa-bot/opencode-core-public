# Orchestration Workflow — Multi-Agent Task Execution

## When to Use

- Task requires 3+ distinct steps across different domains
- Parallel execution is possible and beneficial
- Task benefits from Plan → Review → Build separation
- High-risk changes that need architectural review first

## Workflow Stages

### Stage 1: Intake & Plan (Plan Mode)

1. User provides request
2. Agent analyzes scope, identifies sub-tasks, risks, dependencies
3. Produces brief plan with task breakdown
4. User approves plan before any code is written

### Stage 2: Decomposition

Break into parallel-able units:

- **Independent**: Can run in any order, no shared state
- **Sequential**: B depends on A's output
- **Review gates**: Output of one unit needs validation before next

### Stage 3: Execution

- Run independent sub-tasks in parallel via sub-agents
- Each sub-agent gets: clear goal, context, constraints, exit criteria
- Use `handoff` skill to transfer context between stages

### Stage 4: Integration & Review

- Merge outputs from parallel tracks
- Run verification-loop on integrated result
- Security scan before completion

### Stage 5: Completion

- Present summary of what was done
- Flag any deviations from plan
- Create handoff doc if continuing later

## Principles

- **Plan first, build second** — Tab to Plan mode before any edit
- **One shot per sub-agent** — clear goal, clear done criteria
- **Verify early** — don't accumulate unverified output
- **Handoff explicitly** — compress context between stages
