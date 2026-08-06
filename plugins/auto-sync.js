import { existsSync, readFileSync, writeFileSync, mkdirSync, appendFileSync } from "node:fs"
import { join } from "node:path"
import { homedir } from "node:os"
import { runPy } from "./python-helper.js"

const BASE = join(homedir(), ".config", "opencode")
const STATE_DIR = join(BASE, "state")
const SYNC_LOG = join(STATE_DIR, "auto-sync.jsonl")
const PENDING_FILE = join(STATE_DIR, "sync-pending.json")

const CORE_DIR = process.env.OPENCODE_CORE_DIR || join(homedir(), "opencode-core")
const SYNC_SCRIPT = join(CORE_DIR, "scripts", "sync-public.py")
const SETUP_PS1 = join(CORE_DIR, "setup.ps1")

function ensureState() {
  mkdirSync(STATE_DIR, { recursive: true })
}

function appendLog(entry) {
  try {
    ensureState()
    appendFileSync(SYNC_LOG, JSON.stringify(entry) + "\n")
  } catch {}
}

function readJson(file, fallback) {
  try {
    if (!existsSync(file)) return fallback
    return JSON.parse(readFileSync(file, "utf8"))
  } catch {
    return fallback
  }
}

function writePending(payload) {
  try {
    ensureState()
    writeFileSync(PENDING_FILE, JSON.stringify(payload, null, 2), "utf8")
  } catch {}
}

async function exec(ctx, cmd) {
  try {
    const proc = await ctx.$`${cmd}`
    return { ok: true, out: String(proc.stdout || "").trim() }
  } catch (e) {
    return { ok: false, out: String((e && e.stderr) || e).slice(0, 500) }
  }
}

async function runHead(ctx, repo) {
  const r = await exec(ctx, `git -C ${repo} rev-parse --short HEAD`)
  return r.ok ? r.out : null
}

async function isDirty(ctx, repo) {
  const r = await exec(ctx, `git -C ${repo} status --porcelain`)
  if (!r.ok) return true
  return r.out.split("\n").some((l) => l && !l.startsWith("??"))
}

async function autoPull(ctx) {
  const entry = { ts: new Date().toISOString(), action: "pull" }
  if (!existsSync(join(CORE_DIR, ".git"))) {
    entry.result = "skip-no-repo"
    appendLog(entry)
    return { pulled: false, changed: false }
  }
  const before = await runHead(ctx, CORE_DIR)
  if (await isDirty(ctx, CORE_DIR)) {
    entry.result = "skip-dirty"
    appendLog(entry)
    return { pulled: false, changed: false }
  }
  const pull = await exec(ctx, `git -C ${CORE_DIR} pull --ff-only`)
  if (!pull.ok) {
    entry.result = "fail"
    entry.detail = pull.out.slice(0, 200)
    appendLog(entry)
    return { pulled: false, changed: false }
  }
  const after = await runHead(ctx, CORE_DIR)
  entry.result = "ok"
  entry.before = before
  entry.after = after
  entry.changed = before !== after
  appendLog(entry)
  return { pulled: true, changed: before !== after }
}

async function autoRedeploy(ctx) {
  const entry = { ts: new Date().toISOString(), action: "redeploy" }
  if (!existsSync(SETUP_PS1)) {
    entry.result = "skip-no-setup"
    appendLog(entry)
    return false
  }
  const proc = await exec(
    ctx,
    `powershell -NoProfile -ExecutionPolicy Bypass -File ${SETUP_PS1} -Skills -Commands -Plugins -Memory -SkipUpdateCheck`
  )
  entry.result = proc.ok ? "ok" : "fail"
  entry.detail = proc.out.slice(-300)
  appendLog(entry)
  return proc.ok
}

async function autoStage(ctx, sessionID) {
  const entry = { ts: new Date().toISOString(), action: "stage", sessionID }
  if (!existsSync(SYNC_SCRIPT)) {
    entry.result = "skip-no-script"
    appendLog(entry)
    return
  }
  const proc = await runPy([`${SYNC_SCRIPT}`, "--stage"], { cwd: CORE_DIR })
  entry.result = proc.ok ? "ok" : "fail"
  entry.out = (proc.stdout + " " + proc.stderr).slice(0, 400)
  appendLog(entry)

  writePending({
    sessionID,
    ts: entry.ts,
    result: entry.result,
    message: (proc.stdout + " " + proc.stderr).slice(0, 400),
  })
}

export const AutoSync = async (ctx) => {
  ensureState()
  let lastStageSession = null

  return {
    event: async ({ event }) => {
      const props = event.properties || event.data || {}
      const sessionID = props.sessionID || props.id || null

      if (event.type === "session.created") {
        const { changed } = await autoPull(ctx)
        if (changed) {
          await autoRedeploy(ctx)
        }
      }

      if (event.type === "session.idle") {
        if (sessionID && sessionID === lastStageSession) return
        lastStageSession = sessionID
        await autoStage(ctx, sessionID)
      }
    },
  }
}
