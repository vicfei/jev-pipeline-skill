/**
 * Bridge to the jev_pipeline CLI (Python, stdlib only).
 *
 * The plugin holds no pipeline logic: every tool shells out to
 * `python3 -m jev_pipeline` and returns its output, so the Python package and
 * this adapter can never disagree about behavior. The only logic here is the
 * guard for "the CLI is not installed" — turned into an actionable error
 * instead of a stack trace the model cannot use.
 */

import { spawn } from 'node:child_process'

export interface PipelineConfig {
  /** Python interpreter that has jev_pipeline importable. Default 'python3'. */
  readonly python: string
  /** --out workdir passed to every step. Default 'jev-pipeline-out'. */
  readonly out: string
}

export const DEFAULT_CONFIG: PipelineConfig = { python: 'python3', out: 'jev-pipeline-out' }

export const INSTALL_HINT =
  'Install the CLI first: pip install git+https://github.com/vicfei/jev-pipeline-skill ' +
  '(stdlib only), then run its tools-sync once: python3 -m jev_pipeline tools-sync'

export class PipelineNotInstalledError extends Error {
  constructor(detail: string) {
    super(`jev_pipeline CLI is not usable with the configured interpreter. ${detail}\n${INSTALL_HINT}`)
    this.name = 'PipelineNotInstalledError'
  }
}

export function normalizeConfig(input: unknown): PipelineConfig {
  const raw = (typeof input === 'object' && input !== null ? input : {}) as Partial<PipelineConfig>
  return {
    python: typeof raw.python === 'string' && raw.python ? raw.python : DEFAULT_CONFIG.python,
    out: typeof raw.out === 'string' && raw.out ? raw.out : DEFAULT_CONFIG.out,
  }
}

export interface ExecResult {
  readonly ok: boolean
  readonly exitCode?: number
  readonly output: string
}

const TIMEOUT_MS = 300_000

export async function execPipeline(
  config: PipelineConfig,
  args: string[],
): Promise<ExecResult> {
  const full = [ '-m', 'jev_pipeline', ...args, '--out', config.out ]
  return new Promise<ExecResult>((resolve) => {
    const child = spawn(config.python, full, { stdio: ['ignore', 'pipe', 'pipe'] })
    let stdout = ''
    let stderr = ''
    const timer = setTimeout(() => child.kill('SIGKILL'), TIMEOUT_MS)
    child.stdout.on('data', (chunk: Buffer) => { stdout += chunk.toString() })
    child.stderr.on('data', (chunk: Buffer) => { stderr += chunk.toString() })
    child.on('error', (err: NodeJS.ErrnoException) => {
      clearTimeout(timer)
      throw new PipelineNotInstalledError(String(err))
    })
    child.on('close', (code) => {
      clearTimeout(timer)
      const notInstalled = /No module named jev_pipeline/.test(stderr)
      if (notInstalled) throw new PipelineNotInstalledError(stderr.trim())
      resolve({
        ok: code === 0,
        ...(code === null ? {} : { exitCode: code }),
        output: stdout.trim() + (stderr.trim() ? `\n[stderr]\n${stderr.trim()}` : ''),
      })
    })
  })
}
