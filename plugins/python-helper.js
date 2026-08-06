import { execFile } from "node:child_process"
import { existsSync } from "node:fs"
import { join } from "node:path"
import { homedir, platform } from "node:os"

const isWindows = platform() === "win32"

function probe(cmd, args = []) {
  return new Promise((resolve) => {
    execFile(cmd, args, { timeout: 8000 }, (err) => resolve(!err))
  })
}

function windowsPythonCandidates() {
  const roots = [
    process.env.LOCALAPPDATA ? join(process.env.LOCALAPPDATA, "Programs", "Python") : null,
    process.env.ProgramFiles ? join(process.env.ProgramFiles, "Python") : null,
    process.env.USERPROFILE ? join(process.env.USERPROFILE, "AppData", "Local", "Programs", "Python") : null,
  ].filter(Boolean)

  const out = []
  for (const root of roots) {
    for (const dir of ["Python313", "Python312", "Python311", "Python310", "Python39", "Python38"]) {
      const exe = join(root, dir, "python.exe")
      if (existsSync(exe)) out.push(exe)
    }
  }
  return out
}

let cached = null

export async function resolvePython() {
  if (cached) return cached

  const candidates = []
  if (process.env.OPENCODE_PYTHON) candidates.push(process.env.OPENCODE_PYTHON)
  if (isWindows) {
    candidates.push("python", "py", ...windowsPythonCandidates())
  } else {
    candidates.push("python3", "python")
  }

  for (const candidate of candidates) {
    const probeArgs = candidate === "py" ? ["-3", "--version"] : ["--version"]
    if (await probe(candidate, probeArgs)) {
      cached = candidate
      return candidate
    }
  }
  return null
}

export async function runPy(args, options = {}) {
  const py = await resolvePython()
  if (!py) {
    return { ok: false, stdout: "", stderr: "python not found", code: 1 }
  }
  const finalArgs = py === "py" ? ["-3", ...args] : args
  return new Promise((resolve) => {
    execFile(
      py,
      finalArgs,
      { cwd: options.cwd, timeout: options.timeout || 60000, windowsHide: true, maxBuffer: 4 * 1024 * 1024 },
      (err, stdout, stderr) => {
        resolve({
          ok: !err,
          stdout: String(stdout || ""),
          stderr: String(stderr || ""),
          code: err ? (err.code || 1) : 0,
        })
      },
    )
  })
}
