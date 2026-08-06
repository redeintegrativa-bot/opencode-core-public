---
name: stop-slop
description: Strip AI writing tells from generated text — em dashes, jargon, throat-clearing, rhetorical setups, binary contrasts, and dramatic fragmentation.
---

# Stop Slop — Clean AI Writing

## When to Activate

- Generating user-facing text (docs, copy, error messages)
- Writing commit messages or PR descriptions
- The output "feels like AI" — you can't pinpoint why but it's off
- The user explicitly asks for natural, direct language

## What to Remove

| Pattern | Example | Fix |
|---------|---------|-----|
| Throat-clearing | "Let me walk through", "It's worth noting that", "I'll start by" | Say it directly |
| Emphasis crutches | "crucially", "importantly", "significantly", "of course" | Remove unless essential |
| Binary contrasts | "Not X. But Y." | Combine into one sentence |
| Em dashes | "The system — which is complex — requires..." | Parentheses or commas |
| Business jargon | "leverage", "holistic", "synergy", "robust" | Plain language |
| Rhetorical setups | "So what does this mean?" | Just state the implication |
| Dramatic frags | "The result? Chaos." | Complete sentence |

## Scoring Rubric

Score 1-10 on each dimension. Target >= 35/50.

1. **Directness** — does it say the thing without preamble?
2. **Concision** — could it lose 20% of words without losing meaning?
3. **Jargon** — any buzzwords that don't carry meaning?
4. **AI tells** — em dashes, contrast patterns, throat-clearing?
5. **Natural flow** — would a human write this in an email?

## How to Fix

1. Read through and flag all AI tells
2. Rewrite each flagged section in plain language
3. Re-read aloud — if it sounds like a presentation, cut again
4. Score against rubric
5. Deliver cleaned version

## Reference

When in doubt, ask: "Would a senior engineer write this in a PR comment?" If not, cut it.
