---
name: grill-me
description: Interview the user relentlessly about a plan until shared understanding is reached, before any code is written. Use when the request is vague, complex, or high-risk.
---

# Grill Me — Planning Interview

## When to Activate

- The user's request is vague or underspecified
- The task has high business or security risk
- Multiple implementation approaches exist
- The problem crosses system boundaries (auth, billing, data)
- The user says "just make it work" without spec

## Core Principle

Write code is the last step, not the first. Every hour spent clarifying intent saves three hours of rework. The agent's job is to **pull out the spec** that the user didn't write down.

## Interview Protocol

### Round 1: Scope
- What exactly should this achieve? (one sentence)
- Who is the end user?
- What systems will this touch?
- What is NOT in scope?

### Round 2: Constraints
- Any performance requirements?
- Security/auth considerations?
- Compliance or regulatory needs?
- Browser/device targets?
- Existing patterns to follow?

### Round 3: Approach
- I see 2-3 ways to do this:
  - Option A: <quick summary>
  - Option B: <quick summary>
  - Option C: <quick summary>
- Which direction feels right?
- Any approach you want me to avoid?

### Round 4: Risks
- What could go wrong?
- What's the rollback plan?
- Can this be done incrementally?

## Output

After all rounds, produce a brief plan summary and ask: "Ready for me to start, or any changes?"

Only begin implementation after explicit approval.
