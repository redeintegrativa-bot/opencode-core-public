#!/usr/bin/env python3
"""Pre-commit validation hook.

Scans staged files for secrets, .env files, and dangerous patterns.
CLI: python validate_commit.py [directory]
If directory is omitted, scans current working directory via git.
Exit: 0=PASS, 1=FAIL
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

HOOKS_DIR = Path(__file__).resolve().parent
PASS = "PASS"
FAIL = "FAIL"

SECRET_PATTERNS = [
    re.compile(r"(?:api[_-]?key|apikey|secret|password|token|sk-|ghp_|AKIA[A-Z0-9]{16})\s*[:=]\s*['\"][^'\"]{8,}", re.IGNORECASE),
]
SECRET_EXCLUDE = re.compile(r"example|template|placeholder|YOUR_|xxx|changeme", re.IGNORECASE)
ENV_FILE_PATTERN = re.compile(r"\.env$")
DANGEROUS_PATTERNS = [
    (re.compile(r"eval\s*\("), "eval()"),
    (re.compile(r"exec\s*\("), "exec()"),
    (re.compile(r"os\.system\s*\("), "os.system()"),
    (re.compile(r"subprocess\.\w+\(.*shell\s*=\s*True"), "subprocess with shell=True"),
]
CODE_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rb", ".php"}


def get_staged_files(directory):
    """Get list of staged files via git diff --cached."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            cwd=directory,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return None
        files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
        return files
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


def scan_secrets(filepath):
    """Check a file for hardcoded secrets. Returns list of findings."""
    findings = []
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            for lineno, line in enumerate(f, 1):
                for pat in SECRET_PATTERNS:
                    if pat.search(line) and not SECRET_EXCLUDE.search(line):
                        findings.append({"file": str(filepath), "line": lineno, "content": line.rstrip()[:120]})
                        break
    except (OSError, UnicodeDecodeError):
        pass
    return findings


def check_env_files(staged_files):
    """Return list of .env files found in staged list."""
    return [f for f in staged_files if ENV_FILE_PATTERN.search(f)]


def scan_dangerous(filepath):
    """Check a file for dangerous code patterns. Returns list of findings."""
    findings = []
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            for lineno, line in enumerate(f, 1):
                for pat, label in DANGEROUS_PATTERNS:
                    if pat.search(line):
                        findings.append({"file": str(filepath), "line": lineno, "pattern": label, "content": line.rstrip()[:120]})
    except (OSError, UnicodeDecodeError):
        pass
    return findings


def validate_commit(directory):
    result = {
        "status": PASS,
        "directory": str(directory),
        "timestamp": _now_iso(),
        "checks": [],
        "errors": [],
        "warnings": [],
    }

    staged_files = get_staged_files(directory)
    if staged_files is None:
        result["checks"].append({"name": "git_staged", "passed": False})
        result["errors"].append("Not a git repository or git not available")
        result["status"] = FAIL
        return result

    if not staged_files:
        result["checks"].append({"name": "git_staged", "passed": True})
        result["message"] = "No staged files to check"
        return result
    result["checks"].append({"name": "git_staged", "passed": True, "count": len(staged_files)})

    # Check 1: Secrets
    secret_findings = []
    for fname in staged_files:
        fpath = Path(directory) / fname
        if fpath.is_file():
            secret_findings.extend(scan_secrets(fpath))
    if secret_findings:
        result["checks"].append({"name": "secrets_scan", "passed": False, "findings": len(secret_findings)})
        for f in secret_findings:
            result["errors"].append(f"SECRET: {f['file']}:{f['line']} - {f['content'][:80]}")
    else:
        result["checks"].append({"name": "secrets_scan", "passed": True})

    # Check 2: .env files
    env_files = check_env_files(staged_files)
    if env_files:
        result["checks"].append({"name": "env_files", "passed": False, "files": env_files})
        for f in env_files:
            result["errors"].append(f"ENV_FILE: {f}")
    else:
        result["checks"].append({"name": "env_files", "passed": True})

    # Check 3: Dangerous patterns
    danger_findings = []
    for fname in staged_files:
        ext = Path(fname).suffix
        if ext in CODE_EXTENSIONS:
            fpath = Path(directory) / fname
            if fpath.is_file():
                danger_findings.extend(scan_dangerous(fpath))
    if danger_findings:
        result["checks"].append({"name": "dangerous_patterns", "passed": True, "findings": len(danger_findings)})
        for f in danger_findings:
            result["warnings"].append(f"DANGEROUS: {f['file']}:{f['line']} - {f['pattern']}")
    else:
        result["checks"].append({"name": "dangerous_patterns", "passed": True})

    if result["errors"]:
        result["status"] = FAIL

    return result


def _now_iso():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def main():
    directory = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    directory = os.path.abspath(directory)

    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a directory", file=sys.stderr)
        sys.exit(1)

    result = validate_commit(directory)
    print(json.dumps(result, indent=2))

    if result["status"] == FAIL:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
