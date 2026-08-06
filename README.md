# OpenCode Core - Infrastructure Hub

Central repository for agent definitions, skills, rules, and shared services.

## Directory Structure

| Directory | Purpose |
|-----------|---------|
| agents/core/ | L0 core agents (orchestrator, analyzer, coder, reviewer, documenter, system) |
| agents/experts/ | L1 expert agents |
| agents/experts/L2/ | L2 sub-specialist agents |
| agents/config/ | Agent routing and configuration |
| agents/system/ | System infrastructure components |
| skills/ | Skill definitions (Anthropic + custom) |
| rules/ | Context rules by language |
| workflows/ | Standard workflows (bugfix, feature, refactoring) |
| hooks/ | Pre/post task hooks |
| templates/ | Reusable templates |
| providers/ | DeFi/crypto data providers (extracted from AIOS) |
| memory/ | Memory persistence layer |
| services/ | Shared services (scoring, learning) |
| chat/ | Chat and mission matching |
| patterns/ | Content pipeline patterns |

Created: 2026-07-27
