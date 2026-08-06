import { readFileSync, existsSync } from "node:fs"
import { join } from "node:path"
import { homedir } from "node:os"

const FEATURES_FILE = join(homedir(), ".config", "opencode", "features.json")

export function isFeatureEnabled(feature) {
  try {
    if (!existsSync(FEATURES_FILE)) return false
    const data = JSON.parse(readFileSync(FEATURES_FILE, "utf8"))
    return data[feature] === true
  } catch {
    return false
  }
}
