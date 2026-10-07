"""Command line: python -m jev_pipeline <step> …  (or the jev-pipeline script)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__, tools
from .schema import Candidate, load_candidates, save_candidates
from .steps import cascade, draft, evaluate, find, fit, lint


def _workdir(path: str) -> Path:
    wd = Path(path)
    wd.mkdir(parents=True, exist_ok=True)
    return wd


def _print_candidates(cands: list[Candidate]) -> None:
    for c in cands:
        fit_v = c.fit.get("verdict", "-")
        q = c.question.get("kind", "-") if c.question else "-"
        lint_n = len(c.lint)
        print(f"  {c.id}  {c.file:24} {c.primitive:7} fit={fit_v:16} q={q:7} lint={lint_n}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="jev-pipeline",
        description="Orchestrate Jev question design: find → fit → draft → lint → spread → threshold → cascade.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--out", default="jev-pipeline-out", help="workdir for state and reports")

    sub.add_parser("tools-sync", parents=[common], help="clone/update the upstream tool repos")
    p_run = sub.add_parser("run", parents=[common], help="find + fit + draft + lint over a repo")
    p_run.add_argument("repo")
    p_run.add_argument("--min-score", type=int, default=1)
    for name, help_ in [
        ("find", "scan a codebase for decision-shaped LLM calls"),
        ("fit", "go/no-go per candidate"),
        ("draft", "pick question templates"),
        ("lint", "static-check the drafts"),
    ]:
        sp = sub.add_parser(name, parents=[common], help=help_)
        sp.add_argument("repo", nargs="?", help="(find only) repo path")
        sp.add_argument("--min-score", type=int, default=1)
    p_spread = sub.add_parser("spread", parents=[common], help="discrimination test on responses JSONL")
    p_spread.add_argument("file")
    p_thr = sub.add_parser("threshold", parents=[common], help="threshold calibration on scores JSONL")
    p_thr.add_argument("file")
    p_thr.add_argument("--positive", required=True)
    p_thr.add_argument("--negative", default="")
    p_thr.add_argument("--hard", default="")
    p_cov = sub.add_parser("coverage", parents=[common], help="was the right option ever offered?")
    p_cov.add_argument("file")
    p_cas = sub.add_parser("cascade", parents=[common], help="act/pass/escalate plan from scores JSONL")
    p_cas.add_argument("file")

    args = parser.parse_args(argv)
    wd = _workdir(args.out)
    state = wd / "candidates.jsonl"

    if args.cmd == "tools-sync":
        tools.sync()
        return 0

    if args.cmd in ("run", "find"):
        cands = find.run(args.repo, args.min_score)
        if not cands:
            print("no decision-shaped LLM calls found — try --min-score 0")
        save_candidates(cands, state)
        print(f"find: {len(cands)} candidate(s) → {state}")
        _print_candidates(cands)
        if args.cmd == "find" or not cands:
            return 0
        cands = fit.run(cands, wd)
        cands = draft.run(cands)
        cands = lint.run(cands, wd)
        save_candidates(cands, state)
        print("\nrun complete:")
        _print_candidates(cands)
        print(f"\nreports: {wd}")
        return 0

    if args.cmd == "fit":
        cands = fit.run(load_candidates(state), wd)
        save_candidates(cands, state)
        _print_candidates(cands)
        return 0
    if args.cmd == "draft":
        cands = draft.run(load_candidates(state))
        save_candidates(cands, state)
        _print_candidates(cands)
        return 0
    if args.cmd == "lint":
        cands = lint.run(load_candidates(state), wd)
        save_candidates(cands, state)
        _print_candidates(cands)
        return 0

    if args.cmd == "spread":
        print(json.dumps(evaluate.spread(Path(args.file), wd), indent=2)[:2000])
        return 0
    if args.cmd == "threshold":
        print(json.dumps(evaluate.threshold(
            Path(args.file), args.positive, wd, args.negative, args.hard), indent=2)[:2000])
        return 0
    if args.cmd == "coverage":
        print(json.dumps(evaluate.coverage(Path(args.file), wd), indent=2)[:2000])
        return 0
    if args.cmd == "cascade":
        print(json.dumps(cascade.run(Path(args.file), wd), indent=2)[:2000])
        return 0

    parser.error(f"unknown command {args.cmd}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
