// OpenCode - Canal unificado de notificacoes
// Dispara em paralelo (cada canal independente, com flag ao vivo):
//   1. Toast na TUI  (se ui_ux_toasts)
//   2. Som no terminal (se toast_sounds)  - melodia distinta por tipo
//   3. Toast do Windows silencioso (se windows_toast)
// As flags sao relidas de features.json a cada chamada (toggle via dashboard
// vale na hora, sem reiniciar o opencode).
import { execFile } from "node:child_process"
import { existsSync, readFileSync } from "node:fs"
import { join } from "node:path"
import { homedir } from "node:os"

const BASE = join(homedir(), ".config", "opencode")
const FEATURES_FILE = join(BASE, "features.json")
const SCRIPT_DIR = join(BASE, "scripts")
const TOAST_PS1 = join(SCRIPT_DIR, "windows-toast.ps1")
const SOUND_PS1 = join(SCRIPT_DIR, "play-sound.ps1")
const THEME_FILE = join(BASE, "state", "sound-theme.txt")

const PATTERNS = {
  success: "success",
  info: "info",
  memory: "memory",
  warning: "warning",
  error: "error",
  update: "update",
  sync: "sync",
}

// Prioridade dos sons (maior = mais importante). Dentro da janela de debounce,
// um som so toca se for mais importante que o ultimo que tocou.
const PRIORITY = { error: 6, warning: 5, success: 4, sync: 3, update: 2, memory: 1, info: 0 }

let lastSoundAt = 0
let lastSoundPriority = -1

function readFeatures() {
  try {
    if (existsSync(FEATURES_FILE)) return JSON.parse(readFileSync(FEATURES_FILE, "utf8"))
  } catch {}
  return {}
}

function enabled(key) {
  return readFeatures()[key] !== false
}

function spawn(args) {
  try {
    execFile(
      "powershell",
      ["-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", ...args],
      { windowsHide: true },
    )
  } catch {}
}

export function tuiToast(client, title, message, variant = "info") {
  if (!enabled("ui_ux_toasts")) return
  if (!client?.tui?.showToast) return
  try {
    client.tui.showToast({ body: { title, message, variant } })
  } catch {}
}

function readTheme() {
  try {
    if (existsSync(THEME_FILE)) {
      const t = readFileSync(THEME_FILE, "utf8").trim()
      if (t) return t
    }
  } catch {}
  return "default"
}

function soundCooldown() {
  const ms = readFeatures()["sound_cooldown_ms"]
  return typeof ms === "number" && ms > 0 ? ms : 1500
}

export function terminalSound(variant = "info") {
  if (!enabled("toast_sounds")) return
  if (!existsSync(SOUND_PS1)) return
  const pattern = PATTERNS[variant] || "info"
  const priority = PRIORITY[pattern] ?? 0
  const now = Date.now()
  if (now - lastSoundAt < soundCooldown() && priority <= lastSoundPriority) return
  lastSoundAt = now
  lastSoundPriority = priority
  spawn(["-File", SOUND_PS1, "-Pattern", pattern, "-Theme", readTheme()])
}

export function windowsToast(title, message) {
  if (!enabled("windows_toast")) return
  if (!existsSync(TOAST_PS1)) return
  spawn(["-File", TOAST_PS1, "-Title", title, "-Message", message])
}

export function notify(client, title, message, variant = "info") {
  tuiToast(client, title, message, variant)
  terminalSound(variant)
  windowsToast(title, message)
}

