# Source this file before using unsloth/opencode in the Cursor terminal.
# HOME is redirected because /home/labsadmin is read-only in this environment.
export HOME="/mnt/dev-env"
export PATH="/mnt/dev-env/.opencode/bin:/mnt/dev-env/.local/bin:${PATH}"

_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
_PROJECT_ROOT="$(cd "$_SCRIPT_DIR/.." && pwd)"
if [[ -f "$_PROJECT_ROOT/.env" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "$_PROJECT_ROOT/.env"
  set +a
fi

export UNSLOTH_NODE="${UNSLOTH_NODE:-m1}"

# Project OpenCode config (M1 + M2 providers). Requires UNSLOTH_M1_API_KEY / UNSLOTH_M2_API_KEY in .env.
export OPENCODE_CONFIG="${OPENCODE_CONFIG:-$_PROJECT_ROOT/opencode.json}"
