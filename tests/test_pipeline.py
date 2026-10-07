"""Offline end-to-end tests. Need the upstream tool repos present —
CI runs `python -m jev_pipeline tools-sync` first; locally set JEV_TOOLS_DIR.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from jev_pipeline import tools
from jev_pipeline.steps import cascade, draft, evaluate, find, fit, lint

EXAMPLES = Path(__file__).parent.parent / "examples"

needs_tools = pytest.mark.skipif(
    not (tools.tools_dir() / tools.SCRIPTS["find"]).exists(),
    reason="upstream tools not synced (run: python -m jev_pipeline tools-sync)",
)


@needs_tools
def test_run_chain(tmp_path):
    cands = find.run(str(EXAMPLES / "demo-repo"))
    assert cands, "demo-repo should yield at least one decision candidate"
    cands = fit.run(cands, tmp_path)
    assert cands[0].fit["verdict"] in ("go", "go_with_guards")
    cands = draft.run(cands)
    assert cands[0].question["kind"] in ("Choice", "Score", "Noul")
    assert cands[0].pattern
    cands = lint.run(cands, tmp_path)
    assert isinstance(cands[0].lint, list)


@needs_tools
def test_spread_discriminates(tmp_path):
    report = evaluate.spread(EXAMPLES / "responses.jsonl", tmp_path)
    assert (tmp_path / "spread.json").exists()
    assert report  # non-empty report from upstream spread.py


@needs_tools
def test_threshold_and_cascade(tmp_path):
    report = evaluate.threshold(
        EXAMPLES / "scores.jsonl", positive="spam", negative="ham", hard="hard", workdir=tmp_path
    )
    assert (tmp_path / "threshold.json").exists()
    plan = cascade.run(EXAMPLES / "scores.jsonl", tmp_path)
    total = sum(plan["counts"].values())
    rows = [ln for ln in (EXAMPLES / "scores.jsonl").read_text().splitlines() if ln.strip()]
    assert total == len(rows)
    assert set(plan["counts"]) == {"act", "pass", "escalate"}


def test_cascade_bands():
    rows_path = Path("/tmp/cascade_test.jsonl")
    rows_path.write_text(
        "\n".join(
            json.dumps(r)
            for r in [
                {"id": "a", "score": 0.9},
                {"id": "b", "score": 0.5},
                {"id": "c", "score": 0.1},
                {"id": "d", "score": 0.9, "confidence": 0.3},
            ]
        )
        + "\n"
    )
    plan = cascade.run(rows_path, Path("/tmp"))
    actions = {p["id"]: p["action"] for p in plan["plan"]}
    assert actions == {"a": "act", "b": "escalate", "c": "pass", "d": "escalate"}
