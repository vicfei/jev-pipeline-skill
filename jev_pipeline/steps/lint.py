"""Step 4 — lint: static checks on the drafted questions.

Adapter over VBS2004/jev-questions-skill's lint_questions.py (MIT). Drafts
are materialized as real `typesafe_sdk` call sites in a scratch file, so the
upstream linter sees exactly what a reviewer would.
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

from .. import tools
from ..schema import Candidate

_KIND = {"Choice": "Choice", "Score": "Score", "Noul": "Noul"}


def _render(cand: Candidate) -> str:
    q = cand.question
    kind = _KIND.get(q.get("kind", "Choice"))
    if kind == "Choice":
        body = f'Choice(instructions={q["instructions"]!r}, criteria={q["criteria"]!r})'
    elif kind == "Score":
        body = f'Score(instructions={q["instructions"]!r}, criteria={q["criteria"]!r})'
    else:
        body = f'Noul(instructions={q["instructions"]!r})'
    return textwrap.dedent(f"""\
        from typesafe_sdk import Choice, Noul, Score

        # candidate {cand.id}: {cand.decision} ({cand.file})
        question = {body}
        """)


def run(cands: list[Candidate], workdir: Path) -> list[Candidate]:
    scratch = workdir / "drafts"
    scratch.mkdir(parents=True, exist_ok=True)
    for cand in cands:
        if not cand.question:
            cand.lint = []
            continue
        py = scratch / f"{cand.id}.py"
        py.write_text(_render(cand), encoding="utf-8")
    proc = tools.run_tool("lint", str(scratch), "--json")
    findings: dict[str, list] = {}
    if proc.stdout.strip():
        try:
            findings = json.loads(proc.stdout)
        except ValueError:
            findings = {}
    for cand in cands:
        cand.lint = findings.get(f"{cand.id}.py", [])
    return cands
