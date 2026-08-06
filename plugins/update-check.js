import { spawn } from "node:child_process"
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs"
import { join } from "node:path"
import { homedir } from "node:os"
import { isFeatureEnabled } from "./features.js"

const FEATURE = "update_check"
const STATE_DIR = join(homedir(), ".config", "opencode", "state")
const STATE_FILE = join(STATE_DIR, "update-check.json")
const ALERT_FILE = join(STATE_DIR, "update-alert.json")
const MIN_INTERVAL_MS = 6 * 60 * 60 * 1000

function candidates() {
  return [
    process.env.OPENCODE_CORE_DIR,
    join(homedir(), "opencode-core"),
    join(homedir(), "opencode-core-public"),
  ].filter(Boolean)
}

function findRepo() {
  for (const dir of candidates()) {
    if (existsSync(join(dir, "VERSION"))) return dir
  }
  return null
}

function ensureState() {
  mkdirSync(STATE_DIR, { recursive: true })
}

function readLast() {
  try {
    return JSON.parse(readFileSync(STATE_FILE, "utf8"))
  } catch {
    return null
  }
}

function writeLast(data) {
  ensureState()
  writeFileSync(STATE_FILE, JSON.stringify(data, null, 2), "utf8")
}

function shouldRun(last) {
  if (!last || !last.last) return true
  return Date.now() - new Date(last.last).getTime() >= MIN_INTERVAL_MS
}

function runCheck(ctx, repoDir, reason) {
  const checker = join(repoDir, "scripts", "check-update.py")
  if (!existsSync(checker)) return

  const proc = spawn("python", [checker, "--json"], {
    cwd: repoDir,
    windowsHide: true,
  })
  let out = ""
  proc.stdout.on("data", (d) => { out += d })
  proc.stderr.on("data", (d) => { out += d })
  proc.on("close", (code) => {
    let data = null
    try {
      data = JSON.parse(out.trim().split("\n").pop() || "")
    } catch {}

    if (data && data.has_update) {
      const alert = {
        ts: new Date().toISOString(),
        local: data.local,
        remote: data.remote,
        changelog: String(data.changelog || ""),
        repo: repoDir,
        applied: false,
        presented: false,
      }
      writeFileSync(ALERT_FILE, JSON.stringify(alert, null, 2), "utf8")

      if (ctx.client && ctx.client.app) {
        ctx.client.app.log({
          body: {
            service: "update-check",
            level: "info",
            message: `Novidades disponiveis: ${data.local} -> ${data.remote}. Aguardando revisao do usuario (nao aplicado).`,
            extra: { changelog: alert.changelog.slice(0, 2000) },
          },
        })
      }
    }
  })
}

export function getPendingAlert() {
  try {
    if (!existsSync(ALERT_FILE)) return null
    const a = JSON.parse(readFileSync(ALERT_FILE, "utf8"))
    if (a.applied) return null
    return a
  } catch {
    return null
  }
}

export function markAlertApplied() {
  try {
    const a = JSON.parse(readFileSync(ALERT_FILE, "utf8"))
    a.applied = true
    writeFileSync(ALERT_FILE, JSON.stringify(a, null, 2), "utf8")
  } catch {}
}

export function clearAlert() {
  try {
    writeFileSync(ALERT_FILE, JSON.stringify({ applied: true, cleared: true, ts: new Date().toISOString() }, null, 2), "utf8")
  } catch {}
}

export const UpdateCheck = async (ctx) => {
  ensureState()
  if (!isFeatureEnabled(FEATURE)) return {}

  return {
    event: async ({ event }) => {
      if (event.type !== "session.idle") return
      const last = readLast()
      if (!shouldRun(last)) return
      const repoDir = findRepo()
      if (!repoDir) return
      writeLast({ last: new Date().toISOString(), repo: repoDir })
      runCheck(ctx, repoDir, "idle")
    },
    "chat.message": async (input) => {
      const last = readLast()
      if (!shouldRun(last)) return
      const repoDir = findRepo()
      if (!repoDir) return
      writeLast({ last: new Date().toISOString(), repo: repoDir })
      runCheck(ctx, repoDir, `nova mensagem (${input?.agent || "?"})`)
    },
  }
}
