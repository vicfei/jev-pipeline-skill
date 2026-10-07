"""Step 3 — draft: pick a question template from the pattern library.

Original step: matches each candidate to one of the condensed
awesome-jev-prompts patterns (see jev_pipeline/patterns.py).
"""

from __future__ import annotations

from ..patterns import draft_for
from ..schema import Candidate


def run(cands: list[Candidate]) -> list[Candidate]:
    for cand in cands:
        if cand.fit.get("verdict") == "no_go":
            cand.question = {}
            continue
        pattern_id, question = draft_for(cand.primitive, cand.decision)
        cand.pattern = pattern_id
        cand.question = question
    return cands
