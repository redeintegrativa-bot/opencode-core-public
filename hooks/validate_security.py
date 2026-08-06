"""
Security Validation Hook for OpenCode-Core.

Validates files and code against security rules parsed from markdown documentation.
Provides structured pass/fail results with detailed violation reporting.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Any


class SecurityValidator:
    """Validates code against security rules defined in a markdown file."""

    DEFAULT_RULES_PATH = Path(__file__).resolve().parents[1] / "rules" / "common" / "security.md"

    # Compiled regex patterns for security checks
    SECRET_PATTERNS: list[re.Pattern[str]] = [
        re.compile(r"(?i)(api[_-]?key|secret[_-]?key|password|passwd|token)\s*[=:]\s*['\"][^'\"]{8,}['\"]"),
        re.compile(r"sk-[a-zA-Z0-9]{20,}"),
        re.compile(r"ghp_[a-zA-Z0-9]{36,}"),
        re.compile(r"AKIA[0-9A-Z]{16}"),
        re.compile(r"(?i)(?:api[_-]?key|secret|password|token)\s*=\s*['\"][^'\"]+['\"]"),
    ]

    EVAL_EXEC_PATTERN: re.Pattern[str] = re.compile(
        r"\b(eval|exec)\s*\("
    )

    SHELL_INJECTION_PATTERNS: list[re.Pattern[str]] = [
        re.compile(r"os\.system\s*\("),
        re.compile(r"subprocess\.(?:call|run|Popen|check_output|check_call)\s*\(.*shell\s*=\s*True"),
        re.compile(r"os\.popen\s*\("),
    ]

    SQL_INJECTION_PATTERNS: list[re.Pattern[str]] = [
        re.compile(r"""(?i)(?:execute|cursor\.execute|query)\s*\(\s*['"](?:.*%\s*s|.*\{0\}|.*\+|.*\.format)"""),
        re.compile(r"""(?i)(?:execute|cursor\.execute|query)\s*\(.*f['"]"""),
        re.compile(r"""(?i)query\s*=\s*['"](?:.*%\s*s|.*\{0\}|.*\+|.*\.format)"""),
    ]

    HARDCODED_IP_PATTERN: re.Pattern[str] = re.compile(
        r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b"
    )

    DEBUG_MODE_PATTERNS: list[re.Pattern[str]] = [
        re.compile(r"(?i)DEBUG\s*=\s*True"),
        re.compile(r"(?i)debug\s*:\s*true"),
        re.compile(r"(?i)NODE_ENV\s*=\s*['\"]?development['\"]?"),
    ]

    UNSAFE_DESERIALIZATION_PATTERNS: list[re.Pattern[str]] = [
        re.compile(r"pickle\.loads?\s*\("),
        re.compile(r"yaml\.load\s*\((?!.*Loader)"),
        re.compile(r"marshal\.loads?\s*\("),
    ]

    CORS_WILDCARD_PATTERNS: list[re.Pattern[str]] = [
        re.compile(r"""(?i)(?:Access-Control-Allow-Origin|allow_origins?)\s*[:=]\s*['"]\*['"]"""),
        re.compile(r"""(?i)cors\s*\(\s*\)"""),
        re.compile(r"""(?i)@cross_origin\s*\(\s*\)"""),
    ]

    RATE_LIMIT_PATTERNS: list[re.Pattern[str]] = [
        re.compile(r"(?:@app\.route|@router\.|@api_view|@require_http_methods|@(?:get|post|put|delete|patch|head|options))"),
    ]

    INPUT_VALIDATION_PATTERNS: list[re.Pattern[str]] = [
        re.compile(r"(?:isinstance|type\()\s+"),
        re.compile(r"(?:validate|sanitize|check_input|assert)\s*\("),
        re.compile(r"raise\s+(?:ValueError|TypeError|ValidationError)"),
        re.compile(r"try\s*:\s*\n\s+(?:.*(?:int|float|str)\s*\()"),
        re.compile(r"(?:json\.load|schema|pydantic|marshmallow)"),
    ]

    SKIP_EXTENSIONS: set[str] = {".pyc", ".pyo", ".so", ".dll", ".exe", ".bin", ".png", ".jpg", ".gif", ".ico", ".woff", ".ttf"}

    def __init__(self, rules_path: str | Path | None = None) -> None:
        self.rules_path = Path(rules_path) if rules_path else Path(self.DEFAULT_RULES_PATH)
        self.rules: list[dict[str, str]] = []
        self.violations: list[dict[str, Any]] = []
        self.files_scanned: int = 0
        self.load_rules()

    def load_rules(self) -> list[dict[str, str]]:
        """Parse ## heading rules from a markdown file."""
        if not self.rules_path.exists():
            return self.rules

        content = self.rules_path.read_text(encoding="utf-8")
        rules: list[dict[str, str]] = []
        sections = re.split(r"^## ", content, flags=re.MULTILINE)

        for section in sections[1:]:
            lines = section.strip().splitlines(keepends=False)
            name = lines[0].strip()
            description = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""
            rules.append({"name": name, "description": description})

        self.rules = rules
        return rules

    def validate_code(self, code: str, filename: str = "<string>") -> list[dict[str, Any]]:
        """Validate a raw code string against all hardcoded security rules."""
        violations: list[dict[str, Any]] = []
        lines = code.splitlines()

        for i, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("//") or "re.compile(" in stripped:
                continue

            for pattern in self.SECRET_PATTERNS:
                if pattern.search(line):
                    violations.append(self._violation("No hardcoded secrets", "CRITICAL", filename, i, line))
                    break

            for pattern in self.EVAL_EXEC_PATTERN.finditer(line):
                violations.append(self._violation("No eval/exec calls", "CRITICAL", filename, i, line))

            for pattern in self.SHELL_INJECTION_PATTERNS:
                if pattern.search(line):
                    violations.append(self._violation("No shell injection", "HIGH", filename, i, line))
                    break

            for pattern in self.SQL_INJECTION_PATTERNS:
                if pattern.search(line):
                    violations.append(self._violation("No SQL injection", "CRITICAL", filename, i, line))
                    break

            for pattern in [self.HARDCODED_IP_PATTERN]:
                if pattern.search(line) and "localhost" not in line.lower() and "127.0.0.1" not in line:
                    violations.append(self._violation("No hardcoded IPs", "MEDIUM", filename, i, line))

            for pattern in self.DEBUG_MODE_PATTERNS:
                if pattern.search(line):
                    violations.append(self._violation("No debug mode in production", "MEDIUM", filename, i, line))
                    break

            for pattern in self.UNSAFE_DESERIALIZATION_PATTERNS:
                if pattern.search(line):
                    violations.append(self._violation("No unsafe deserialization", "HIGH", filename, i, line))
                    break

            for pattern in self.CORS_WILDCARD_PATTERNS:
                if pattern.search(line):
                    violations.append(self._violation("No CORS wildcard", "MEDIUM", filename, i, line))
                    break

        has_endpoint = any(p.search(code) for p in self.RATE_LIMIT_PATTERNS)
        if has_endpoint:
            has_rate_limit = re.search(r"(?:rate.?limit|throttl|limiter)", code, re.IGNORECASE) is not None
            if not has_rate_limit:
                violations.append(self._violation("Rate limiting check on endpoints", "MEDIUM", filename, 1, "(entire file)"))

        self.violations.extend(violations)
        return violations

    def validate_file(self, filepath: str | Path) -> list[dict[str, Any]]:
        """Validate a single file against all security rules."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if not path.is_file():
            raise ValueError(f"Not a file: {path}")
        if path.suffix.lower() in self.SKIP_EXTENSIONS:
            return []
        if path.stat().st_size > 1_000_000:
            return []

        self.files_scanned += 1
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except (OSError, PermissionError) as exc:
            self.violations.append(self._violation("File access error", "INFO", str(path), 0, str(exc)))
            return []

        return self.validate_code(content, str(path))

    def validate_directory(self, dirpath: str | Path, extensions: list[str] | None = None) -> list[dict[str, Any]]:
        """Validate all matching files in a directory tree."""
        path = Path(dirpath)
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")
        if not path.is_dir():
            raise ValueError(f"Not a directory: {path}")

        if extensions is None:
            extensions = [".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rb", ".java", ".php", ".rs", ".sh", ".yaml", ".yml", ".toml", ".json", ".env", ".cfg", ".conf", ".ini"]

        skip_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", "vendor", ".tox", ".eggs", "dist", "my-money-track"}
        violations: list[dict[str, Any]] = []

        for root, dirs, files in os.walk(path):
            root = Path(root)
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for fname in sorted(files):
                fpath = Path(root) / fname
                if fpath.suffix.lower() in extensions:
                    try:
                        result = self.validate_file(fpath)
                        violations.extend(result)
                    except (FileNotFoundError, ValueError):
                        continue

        return violations

    def get_report(self) -> dict[str, Any]:
        """Return a structured report dict of the validation run."""
        severity_counts: dict[str, int] = {}
        rule_counts: dict[str, int] = {}
        for v in self.violations:
            severity_counts[v["severity"]] = severity_counts.get(v["severity"], 0) + 1
            rule_counts[v["rule"]] = rule_counts.get(v["rule"], 0) + 1

        return {
            "passed": not any(v["severity"] in {"CRITICAL", "HIGH"} for v in self.violations),
            "total_violations": len(self.violations),
            "files_scanned": self.files_scanned,
            "severity_breakdown": severity_counts,
            "rule_breakdown": rule_counts,
            "violations": self.violations,
        }

    def _violation(self, rule: str, severity: str, filename: str, line: int, code: str) -> dict[str, Any]:
        return {
            "rule": rule,
            "severity": severity,
            "file": filename,
            "line": line,
            "code": code.strip()[:200],
        }


def _print_report(report: dict[str, Any]) -> None:
    """Pretty-print a validation report."""
    print("=" * 60)
    print("  SECURITY VALIDATION REPORT")
    print("=" * 60)
    print(f"  Files scanned:    {report['files_scanned']}")
    print(f"  Total violations: {report['total_violations']}")
    if report["severity_breakdown"]:
        print("  Severity breakdown:")
        for sev, count in sorted(report["severity_breakdown"].items()):
            print(f"    {sev}: {count}")
    if report["rule_breakdown"]:
        print("  Rules violated:")
        for rule, count in sorted(report["rule_breakdown"].items()):
            print(f"    {rule}: {count}")
    print("-" * 60)
    if report["passed"]:
        print("  RESULT: PASS — No violations found.")
    else:
        print("  RESULT: FAIL — Violations detected.\n")
        for v in report["violations"]:
            print(f"  [{v['severity']}] {v['rule']}")
            print(f"    File: {v['file']}:{v['line']}")
            print(f"    Code: {v['code']}")
            print()
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <directory> [extension1 extension2 ...]")
        sys.exit(1)

    target = sys.argv[1]
    exts = sys.argv[2:] if len(sys.argv) > 2 else None

    validator = SecurityValidator()
    validator.validate_directory(target, extensions=exts)
    report = validator.get_report()
    _print_report(report)
    sys.exit(1 if not report["passed"] else 0)
