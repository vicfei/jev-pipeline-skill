"""Step 8 — cascade: which answers can act, and which go to a System Two model?

Original step. Implements the two-band policy from awesome-jev-prompts
(calibration-and-eval): act on the top band, pass the bottom band, and treat
the middle band — or any low-confidence top-band answer — as an explicit
escalation branch instead of rounding it into a decision.
"""

from __future__ import annotations

import json
from pathlib import Path

DEFAULT_BANDS = {"act_min": 0.75, "review_min": 0.40}


def run(file: Path, workdir: Path, bands: dict | None = None) -> dict:
    bands = {**DEFAULT_BANDS, **(bands or {})}
    rows = [json.loads(ln) for ln in file.read_text().splitlines() if ln.strip()]
    plan, counts = [], {"act": 0, "pass": 0, "escalate": 0}
    for row in rows:
        score = float(row["score"])
        conf = float(row.get("confidence", 1.0))
        if score >= bands["act_min"]:
            action = "act" if conf >= 0.5 else "escalate"
        elif score < bands["review_min"]:
            action = "pass"
        else:
            action = "escalate"  # uncertain middle band: explicit branch, never averaged
        counts[action] += 1
        plan.append({"id": row.get("id", "?"), "score": score, "action": action})
    report = {"bands": bands, "counts": counts, "plan": plan}
    (workdir / "cascade.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report
