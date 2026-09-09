#!/usr/bin/env bash
# Host-side Pandamonium updater for the pve-prod Docker Compose install.
#
# The in-container signed updater cannot rewrite the image. This script:
# 1. fetches MADPANDA3D tags
# 2. merges the newest tag into cursor-bridge and main (bridge files stay off main)
# 3. rebuilds the running compose stack when git APP_VERSION != container APP_VERSION
set -euo pipefail

ROOT="${PANDAMONIUM_ROOT:-/mnt/dev-env/projects/pandamonium}"
GIT_USER="${PANDAMONIUM_GIT_USER:-labsadmin}"
COMPOSE_BIN="${COMPOSE_BIN:-/usr/local/bin/docker-compose}"
REQUEST_PATH="${PANDAMONIUM_UPDATE_REQUEST:-$ROOT/data/updates/request.json}"
LIVE_BRANCH="${PANDAMONIUM_LIVE_BRANCH:-cursor-bridge}"
BRIDGE_GUARD='cursor.?bridge|pc-cursor|cursorBridge|cursorCanvas'

if [[ ! -d /mnt/dev-env ]]; then
  echo "error: /mnt/dev-env is not mounted" >&2
  exit 1
fi
if [[ ! -d "$ROOT/.git" ]]; then
  echo "error: not a git repo: $ROOT" >&2
  exit 1
fi

git_as() {
  sudo -u "$GIT_USER" git -C "$ROOT" "$@"
}

app_version_in_tree() {
  git_as show HEAD:src/constants.py | python3 - <<'PY'
import re, sys
text = sys.stdin.read()
match = re.search(r'^APP_VERSION\s*=\s*"([^"]+)"', text, re.M)
print(match.group(1) if match else "")
PY
}

container_app_version() {
  sudo docker exec pandamonium-pandamonium-1 python -c \
    'from src.constants import APP_VERSION; print(APP_VERSION)' 2>/dev/null || true
}

semver_gt() {
  python3 - "$1" "$2" <<'PY'
import re, sys
def parts(value):
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", value.strip())
    if not match:
        sys.exit(2)
    return tuple(int(p) for p in match.groups())
sys.exit(0 if parts(sys.argv[1]) > parts(sys.argv[2]) else 1)
PY
}

tree_is_dirty() {
  [[ -n "$(git_as status --porcelain)" ]]
}

assert_no_bridge_on_main() {
  if git_as ls-tree -r --name-only main | grep -iE "$BRIDGE_GUARD" >/dev/null; then
    echo "error: cursor-bridge files present on main; refusing to continue" >&2
    git_as ls-tree -r --name-only main | grep -iE "$BRIDGE_GUARD" >&2
    exit 4
  fi
}

merge_tag_into() {
  local branch="$1" tag="$2"
  git_as checkout "$branch"
  if git_as merge-base --is-ancestor "$tag" HEAD; then
    echo "$branch already contains $tag"
    return 0
  fi
  git_as merge "$tag" -m "Merge upstream Pandamonium $tag into $branch."
}

rebuild_if_needed() {
  local git_ver container_ver rev
  git_ver="$(app_version_in_tree)"
  container_ver="$(container_app_version)"
  rev="$(git_as rev-parse HEAD)"
  echo "git APP_VERSION=$git_ver HEAD=$rev container APP_VERSION=${container_ver:-unknown}"
  if [[ "$container_ver" == "$git_ver" ]]; then
    echo "container already matches git; no rebuild"
    return 0
  fi
  echo "rebuilding pandamonium image to $git_ver ($rev) from committed HEAD"
  build_dir="$(mktemp -d /tmp/panda-update.XXXXXX)"
  git_as archive HEAD | tar -C "$build_dir" -xf -
  sudo docker build -f "$build_dir/docker/Dockerfile.app-overlay" \
    --build-arg PANDAMONIUM_SOURCE_REVISION="$rev" \
    -t pandamonium-pandamonium:latest "$build_dir"
  rm -rf "$build_dir"
  sudo env PANDAMONIUM_SOURCE_REVISION="$rev" \
    "$COMPOSE_BIN" -f "$ROOT/docker-compose.yml" -f "$ROOT/docker/host-proxmox.yml" \
    --env-file "$ROOT/.env" \
    up -d --no-deps --no-build --force-recreate pandamonium
}

cd "$ROOT"
current="$(git_as branch --show-current)"
if [[ "$current" != "$LIVE_BRANCH" ]]; then
  echo "error: live checkout must be $LIVE_BRANCH (got $current)" >&2
  exit 5
fi
trap 'git_as checkout "$LIVE_BRANCH" >/dev/null 2>&1 || true' EXIT

git_as fetch github --tags --prune

want_tag=""
if [[ -f "$REQUEST_PATH" ]]; then
  want_tag="$(python3 - "$REQUEST_PATH" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
version = str(data.get("target_version") or "").strip()
print(f"v{version.lstrip('v')}" if version else "")
PY
)"
fi
if [[ -z "$want_tag" ]]; then
  set +o pipefail
  want_tag="$(git_as tag -l 'v[0-9]*.[0-9]*.[0-9]*' --sort=-v:refname | awk '/^v[0-9]+\.[0-9]+\.[0-9]+$/{print; exit}')"
  set -o pipefail
fi

git_ver="$(app_version_in_tree)"
if [[ -n "$want_tag" ]] && semver_gt "$want_tag" "v$git_ver"; then
  if tree_is_dirty; then
    echo "warning: working tree is dirty; skipping git merge of $want_tag (rebuild still uses committed HEAD)"
    git_as status --short
  else
    echo "merging $want_tag into $LIVE_BRANCH and main"
    merge_tag_into "$LIVE_BRANCH" "$want_tag"
    git_as checkout main
    merge_tag_into main "$want_tag"
    assert_no_bridge_on_main
    git_as checkout "$LIVE_BRANCH"
    assert_no_bridge_on_main
  fi
fi

rebuild_if_needed

if [[ -f "$REQUEST_PATH" ]]; then
  rm -f "$REQUEST_PATH"
fi
echo "done"
