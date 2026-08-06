#!/usr/bin/env python3
"""Fail when OpenCode utility modules can be auto-loaded as plugins."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ROOT / "plugins"
FORBIDDEN_ROOT = {"notify.js", "python-helper.js"}
EXPORT_RE = re.compile(r"^\s*export\s+(?:default\s+)?(?:async\s+)?(?:const|let|var|function|class)\s+", re.MULTILINE)
IMPORT_RE = re.compile(r'''from\s+["'](\./lib/[^"']+)["']''')

errors: list[str] = []
root_js = sorted(PLUGINS.glob("*.js"))

for path in root_js:
    if path.name in FORBIDDEN_ROOT:
        errors.append(f"utility module must live in plugins/lib: {path.relative_to(ROOT)}")
    text = path.read_text(encoding="utf-8")
    exports = EXPORT_RE.findall(text)
    if len(exports) != 1:
        errors.append(f"plugin root file must export exactly one plugin factory: {path.relative_to(ROOT)} ({len(exports)} exports)")
    for relative in IMPORT_RE.findall(text):
        target = (path.parent / relative).resolve()
        if not target.is_file():
            errors.append(f"missing plugin helper imported by {path.relative_to(ROOT)}: {relative}")

for name in FORBIDDEN_ROOT:
    if not (PLUGINS / "lib" / name).is_file():
        errors.append(f"required helper missing: plugins/lib/{name}")

setup_requirements = {
    "setup.ps1": ("-Recurse", "legacyHelper", "python-helper.js"),
    "setup.sh": ("cp -R", "plugins_target/notify.js", "plugins_target/python-helper.js"),
}
for relative, required in setup_requirements.items():
    setup_path = ROOT / relative
    setup_text = setup_path.read_text(encoding="utf-8-sig")
    for snippet in required:
        if snippet not in setup_text:
            errors.append(f"installer regression in {relative}: missing {snippet!r}")

if errors:
    print("Plugin layout validation failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)

print(f"Plugin layout OK: {len(root_js)} plugins; helpers isolated in plugins/lib")