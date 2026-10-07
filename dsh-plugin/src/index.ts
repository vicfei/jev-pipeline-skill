/**
 * jev-pipeline-dsh — the jev_pipeline workflow as DeepSeek Harness tools.
 *
 * One Cordis plugin, three model-visible tools, zero network egress of its
 * own: every tool shells out to the local jev_pipeline CLI (Python, stdlib
 * only) inside this workspace. Nothing runs unless the model calls a tool,
 * and the CLI itself never calls an API.
 *
 * Adapter structure follows the pattern of PerryLink/jevcore's DSH package
 * (Apache-2.0) — see NOTICE. No upstream code is copied.
 */

import type { Context } from '@deepseek-ai/cordis'
import { execPipeline, normalizeConfig, type PipelineConfig } from './exec.js'
import {
  jevPipelineCascadeTool,
  jevPipelineFindTool,
  jevPipelineRunTool,
} from './tools.js'

/** Plugin name, also the service identity in the host config. */
export const name = 'jev-pipeline'

/** Only the host service this plugin cannot work without. */
export const inject = ['tools']

export type { PipelineConfig } from './exec.js'
export { PipelineNotInstalledError, execPipeline, normalizeConfig } from './exec.js'
export { jevPipelineCascadeTool, jevPipelineFindTool, jevPipelineRunTool } from './tools.js'

/**
 * The configuration schema, as Cordis consumes it.
 *
 * Cordis validates a plugin's config through the Standard Schema protocol
 * before the plugin starts, so `Config` must expose `~standard.validate`.
 * This minimal implementation normalizes { python?, out? } and accepts
 * everything else as defaults — validation cannot reject, only normalize.
 */
export const Config = {
  '~standard': {
    version: 1,
    vendor: 'jev-pipeline-dsh',
    validate: (value: unknown) => ({ value: normalizeConfig(value) }),
  },
} as const

export function apply(ctx: Context, input?: unknown): void {
  const config = normalizeConfig(input)
  const tools = (ctx as unknown as { tools: { register(definition: unknown): () => void } }).tools
  for (const definition of [
    jevPipelineFindTool(config),
    jevPipelineRunTool(config),
    jevPipelineCascadeTool(config),
  ]) {
    ctx.effect(() => tools.register(definition))
  }
}
