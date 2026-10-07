"""Resolve the upstream tool scripts this pipeline orchestrates.

The pipeline never copies upstream code: `tools sync` clones the two source
repos (attributed in ATTRIBUTION.md) and every step calls their scripts as-is.
Override the location with JEV_TOOLS_DIR (used by tests and CI).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

TOOL_REPOS = {
    "jev-questions-skill": "https://github.com/VBS2004/jev-questions-skill",
    "jev-skill": "https://github.com/abhisheksharma001/jev-skill",
}

SCRIPTS = {
    "find": "jev-skill/skills/jev/scripts/find_decision_calls.py",
    "fit": "jev-skill/skills/jev/scripts/fit_check.py",
    "lint": "jev-questions-skill/skills/jev-questions/scripts/lint_questions.py",
    "spread": "jev-questions-skill/skills/jev-questions/scripts/spread.py",
    "threshold": "jev-questions-skill/skills/jev-questions/scripts/threshold.py",
    "coverage": "jev-questions-skill/skills/jev-questions/scripts/coverage.py",
}


def tools_dir() -> Path:
    return Path(os.environ.get("JEV_TOOLS_DIR") or (Path.home() / ".cache" / "jev-pipeline" / "tools"))


def script(name: str) -> Path:
    path = tools_dir() / SCRIPTS[name]
    if not path.exists():
        raise SystemExit(
            f"upstream tool '{name}' not found at {path}.\n"
            "Run: python -m jev_pipeline tools sync"
        )
    return path


def sync() -> None:
    tools_dir().mkdir(parents=True, exist_ok=True)
    for name, url in TOOL_REPOS.items():
        dest = tools_dir() / name
        if (dest / ".git").exists():
            subprocess.run(["git", "-C", str(dest), "pull", "-q", "--ff-only"], check=False)
            print(f"synced (pull) {name}")
        else:
            subprocess.run(
                ["git", "clone", "-q", "--depth", "1", url, str(dest)], check=True
            )
            head = subprocess.run(
                ["git", "-C", str(dest), "rev-parse", "--short", "HEAD"],
                capture_output=True, text=True, check=True,
            ).stdout.strip()
            print(f"synced (clone @{head}) {name}")


def run_tool(name: str, *args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    """Run an upstream script; return the completed process (stdout is JSON where supported)."""
    return subprocess.run(
        [sys.executable, str(script(name)), *args],
        capture_output=True, text=True, input=stdin, timeout=300,
    )
