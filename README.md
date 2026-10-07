# Jev Pipeline Skill

> **v0.1 — early prototype.** The chain works end to end offline; treat APIs and defaults as unstable.

One workflow for Jev question design:

```
find ──► fit ──► draft ──► lint ──► (collect responses) ──► spread ──► threshold ──► cascade
```

Find where your codebase makes LLM calls that are really decisions, check whether each one should be a Jev question at all, draft it from a field-tested pattern, lint it, then — once you have responses — check the question discriminates, calibrate thresholds on the hard cases, and get an act/pass/escalate plan.

**This is an orchestrator, not another catalog.** It wires together the best community tools by reference (never copying them — see [ATTRIBUTION.md](ATTRIBUTION.md)) and adds the glue they each lack: a unified candidate record that flows through every step, pattern-based drafting from [awesome-jev-prompts](https://github.com/vicfei/awesome-jev-prompts) (43 patterns, CC0), and a cascade policy where the uncertain middle band is an explicit branch, never an averaged decision.

## Install & quickstart

Install as an **agent skill** (Claude Code, Codex, OpenCode, and other agents that support the open skills format):

```bash
npx skills add vicfei/jev-pipeline-skill
```

Or use the CLI directly:

```bash
git clone https://github.com/vicfei/jev-pipeline-skill && cd jev-pipeline-skill
pip install -e .

python -m jev_pipeline tools-sync          # clone the two upstream tool repos (once)
python -m jev_pipeline run examples/demo-repo
#   find: 1 candidate(s)
#     c001  triage.py:8  choice  fit=go_with_guards  q=Choice  lint=0

python -m jev_pipeline cascade examples/scores.jsonl   # act/pass/escalate plan
```

Python ≥ 3.10, stdlib only, no API key needed for any step (live Jev calls happen in *your* code, not in this pipeline).

## The steps

| Step | What it answers | Source |
|---|---|---|
| `find REPO` | Which LLM calls in this codebase output decisions, not text? | calls [abhisheksharma001/jev-skill](https://github.com/abhisheksharma001/jev-skill) `find_decision_calls.py` |
| `fit` | Should this candidate use Jev — go, go-with-guards, or no-go? | calls `fit_check.py`; answers file is written per candidate for you to review and re-run |
| `draft` | What does a good first question look like for this decision? | original — pattern matching against awesome-jev-prompts templates |
| `lint` | Does the draft break the known question-design rules? | calls [VBS2004/jev-questions-skill](https://github.com/VBS2004/jev-questions-skill) `lint_questions.py` |
| `spread RESPONSES.jsonl` | Can this question tell cases apart, or is it a constant? | calls `spread.py` |
| `threshold SCORES.jsonl` | Where does the bar go, fitted on hard cases? | calls `threshold.py` |
| `coverage CASES.jsonl` | Was the right option ever on offer? | calls `coverage.py` |
| `cascade SCORES.jsonl` | Which answers act, which pass, which escalate to a System Two model? | original — two-band policy: middle band and low-confidence tops escalate, never average |

State lives in `--out` (default `./jev-pipeline-out/`): `candidates.jsonl` is the unified record every step enriches; `*.answers.json` are editable fit inputs; `spread/threshold/coverage/cascade.json` are reports.

## Design rules

1. **Upstream tools are called, never copied** — `tools-sync` clones the two repos and each step runs their scripts as-is (MIT; see [ATTRIBUTION.md](ATTRIBUTION.md)).
2. **No step calls an API** — calibration data comes from JSONL you collect from real usage; synthetic examples are in `examples/`.
3. **The middle band is a branch** — a Noul at 0.5 means "can't tell"; it routes to escalation, not to a midpoint decision.

## Roadmap

- `optimize` step (question rewriting with a referee) and `ensemble` wiring — upstream scripts exist, adapters planned
- `report` — one markdown summary across all steps
- wuyoscar-style scenario templates as `draft` inputs (Chinese-first)

Independent community project — not affiliated with TypeSafe AI. MIT; pattern content CC0 via awesome-jev-prompts. 中文说明见 [README.zh-CN.md](README.zh-CN.md)。
