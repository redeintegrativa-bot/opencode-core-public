---
name: simplify
description: Review and simplify code for clarity and maintainability
user-invokable: true
allowed-tools: [Read, Edit, Grep, Glob, Task]
---

# Skill: Simplify

Review code for unnecessary complexity and suggest simplifications.

## Workflow

1. **Read** target code
2. **Identify** complexity hotspots:
   - Nested conditionals (flatten with early returns)
   - Duplicated logic (extract to function)
   - Overly verbose patterns (simplify expressions)
   - Dead code (remove unused)
3. **Apply** simplifications
4. **Verify** functionality unchanged

## Simplification Patterns

| Pattern | Before | After |
|---------|--------|-------|
| Early return | `if (a) { if (b) { ... } }` | `if (!a) return; if (!b) return; ...` |
| Guard clause | `if (valid) { main logic }` | `if (!valid) return; main logic` |
| Ternary | `if (x) y = a; else y = b;` | `y = x ? a : b;` |
| Extract | Repeated 3+ lines | `function extracted()` |
| Remove | Commented code, unused vars | Delete |

## Rules

- Never change behavior, only structure
- Preserve all tests passing
- Keep function signatures unchanged
- Prefer readability over cleverness

