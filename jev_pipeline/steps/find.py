"""Step 1 — find: where are LLM calls making decisions in this codebase?

Adapter over abhisheksharma001/jev-skill's find_decision_calls.py (MIT).
"""

from __future__ import annotations

import json

from .. import tools
from ..schema import Candidate


def run(repo: str, min_score: int = 1) -> list[Candidate]:
    proc = tools.run_tool("find", repo, "--json", "--min-score", str(min_score))
    if proc.returncode != 0:
        raise SystemExit(f"find failed: {proc.stderr.strip()}")
    try:
        hits = json.loads(proc.stdout)
    except ValueError as err:
        raise SystemExit(f"find returned unparseable output: {err}\n{proc.stdout[:400]}") from err
    cands = []
    for i, hit in enumerate((hits or []), start=1):
        if not isinstance(hit, dict) or hit.get("verdict") != "candidate":
            continue
        primitives = hit.get("likely_primitive") or ["choice"]
        cands.append(
            Candidate(
                id=f"c{i:03d}",
                source="find",
                file=f"{hit.get('file', '?')}:{hit.get('line', '?')}",
                decision="; ".join(hit.get("signals") or []) or "unnamed decision",
                primitive=primitives[0],
                raw=hit,
            )
        )
    return cands
