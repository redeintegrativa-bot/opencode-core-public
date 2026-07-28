#!/bin/bash
# Sync workflow between opencode-core and project repos
# Usage: ./sync-repos.sh [target_project_path]

set -e

CORE_PATH="/root/opencode-core"
TARGET="${1:-.}"

echo "=== OpenCode Core Sync ==="
echo "Source: $CORE_PATH"
echo "Target: $TARGET"

# Sync providers
echo ""
echo "[1/4] Syncing providers..."
if [ -d "$CORE_PATH/providers" ]; then
    rsync -av --progress "$CORE_PATH/providers/" "$TARGET/providers/" 2>/dev/null || \
    cp -r "$CORE_PATH/providers/" "$TARGET/"
    echo "  ✓ Providers synced"
fi

# Sync services
echo ""
echo "[2/4] Syncing services..."
if [ -d "$CORE_PATH/services" ]; then
    rsync -av --progress "$CORE_PATH/services/" "$TARGET/services/" 2>/dev/null || \
    cp -r "$CORE_PATH/services/" "$TARGET/"
    echo "  ✓ Services synced"
fi

# Sync agents
echo ""
echo "[3/4] Syncing agents..."
if [ -d "$CORE_PATH/agents" ]; then
    rsync -av --progress "$CORE_PATH/agents/" "$TARGET/agents/" 2>/dev/null || \
    cp -r "$CORE_PATH/agents/" "$TARGET/"
    echo "  ✓ Agents synced"
fi

# Sync skills
echo ""
echo "[4/4] Syncing skills..."
if [ -d "$CORE_PATH/skills" ]; then
    rsync -av --progress "$CORE_PATH/skills/" "$TARGET/skills/" 2>/dev/null || \
    cp -r "$CORE_PATH/skills/" "$TARGET/"
    echo "  ✓ Skills synced"
fi

echo ""
echo "=== Sync Complete ==="
echo "Components synced from opencode-core to $TARGET"
