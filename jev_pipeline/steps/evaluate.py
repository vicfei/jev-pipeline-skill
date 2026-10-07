"""Steps 5–7 — evaluate: does the question discriminate, and where does the threshold go?

Adapters over VBS2004/jev-questions-skill's spread.py / threshold.py /
coverage.py (MIT, stdlib only, no API calls). Each takes the JSONL you
collected from live Jev responses (or the synthetic example data) and writes
a JSON report into the workdir.
"""

from __future__ import annotations

import json
from pathlib import Path

from .. import tools


def _parse(proc, what: str) -> dict:
    if proc.returncode not in (0, 1):  # these tools use 1 for "findings present"
        raise SystemExit(f"{what} failed: {proc.stderr.strip()}")
    try:
        return json.loads(proc.stdout)
    except ValueError:
        return {"raw_stdout": proc.stdout}


def spread(file: Path, workdir: Path) -> dict:
    proc = tools.run_tool("spread", str(file), "--json")
    report = _parse(proc, "spread")
    (workdir / "spread.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def threshold(file: Path, positive: str, workdir: Path,
              negative: str = "", hard: str = "", direction: str = "high") -> dict:
    args = ["--positive", positive, "--direction", direction, "--json"]
    if negative:
        args += ["--negative", negative]
    if hard:
        args += ["--hard", hard]
    proc = tools.run_tool("threshold", str(file), *args)
    report = _parse(proc, "threshold")
    (workdir / "threshold.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def coverage(file: Path, workdir: Path) -> dict:
    proc = tools.run_tool("coverage", str(file), "--json")
    report = _parse(proc, "coverage")
    (workdir / "coverage.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report
