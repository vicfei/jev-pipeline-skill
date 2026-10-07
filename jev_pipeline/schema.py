"""The unified candidate record that flows between pipeline steps."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class Candidate:
    id: str
    source: str = "find"          # find | manual
    file: str = ""                # file:line of the incumbent decision
    decision: str = ""            # what the decision is, in words
    primitive: str = "unknown"    # choice | score | noul
    fit: dict = field(default_factory=dict)        # {verdict, why, answers_path}
    question: dict = field(default_factory=dict)   # drafted question (SDK shape)
    pattern: str = ""             # pattern id from jev_pipeline.patterns
    lint: list = field(default_factory=list)       # lint findings
    raw: dict = field(default_factory=dict)        # upstream find() hit, verbatim


def load_candidates(path: Path) -> list[Candidate]:
    if not path.exists():
        return []
    return [Candidate(**json.loads(line)) for line in path.read_text().splitlines() if line.strip()]


def save_candidates(cands: list[Candidate], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(asdict(c), ensure_ascii=False) for c in cands) + "\n",
        encoding="utf-8",
    )
