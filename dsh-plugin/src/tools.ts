/**
 * The model-visible tools. Thin by design: declare the schema, shell out to
 * one CLI step, return its text. Anything richer belongs in the Python
 * package where it is tested, not in this adapter.
 */

import { defineTool } from '@deepseek-ai/dsh-tools'
import { execPipeline, type PipelineConfig } from './exec.js'

const OUTPUT_SCHEMA = {
  type: 'object' as const,
  properties: {
    ok: { type: 'boolean' as const, required: true as const },
    exitCode: { type: 'number' as const },
    output: { type: 'string' as const, required: true as const },
  },
  additionalProperties: false,
}

function render(_args: unknown, value: unknown) {
  return [{ type: 'text' as const, text: JSON.stringify(value, null, 2) }]
}

function summary(label: string) {
  return (_args: unknown, value: unknown) => ({
    summary: `${(value as { ok?: boolean }).ok === false ? 'failed' : 'ok'} - ${label}`,
  })
}

/**
 * find: scan a codebase for LLM calls whose output is a decision. Read-only
 * over a repo path; safe to run alongside anything else.
 */
export const jevPipelineFindTool = (config: PipelineConfig) =>
  defineTool({
    name: 'jev_pipeline_find',
    description:
      'Scan a codebase for LLM calls whose output is a DECISION (classify, route, yes/no, ' +
      'pick-one, rate) rather than text — the places where Jev / TypeSafe System One could ' +
      'replace or pre-screen a generative model. Returns each hit with file:line, why it was ' +
      'flagged, and the likely primitive (choice/score/noul). Read-only; no API calls.',
    parameters: {
      repo: {
        type: 'string',
        required: true,
        description: 'Repository path to scan, relative to the workspace root.',
      },
      min_score: {
        type: 'number',
        description: 'Minimum decision score to report (default 1; lower is noisier).',
      },
    },
    output: { schema: OUTPUT_SCHEMA, render, presentationMeta: summary('jev_pipeline_find') },
    execute: async (args) => {
      const typed = args as { repo: string; min_score?: number }
      const argv = ['find', typed.repo, '--min-score', String(typed.min_score ?? 1)]
      return execPipeline(config, argv)
    },
  })

/**
 * run: the full offline chain — find + fit + draft + lint. Writes candidate
 * state into the workdir, so it is NOT concurrency-safe.
 */
export const jevPipelineRunTool = (config: PipelineConfig) =>
  defineTool({
    name: 'jev_pipeline_run',
    description:
      'Run the full offline Jev pipeline over a repo: find decision-shaped LLM calls, fit-check ' +
      'each one (go / go-with-guards / no-go), draft a typed Choice/Score/Noul question from a ' +
      'field-tested pattern, and lint the draft against known question-design rules. No API ' +
      'calls; needs the upstream tool repos synced once (python3 -m jev_pipeline tools-sync).',
    parameters: {
      repo: {
        type: 'string',
        required: true,
        description: 'Repository path to analyze.',
      },
      min_score: {
        type: 'number',
        description: 'Minimum decision score for find (default 1).',
      },
    },
    output: { schema: OUTPUT_SCHEMA, render, presentationMeta: summary('jev_pipeline_run') },
    execute: async (args) => {
      const typed = args as { repo: string; min_score?: number }
      const argv = ['run', typed.repo, '--min-score', String(typed.min_score ?? 1)]
      return execPipeline(config, argv)
    },
  })

/**
 * cascade: act/pass/escalate plan over logged scores. Pure computation.
 */
export const jevPipelineCascadeTool = (config: PipelineConfig) =>
  defineTool({
    name: 'jev_pipeline_cascade',
    description:
      'Turn logged Jev scores into an act / pass / escalate plan using the two-band policy: ' +
      'act on the top band, pass the bottom, and treat the middle band — and any low-confidence ' +
      'top answer — as an explicit escalation branch to a System Two model or a human. ' +
      'Input is a JSONL file of {id, score, confidence?} rows.',
    parameters: {
      file: {
        type: 'string',
        required: true,
        description: 'Path to a scores JSONL file.',
      },
    },
    output: { schema: OUTPUT_SCHEMA, render, presentationMeta: summary('jev_pipeline_cascade') },
    execute: async (args) => {
      const typed = args as { file: string }
      return execPipeline(config, ['cascade', typed.file])
    },
  })
