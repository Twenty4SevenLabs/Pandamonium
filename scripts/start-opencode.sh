#!/usr/bin/env bash
# Launch OpenCode with M1 + M2 GPU Unsloth providers (project opencode.json).
#
# Usage (from repo root):
#   ./scripts/start-opencode.sh              # OpenCode TUI, pick model via /model
#   ./scripts/start-opencode.sh run "task"   # one-shot
#
# Models appear under providers:
#   unsloth-m1  → 192.168.1.2:8888  (Qwen3.5-9B, Qwen3-14B, FLUX)
#   unsloth-m2  → 192.168.1.191:8888 (Qwen2.5-Coder-7B, Qwen3.5-9B)
#
# Requires in .env: UNSLOTH_M1_API_KEY, UNSLOTH_M2_API_KEY
#
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=/dev/null
source "$ROOT/scripts/opencode-env.sh"
cd "$ROOT"

if [[ -z "${UNSLOTH_M1_API_KEY:-}" || -z "${UNSLOTH_M2_API_KEY:-}" ]]; then
  echo "Missing UNSLOTH_M1_API_KEY or UNSLOTH_M2_API_KEY in .env" >&2
  exit 1
fi

if [[ -n "${PANDAMONIUM_UNSLOTH_WAKE_URL:-}" ]]; then
  curl -sf -X POST "${PANDAMONIUM_UNSLOTH_WAKE_URL}" >/dev/null 2>&1 || true
fi

echo "OpenCode → M1 + M2 Unsloth (config: ${OPENCODE_CONFIG})" >&2
echo "Use /model to switch between unsloth-m1 and unsloth-m2 models." >&2
exec opencode "$@"
