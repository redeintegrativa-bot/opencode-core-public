#!/usr/bin/env python3
"""PreAgentSpawn validation hook.

Validates agent availability before spawning a subagent.
Checks: agent definition file exists, circuit breaker status.
Returns: PASS / FAIL / ESCALATE
"""

import json
import os
import sys
from pathlib import Path

HOOKS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = HOOKS_DIR.parent
AGENTS_DIR = PROJECT_ROOT / "agents"
REGISTRY_PATH = PROJECT_ROOT / "agent-registry.json"
CIRCUIT_BREAKER_PATH = HOOKS_DIR / ".circuit_breakers.json"

REQUIRED_RESULT_FIELDS = ["status", "agent", "timestamp"]
PASS = "PASS"
FAIL = "FAIL"
ESCALATE = "ESCALATE"


def _now_iso():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def load_registry():
    if REGISTRY_PATH.exists():
        with open(REGISTRY_PATH) as f:
            return json.load(f)
    # Fall back to skills registry which has agent routing info
    skills_registry_path = PROJECT_ROOT / "skills" / "registry.json"
    if skills_registry_path.exists():
        with open(skills_registry_path) as f:
            return json.load(f)
    return {}


def load_circuit_breakers():
    if not CIRCUIT_BREAKER_PATH.exists():
        return {}
    with open(CIRCUIT_BREAKER_PATH) as f:
        return json.load(f)


def find_agent_file(agent_name):
    """Search for agent definition .md in agents/ tree.

    Handles both flat naming (coder.md) and display-name variants
    (e.g. 'Integration Expert' -> integration_expert.md or similar).
    """
    normalised = agent_name.lower().replace(" ", "_").replace("-", "_")

    for root, dirs, files in os.walk(AGENTS_DIR):
        for fname in files:
            if not fname.endswith(".md") or fname.startswith("INDEX") or fname.startswith("CLAUDE"):
                continue
            stem = fname[:-3].lower().replace("-", "_")
            if stem == normalised or stem == agent_name.lower().replace("-", "_"):
                return Path(root) / fname

    # Second pass: partial match (e.g. "coder" matches "coder.md" anywhere)
    for root, dirs, files in os.walk(AGENTS_DIR):
        for fname in files:
            if not fname.endswith(".md") or fname.startswith("INDEX") or fname.startswith("CLAUDE"):
                continue
            if normalised in fname[:-3].lower():
                return Path(root) / fname

    return None


def validate_agent(agent_name):
    result = {
        "status": PASS,
        "agent": agent_name,
        "timestamp": _now_iso(),
        "checks": [],
        "errors": [],
        "warnings": [],
    }

    # Check 1: Agent definition file exists in agents/ tree
    agent_file = find_agent_file(agent_name)
    if agent_file is None:
        result["checks"].append({"name": "definition_file", "passed": False})
        result["errors"].append(f"VH001: Agent not found: {agent_name}")
        result["status"] = FAIL
        result["action"] = "FALLBACK"
        result["fallback"] = "coder"
        return result
    result["checks"].append({"name": "definition_file", "passed": True})
    result["definition_file"] = str(agent_file.relative_to(PROJECT_ROOT))

    # Check 2: Agent in registry (informational)
    registry = load_registry()
    agents = registry.get("agents", registry.get("skills", {}))
    if agent_name not in agents:
        result["warnings"].append(f"Agent not in registry: {agent_name} (continuing with definition file)")
    result["checks"].append({"name": "registry_lookup", "passed": True})

    # Check 3: Circuit breaker
    breakers = load_circuit_breakers()
    agent_info = breakers.get(agent_name, {})
    if agent_info.get("open", False):
        result["checks"].append({"name": "circuit_breaker", "passed": False})
        result["warnings"].append(f"VH003: Circuit breaker open for: {agent_name}")
        result["status"] = ESCALATE
        result["action"] = "FALLBACK"
        result["fallback"] = agent_info.get("fallback_agent", "coder")
    else:
        result["checks"].append({"name": "circuit_breaker", "passed": True})

    if result["status"] == PASS:
        result["action"] = "PROCEED"

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_agent.py <agent_name>", file=sys.stderr)
        sys.exit(1)

    agent_name = sys.argv[1]
    result = validate_agent(agent_name)

    print(json.dumps(result, indent=2))

    if result["status"] == FAIL:
        sys.exit(1)
    elif result["status"] == ESCALATE:
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
