import { spawn } from "node:child_process"
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs"
import { join } from "node:path"
import { homedir } from "node:os"

const FEATURE = "network_watch"
const FEATURES_FILE = join(homedir(), ".config", "opencode", "features.json")
const BASE = join(homedir(), "network-dashboard")
const SCANNER = join(BASE, "scanner.py")
const STATE_FILE = join(BASE, "data", "last-watch.json")
const MIN_INTERVAL_MS = 15 * 60 * 1000

function isFeatureEnabled(feature) {
  try {
    if (!existsSync(FEATURES_FILE)) return false
    const data = JSON.parse(readFileSync(FEATURES_FILE, "utf8"))
    return data[feature] === true
  } catch {
    return false
  }
}

function ensureState() {
  mkdirSync(join(BASE, "data"), { recursive: true })
}

function readLastWatch() {
  try {
    return JSON.parse(readFileSync(STATE_FILE, "utf8"))
  } catch {
    return null
  }
}

function writeLastWatch(ts) {
  ensureState()
  writeFileSync(STATE_FILE, JSON.stringify({ last: ts }, null, 2), "utf8")
}

function shouldRun() {
  const last = readLastWatch()
  if (!last || !last.last) return true
  return Date.now() - new Date(last.last).getTime() >= MIN_INTERVAL_MS
}

function runWatch(ctx, reason) {
  if (!shouldRun()) return
  writeLastWatch(new Date().toISOString())

  const proc = spawn("python", [SCANNER, "--watch"], {
    cwd: BASE,
    windowsHide: true,
  })
  let out = ""
  proc.stdout.on("data", (d) => { out += d })
  proc.stderr.on("data", (d) => { out += d })
  proc.on("close", (code) => {
    let summary = null
    try {
      const jsonStart = out.indexOf("{")
      if (jsonStart >= 0) {
        summary = JSON.parse(out.slice(jsonStart))
      }
    } catch {}

    if (ctx.client && ctx.client.app) {
      ctx.client.app.log({
        body: {
          service: "network-watch",
          level: summary ? "info" : "warn",
          message: `Scan de rede (${reason})${code === 0 ? "" : " - erro"}`,
          extra: {
            code,
            summary: summary || { raw: out.slice(-1000) },
          },
        },
      })
    }
  })
}

export const NetworkWatch = async (ctx) => {
  ensureState()
  if (!isFeatureEnabled(FEATURE)) return {}

  return {
    event: async ({ event }) => {
      const props = event.properties || event.data || {}
      if (event.type === "session.idle" || event.type === "session.updated") {
        runWatch(ctx, "idle")
      }
    },
    "chat.message": async (input) => {
      runWatch(ctx, `nova mensagem (${input?.agent || "?"})`)
    },
  }
}
