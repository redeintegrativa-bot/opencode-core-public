import {
  appendFileSync,
  existsSync,
  mkdirSync,
  readFileSync,
  writeFileSync,
} from "node:fs"
import { join } from "node:path"
import { homedir } from "node:os"
import { runPy } from "./python-helper.js"

const BASE = join(homedir(), ".config", "opencode")
const STATE_DIR = join(BASE, "state")
const SESSION_LOG = join(STATE_DIR, "session-history.jsonl")
const FALLBACK_JSONL = join(STATE_DIR, "fallback-log.jsonl")
const KNOWLEDGE_LOG = join(STATE_DIR, "knowledge.jsonl")
const RECOVERY_FILE = join(STATE_DIR, "session-recovery.json")
const COUNTER_FILE = join(STATE_DIR, ".session-counter")
const LEGACY_FALLBACK = join(BASE, "fallback-log.json")
const EVOLVE_SCRIPT = join(BASE, "scripts", "evolve-agent.py")
const MEMORY_SCRIPT = join(BASE, "memory", "session.py")

const CHECK_INTERVAL = 10

const AGENT_NAMES = [
  "analyzer", "coder", "reviewer", "documenter", "orchestrator",
  "system_coordinator", "gui-super-expert",
]

function ensureDirs() {
  mkdirSync(STATE_DIR, { recursive: true })
}

function appendLine(file, obj) {
  ensureDirs()
  appendFileSync(file, JSON.stringify(obj) + "\n")
}

function readCounter() {
  try {
    return parseInt(readFileSync(COUNTER_FILE, "utf8").trim(), 10) || 0
  } catch {
    return 0
  }
}

function writeCounter(n) {
  ensureDirs()
  writeFileSync(COUNTER_FILE, String(n))
}

function extractKeywords(text) {
  if (!text) return []
  return AGENT_NAMES.filter((a) => text.toLowerCase().includes(a))
}

async function getMemoryStatus(ctx) {
  try {
    if (!existsSync(MEMORY_SCRIPT)) return null
    const cache = join(BASE, "state", "session-status.json")
    await runPy([`${MEMORY_SCRIPT}`, "status", "--short", "--quiet"])
    if (!existsSync(cache)) return null
    return JSON.parse(readFileSync(cache, "utf8"))
  } catch {
    return null
  }
}

function rebuildLegacyFallback() {
  if (!existsSync(FALLBACK_JSONL)) return
  const entries = []
  try {
    const lines = readFileSync(FALLBACK_JSONL, "utf8").split("\n").filter(Boolean)
    for (const line of lines.slice(-200)) {
      try {
        entries.push(JSON.parse(line))
      } catch {}
    }
  } catch {}
  const payload = { version: 1, entries, generated_at: new Date().toISOString() }
  try {
    writeFileSync(LEGACY_FALLBACK, JSON.stringify(payload, null, 2), "utf8")
  } catch {}
}

async function runEvolveCheck(ctx) {
  try {
    const proc = await runPy([`${EVOLVE_SCRIPT}`, "--check"])
    const out = String(proc.stdout || "").trim()
    appendLine(KNOWLEDGE_LOG, {
      type: "evolve_check",
      ts: new Date().toISOString(),
      suggestions: out.slice(0, 4000),
    })
  } catch {}
}

export const SelfImprovement = async (ctx) => {
  ensureDirs()
  return {
    event: async ({ event }) => {
      const props = event.properties || event.data || {}
      const now = new Date().toISOString()
      const sessionID = props.sessionID || props.id || null
      const directory = ctx.directory || ""

      if (event.type === "session.idle") {
        appendLine(SESSION_LOG, { type: "session", ts: now, sessionID, directory })
        try {
          const mem = await getMemoryStatus(ctx)
          const recovery = { lastSession: sessionID, ts: now, directory, resumed: false }
          if (mem) recovery.memory = mem
          writeFileSync(
            RECOVERY_FILE,
            JSON.stringify(recovery, null, 2),
            "utf8"
          )
        } catch {}

        const count = readCounter() + 1
        writeCounter(count)
        if (count >= CHECK_INTERVAL) {
          writeCounter(0)
          rebuildLegacyFallback()
          await runEvolveCheck(ctx)
        }
      }

      if (event.type === "session.error") {
        const raw = props.error
        let errText = ""
        if (typeof raw === "string") errText = raw
        else if (raw && typeof raw === "object") {
          errText = raw.message || raw.error || raw.name || JSON.stringify(raw)
        } else if (raw != null) errText = String(raw)
        if (!errText || errText === "[object Object]") return
        appendLine(FALLBACK_JSONL, {
          type: "session_error",
          ts: now,
          sessionID,
          error: errText.slice(0, 500),
        })
      }
    },

    "tool.execute.after": async (input, output) => {
      const now = new Date().toISOString()
      const err = output?.error ? String(output.error) : null
      if (!err) return
      const tool = input?.tool || "unknown"
      const text = `${tool} ${err}`
      appendLine(FALLBACK_JSONL, {
        type: "tool_error",
        ts: now,
        tool,
        error: err.slice(0, 400),
        keywords: extractKeywords(text),
      })
    },
  }
}
