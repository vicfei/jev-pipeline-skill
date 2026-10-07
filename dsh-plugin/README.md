# jev-pipeline-dsh

DeepSeek Harness plugin that exposes the [jev-pipeline](https://github.com/vicfei/jev-pipeline-skill) workflow as model-visible tools. Three tools, no own network egress — every call shells out to the local `jev_pipeline` CLI (Python, stdlib only) inside the workspace.

**Status: v0.1, experimental.** The adapter follows the documented Cordis/DSH plugin pattern and typechecks/builds against `@deepseek-ai/dsh-tools`, but has not yet been exercised inside a live DeepSeek Harness instance — treat the engine range as untested and report issues.

## Tools

| Tool | What the model can ask for |
|---|---|
| `jev_pipeline_find` | Scan a repo for LLM calls whose output is a decision (classify / route / yes-no / rate) |
| `jev_pipeline_run` | Full offline chain: find → fit (go/no-go) → draft (pattern template) → lint |
| `jev_pipeline_cascade` | act / pass / escalate plan over logged scores (two-band policy) |

## Install

1. Install the Python CLI (once, on the machine running the harness):

   ```bash
   pip install git+https://github.com/vicfei/jev-pipeline-skill
   python3 -m jev_pipeline tools-sync   # clones the upstream MIT tool repos
   ```

2. Install this plugin from the monorepo:

   ```bash
   git clone https://github.com/vicfei/jev-pipeline-skill
   cd jev-pipeline-skill/dsh-plugin && npm install && npm run build
   ```

   Then register it in your DeepSeek Harness config (or via `cordis.patch.yml` when bundling):

   ```yaml
   jev-pipeline:
     python: python3        # interpreter that has jev_pipeline importable
     out: jev-pipeline-out  # workdir for pipeline state and reports
   ```

## Behavior notes

- The plugin starts no services and makes no network calls; work only happens when the model invokes a tool, and the CLI itself never calls an API (calibration data comes from JSONL you provide).
- If `jev_pipeline` is not importable, tools fail fast with install instructions instead of a stack trace.
- `jev_pipeline_run` writes state into the workdir and is not concurrency-safe; `find` and `cascade` are read-only computations.

Adapter structure follows [PerryLink/jevcore](https://github.com/PerryLink/jevcore)'s DSH package pattern (Apache-2.0) — see NOTICE. No upstream code copied. MIT.
