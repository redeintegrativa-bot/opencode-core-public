#!/usr/bin/env python3
"""Perfil local de capacidade para adaptar cada sessao ao dispositivo."""

import argparse
import json
import os
import platform
import shutil
from datetime import datetime, timezone
from pathlib import Path


def command_available(name: str) -> bool:
    return shutil.which(name) is not None


def memory_mb() -> int | None:
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemTotal:"):
                return int(line.split()[1]) // 1024
    except OSError:
        pass
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera o perfil de capacidade local.")
    parser.add_argument("--write", action="store_true", help="Salva em ~/.config/opencode/capabilities/.")
    parser.add_argument("--json", action="store_true", help="Emite apenas JSON.")
    args = parser.parse_args()

    version = Path("/proc/version").read_text(encoding="utf-8", errors="ignore") if Path("/proc/version").exists() else ""
    termux = bool(os.environ.get("TERMUX_VERSION") or Path("/data/data/com.termux").exists())
    proot = "proot" in version.lower() or Path("/proc/1/root").is_symlink()
    disk = shutil.disk_usage(Path.home())
    machine = platform.node() or "unknown"
    profile = {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "device_id": machine,
        "platform": {"system": platform.system(), "release": platform.release(), "machine": platform.machine(), "termux": termux, "proot": proot},
        "resources": {"cpu_count": os.cpu_count(), "memory_mb": memory_mb(), "disk_free_mb": disk.free // (1024 * 1024)},
        "tools": {name: command_available(name) for name in ("git", "python3", "node", "npm", "docker", "vercel", "opencode")},
        "constraints": {
            "raw_sockets": not proot,
            "container_runtime": command_available("docker") and not proot,
            "desktop": bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")),
            "network_limited": proot,
        },
    }
    text = json.dumps(profile, ensure_ascii=False, indent=2) + "\n"
    if args.write:
        output = Path.home() / ".config" / "opencode" / "capabilities" / (machine + ".json")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
        if not args.json:
            print(output)
            return 0
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
