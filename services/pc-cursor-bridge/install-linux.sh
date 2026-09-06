#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
INSTALL_DIR="${INSTALL_DIR:-$HOME/.local/share/pandamonium/pc-cursor-bridge}"
TOKEN_FILE="${JARVIS_CURSOR_BRIDGE_TOKEN_FILE:-$HOME/.config/jarvis/cursor-bridge-token}"
PROJECTS_ROOT="${JARVIS_CURSOR_PROJECTS_ROOT:-$HOME/.cursor/projects}"
HOST="${JARVIS_CURSOR_BRIDGE_HOST:-0.0.0.0}"
PORT="${JARVIS_CURSOR_BRIDGE_PORT:-8051}"

mkdir -p "$INSTALL_DIR" "$(dirname "$TOKEN_FILE")"
cp "$ROOT/services/pc-cursor-bridge/pc_cursor_bridge.py" "$INSTALL_DIR/"
cp "$ROOT/services/pc-cursor-bridge/transcript_io.py" "$INSTALL_DIR/"

if [[ ! -s "$TOKEN_FILE" ]]; then
  TOKEN_FILE="$TOKEN_FILE" python3 - <<'PY'
import secrets
from pathlib import Path
import os
path = Path(os.environ["TOKEN_FILE"])
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(secrets.token_urlsafe(32) + "\n", encoding="utf-8")
try:
    path.chmod(0o600)
except OSError:
    pass
print(path.read_text(encoding="utf-8").strip())
PY
fi

export JARVIS_CURSOR_BRIDGE_ALLOW_LAN="${JARVIS_CURSOR_BRIDGE_ALLOW_LAN:-1}"
export JARVIS_CURSOR_BRIDGE_HOST="$HOST"
export JARVIS_CURSOR_BRIDGE_PORT="$PORT"
export JARVIS_CURSOR_BRIDGE_HOSTS="$HOST"
export JARVIS_CURSOR_BRIDGE_TOKEN_FILE="$TOKEN_FILE"
export JARVIS_CURSOR_PROJECTS_ROOT="$PROJECTS_ROOT"

echo "Starting PC Cursor bridge on http://${HOST}:${PORT}"
echo "Projects root: $PROJECTS_ROOT"
echo "Token file: $TOKEN_FILE"
cd "$INSTALL_DIR"
exec python3 pc_cursor_bridge.py
