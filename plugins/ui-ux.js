import {
  existsSync,
  mkdirSync,
  readFileSync,
  writeFileSync,
} from "node:fs"
import { join } from "node:path"
import { homedir } from "node:os"
import { notify } from "./notify.js"

const BASE = join(homedir(), ".config", "opencode")
const FEATURES_FILE = join(BASE, "features.json")
const STATE_DIR = join(BASE, "state")
const LAST_TOAST_FILE = join(STATE_DIR, "ui-ux-last-toast.json")

const MIN_TOAST_INTERVAL_MS = 30 * 1000
const ACTIVITY_WINDOW_MS = 60 * 1000

function isFeatureEnabled() {
  try {
    if (!existsSync(FEATURES_FILE)) return true
    const data = JSON.parse(readFileSync(FEATURES_FILE, "utf8"))
    return data["ui_ux_toasts"] !== false
  } catch {
    return true
  }
}

function readLastToast() {
  try {
    if (!existsSync(LAST_TOAST_FILE)) return 0
    return parseInt(readFileSync(LAST_TOAST_FILE, "utf8").trim(), 10) || 0
  } catch {
    return 0
  }
}

function writeLastToast(ts) {
  try {
    mkdirSync(STATE_DIR, { recursive: true })
    writeFileSync(LAST_TOAST_FILE, String(ts))
  } catch {}
}

function toast(client, title, message, variant = "info") {
  if (!isFeatureEnabled()) return
  const now = Date.now()
  if (now - readLastToast() < MIN_TOAST_INTERVAL_MS) return
  writeLastToast(now)
  notify(client, title, message, variant)
}

export const UiUx = async ({ client }) => {
  let lastActivityAt = 0

  return {
    event: async ({ event }) => {
      const type = event?.type
      if (!type) return

      if (type === "message.updated" || type === "session.status") {
        lastActivityAt = Date.now()
      }

      if (type === "session.idle") {
        const now = Date.now()
        if (now - lastActivityAt <= ACTIVITY_WINDOW_MS) {
          toast(client, "Tarefa concluída", "Resposta finalizada no opencode.", "success")
        }
        lastActivityAt = 0
      }

      if (type === "session.error") {
        toast(client, "Erro na sessão", "Algo falhou no opencode. Veja os detalhes no chat.", "error")
      }

      if (type === "command.executed") {
        const name = event.properties?.name || event.data?.name || event.properties?.command || ""
        if (String(name).includes("salvar") || String(name).includes("remember")) {
          toast(client, "Memória salva", "Sessão registrada na memória persistente.", "memory")
        }
      }
    },

    "tool.execute.after": async (input, output) => {
      if (!output?.error) return
      const tool = input?.tool || "ferramenta"
      toast(client, `Erro em ${tool}`, "Ferramenta falhou durante a execução.", "warning")
    },
  }
}
