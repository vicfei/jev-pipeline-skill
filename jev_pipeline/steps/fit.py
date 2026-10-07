"""Step 2 — fit: should this candidate use Jev at all?

Adapter over abhisheksharma001/jev-skill's fit_check.py (MIT). The answers
file is prefilled with reviewable defaults — edit it and re-run `fit` to
change the verdict. Exit codes: 0=GO, 4=GO WITH GUARDS, 3=NO-GO.
"""

from __future__ import annotations

import json
from pathlib import Path

from .. import tools
from ..schema import Candidate

VERDICTS = {0: "go", 4: "go_with_guards", 3: "no_go"}

PREFILLED_ANSWERS = {
    "output_is_decision": True,      # find() only surfaces decision-shaped calls
    "code_can_decide": False,        # if it could, you would not be here
    "needs_math_dates_counting": False,
    "text_input": True,
    "fits_state_budget": True,
    "high_volume": True,
    "latency_under_300ms": False,
    "irreversible_or_regulated": False,
    "adversarial_input": True,       # user-authored input until proven otherwise
    "non_english": False,
    "can_send_data": True,
    "has_labels": False,
    "incumbent_exists": True,        # the LLM call find() flagged IS the incumbent
}


def run(cands: list[Candidate], workdir: Path) -> list[Candidate]:
    workdir.mkdir(parents=True, exist_ok=True)
    for cand in cands:
        answers_path = workdir / f"{cand.id}.answers.json"
        if not answers_path.exists():
            answers_path.write_text(
                json.dumps(PREFILLED_ANSWERS, indent=2) + "\n", encoding="utf-8"
            )
        proc = tools.run_tool("fit", "--answers", str(answers_path))
        verdict = VERDICTS.get(proc.returncode, f"error({proc.returncode})")
        cand.fit = {
            "verdict": verdict,
            "why": [ln for ln in proc.stdout.splitlines() if ln.strip()][-3:],
            "answers_path": str(answers_path),
        }
    return cands
