import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs"
import { join } from "node:path"
import { homedir } from "node:os"
import { runPy } from "./python-helper.js"

const FEATURE = "update_check"
const FEATURES_FILE = join(homedir(), ".config", "opencode", "features.json")

function isFeatureEnabled(feature) {
  try {
    if (!existsSync(FEATURES_FILE)) return false
    const data = JSON.parse(readFileSync(FEATURES_FILE, "utf8"))
    return data[feature] === true
  } catch {
    return false
  }
}

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

  runPy([`${checker}`, "--json"], { cwd: repoDir }).then((proc) => {
    const out = proc.stdout.trim()
    let data = null
    try {
      data = JSON.parse(out.split("\n").pop() || "")
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
    }
  })
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
