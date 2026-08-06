/** @jsxImportSource @opentui/solid */
import { readFileSync, existsSync } from "node:fs"
import { join } from "node:path"
import { homedir } from "node:os"
import { type JSX } from "@opentui/solid"
import type { TuiPlugin, TuiPluginModule, TuiSlotPlugin } from "@opencode-ai/plugin/tui"

const BASE = join(homedir(), ".config", "opencode")
const STATE = join(BASE, "state")

type File = { status: string; detail: string }

function lastLine(file: string): string | null {
  if (!existsSync(file)) return null
  try {
    const text = readFileSync(file, "utf8")
    const lines = text.split("\n").filter(Boolean)
    return lines.length ? lines[lines.length - 1] : null
  } catch {
    return null
  }
}

function readJson(file: string): Record<string, unknown> | null {
  if (!existsSync(file)) return null
  try {
    return JSON.parse(readFileSync(file, "utf8"))
  } catch {
    return null
  }
}

function autoSync(): File {
  const line = lastLine(join(STATE, "auto-sync.jsonl"))
  if (!line) return { status: "off", detail: "sem histórico" }
  try {
    const e = JSON.parse(line)
    const action = e.action || "?"
    const result = e.result || "?"
    const detail = e.out || e.detail || e.message || ""
    const time = e.ts ? new Date(e.ts).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }) : ""
    return {
      status: result === "ok" ? "ok" : "warn",
      detail: `${action} ${result}${time ? " · " + time : ""}${detail ? "\n" + String(detail).slice(0, 40) : ""}`,
    }
  } catch {
    return { status: "off", detail: "log ilegível" }
  }
}

function updateCheck(): File {
  const alert = readJson(join(STATE, "update-alert.json"))
  if (alert && alert.has_update !== undefined) {
    return {
      status: alert.has_update ? "warn" : "ok",
      detail: alert.has_update ? `atualização ${alert.remote}` : "em dia",
    }
  }
  const last = readJson(join(STATE, "update-check.json"))
  if (!last) return { status: "off", detail: "nunca rodou" }
  const time = last.last ? new Date(last.last as string).toLocaleDateString("pt-BR") : ""
  return { status: "ok", detail: `verificado ${time}` }
}

function services(): File {
  const features = readJson(join(BASE, "features.json")) || {}
  const on = (k: string) => features[k] === true
  const parts = [
    on("network_watch") ? "network" : null,
    on("update_check") ? "update" : null,
  ].filter(Boolean)
  return {
    status: parts.length ? "ok" : "off",
    detail: parts.length ? parts.join(", ") : "nenhum serviço",
  }
}

function memory(): File {
  const recovery = readJson(join(STATE, "session-recovery.json"))
  if (!recovery) return { status: "off", detail: "sem recuperação" }
  const mem = recovery.memory as Record<string, unknown> | undefined
  const last = mem?.last_session ? String(mem.last_session).slice(0, 42) : ""
  return {
    status: mem ? "ok" : "warn",
    detail: last || "memória ativa",
  }
}

function dot(color: JSX.CSSProperties | undefined, status: string) {
  const c = status === "ok" ? "#2ecc71" : status === "warn" ? "#e67e22" : "#888"
  return <text fg={c}>●</text>
}

function row(label: string, file: File, skin: Record<string, unknown>) {
  return (
    <box flexDirection="row" gap={1}>
      {dot(undefined, file.status)}
      <box flexDirection="column">
        <text fg={skin.text as string}>{label}</text>
        <text fg={skin.muted as string}>{file.detail}</text>
      </box>
    </box>
  )
}

const statusSlot = (order: number): TuiSlotPlugin => ({
  order,
  slots: {
    sidebar_content(ctx, value) {
      const theme = ctx.theme.current as unknown as Record<string, unknown>
      const text = (theme.text as string) ?? "#e6e6e6"
      const muted = (theme.textMuted as string) ?? "#8a8a8a"
      const border = (theme.border as string) ?? "#444"
      const panel = (theme.backgroundPanel as string) ?? "#1d1d1d"
      const accent = (theme.primary as string) ?? "#5f87ff"
      const skin = { text, muted, border, panel, accent }

      return (
        <box
          border
          borderColor={skin.border}
          backgroundColor={skin.panel}
          paddingTop={1}
          paddingBottom={1}
          paddingLeft={2}
          paddingRight={2}
          flexDirection="column"
          gap={1}
        >
          <text fg={skin.accent}>
            <b>Status</b>
          </text>
          {row("Auto-sync", autoSync(), skin)}
          {row("Update", updateCheck(), skin)}
          {row("Serviços", services(), skin)}
          {row("Memória", memory(), skin)}
        </box>
      )
    },
  },
})

const tui: TuiPlugin = async (api, options) => {
  const order = typeof options?.order === "number" ? options.order : 450
  api.slots.register(statusSlot(order))
}

const plugin: TuiPluginModule & { id: string } = {
  id: "status-panel",
  tui,
}

export default plugin
