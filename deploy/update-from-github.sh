#!/usr/bin/env bash
# Pull the latest MADPANDA3D/Pandamonium release (or a given ref) into this
# tree. GitLab labs247 stays origin. Personal overlay (.env, Proxmox compose,
# Unsloth client, systemd unit) is restored after the reset.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export OVERLAY_LIST="$ROOT/deploy/overlay-paths.txt"

if ! git -C "$ROOT" remote get-url github >/dev/null 2>&1; then
  git -C "$ROOT" remote add github https://github.com/MADPANDA3D/Pandamonium.git
fi
git -C "$ROOT" remote set-url --push github no_push

exec /mnt/dev-env/tools/scripts/update-ingested-from-github.sh "$ROOT" "${1:-}"
