#!/usr/bin/env python3
"""PreSkillInvoke validation hook.

Validates skill integrity before invoking a skill.
Checks: SKILL.md exists, frontmatter format, required fields.
Returns: PASS / FAIL / ESCALATE
"""

import json
import re
import sys
from pathlib import Path

HOOKS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = HOOKS_DIR.parent
SKILLS_DIR = PROJECT_ROOT / "skills"
MIN_SUPPORTED_VERSION = "1.0.0"
REQUIRED_FIELDS = ["name", "description"]
PASS = "PASS"
FAIL = "FAIL"
ESCALATE = "ESCALATE"


def _now_iso():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def parse_frontmatter(skill_md_path):
    """Extract YAML frontmatter from SKILL.md between --- delimiters."""
    content = skill_md_path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return None, content
    raw = match.group(1)
    fm = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip().strip("\"'")
    return fm, content


def version_tuple(v):
    """Convert version string like '1.0.0' to comparable tuple."""
    try:
        return tuple(int(x) for x in v.split("."))
    except (ValueError, AttributeError):
        return (0, 0, 0)


def validate_skill(skill_name):
    result = {
        "status": PASS,
        "skill": skill_name,
        "timestamp": _now_iso(),
        "checks": [],
        "errors": [],
        "warnings": [],
    }

    skill_path = SKILLS_DIR / skill_name / "SKILL.md"

    # Check 1: SKILL.md exists
    if not skill_path.exists():
        result["checks"].append({"name": "file_exists", "passed": False})
        result["errors"].append(f"VH004: Skill not found: {skill_path}")
        result["status"] = FAIL
        result["action"] = "DEFAULT"
        return result
    result["checks"].append({"name": "file_exists", "passed": True})
    result["skill_path"] = str(skill_path.relative_to(PROJECT_ROOT))

    # Check 2: Parse frontmatter
    frontmatter, _ = parse_frontmatter(skill_path)
    if frontmatter is None:
        result["checks"].append({"name": "frontmatter_parse", "passed": False})
        result["errors"].append(f"VH005: No valid frontmatter in {skill_name}/SKILL.md")
        result["status"] = FAIL
        result["action"] = "DEFAULT"
        return result
    result["checks"].append({"name": "frontmatter_parse", "passed": True})

    # Check 3: Required fields
    missing = [f for f in REQUIRED_FIELDS if f not in frontmatter]
    if missing:
        result["checks"].append({"name": "required_fields", "passed": False})
        result["errors"].append(f"VH005: Missing frontmatter fields: {', '.join(missing)}")
        result["status"] = FAIL
        result["action"] = "DEFAULT"
        return result
    result["checks"].append({"name": "required_fields", "passed": True})

    # Check 4: Version not deprecated
    version = frontmatter.get("version", "1.0.0")
    if version_tuple(version) < version_tuple(MIN_SUPPORTED_VERSION):
        result["checks"].append({"name": "version_check", "passed": False})
        result["warnings"].append(f"Skill version deprecated: {skill_name} v{version}")
        result["status"] = ESCALATE
        result["action"] = "ESCALATE"
    else:
        result["checks"].append({"name": "version_check", "passed": True})

    # Check 5: Not deprecated flag
    if frontmatter.get("deprecated", "").lower() in ("true", "yes", "1"):
        result["checks"].append({"name": "deprecated_flag", "passed": False})
        result["warnings"].append(f"Skill is marked deprecated: {skill_name}")
        result["status"] = ESCALATE
        result["action"] = "ESCALATE"
    else:
        result["checks"].append({"name": "deprecated_flag", "passed": True})

    if result["status"] == PASS:
        result["action"] = "PROCEED"

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_skill.py <skill_name>", file=sys.stderr)
        sys.exit(1)

    skill_name = sys.argv[1]
    result = validate_skill(skill_name)

    print(json.dumps(result, indent=2))

    if result["status"] == FAIL:
        sys.exit(1)
    elif result["status"] == ESCALATE:
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
