# Attribution

This project is an orchestrator: it calls upstream tools by reference and copies none of their code. `tools-sync` clones the upstream repositories into `~/.cache/jev-pipeline/tools` (override with `JEV_TOOLS_DIR`); each pipeline step runs their scripts as-is, so their licenses, notices, and updates stay intact upstream.

| Upstream | License | What this pipeline uses | How |
|---|---|---|---|
| [abhisheksharma001/jev-skill](https://github.com/abhisheksharma001/jev-skill) | MIT | `find_decision_calls.py` (find step), `fit_check.py` (fit step) | subprocess, cloned at sync time |
| [VBS2004/jev-questions-skill](https://github.com/VBS2004/jev-questions-skill) | MIT | `lint_questions.py`, `spread.py`, `threshold.py`, `coverage.py` | subprocess, cloned at sync time |
| [vicfei/awesome-jev-prompts](https://github.com/vicfei/awesome-jev-prompts) | CC0 | question templates condensed into `jev_pipeline/patterns.py` (draft step), two-band cascade policy | content, CC0 |
| [PyModel/jev-skill](https://github.com/PyModel/jev-skill) | MIT | nothing wired yet — its "eleven implementation shapes" inform the roadmap for `draft` | reference only |
| [wuyoscar/jev-skill](https://github.com/wuyoscar/jev-skill) | MIT | nothing wired yet — its scenario templates are a planned `draft` input source | reference only |

If you are an upstream author and want a step changed, added, or removed — open an issue; this project exists to route credit and users to your tools, not to shadow them.
