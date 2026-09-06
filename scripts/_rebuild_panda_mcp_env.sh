#!/bin/bash
# Rebuild Panda and verify MCP ENV placeholders. Prints key names and set/empty, never values.
set -euo pipefail
cd /mnt/dev-env/projects/pandamonium

KEYS=(
  GITHUB_TOKEN
  GITLAB_TOKEN
  GITLAB_API_URL
  CONTEXT7_API_KEY
  NEON_API_KEY
  FIGMA_API_KEY
  AIKIDO_API_KEY
  APP_PUBLIC_URL
  OAUTH_REDIRECT_BASE_URL
)

echo "=== 1. ensure .env keys exist (names only) ==="
sudo python3 - <<'PY'
from pathlib import Path
p = Path("/mnt/dev-env/projects/pandamonium/.env")
defaults = {
    "GITHUB_TOKEN": "",
    "GITLAB_TOKEN": "",
    "GITLAB_API_URL": "http://192.168.1.211/api/v4",
    "CONTEXT7_API_KEY": "",
    "NEON_API_KEY": "",
    "FIGMA_API_KEY": "",
    "AIKIDO_API_KEY": "",
    "APP_PUBLIC_URL": "https://prod.tail61d527.ts.net:7080",
    "OAUTH_REDIRECT_BASE_URL": "https://prod.tail61d527.ts.net:7080",
}
text = p.read_text(encoding="utf-8") if p.exists() else ""
present = set()
for line in text.splitlines():
    s = line.strip()
    if not s or s.startswith("#") or "=" not in s:
        continue
    present.add(s.split("=", 1)[0])
added = []
for key, default in defaults.items():
    if key not in present:
        text += ("" if text.endswith("\n") or not text else "\n") + f"{key}={default}\n"
        added.append(key)
if added:
    p.write_text(text, encoding="utf-8")
print("already_present", sorted(k for k in defaults if k in present))
print("added", added)
PY

echo "=== 2. rewrite MCP rows (placeholders in DB env JSON) ==="
python3 scripts/import_cursor_opencode_bundle.py --mcp-only || sudo python3 scripts/import_cursor_opencode_bundle.py --mcp-only

echo "=== 3. DB env placeholders ==="
python3 - <<'PY'
import json, sqlite3
from pathlib import Path
db = Path("/mnt/dev-env/projects/pandamonium/data/app.db")
con = sqlite3.connect(db)
rows = con.execute("SELECT name, transport, env FROM mcp_servers ORDER BY name").fetchall()
con.close()
for name, transport, env in rows:
    parsed = {}
    try:
        parsed = json.loads(env or "{}")
    except Exception:
        parsed = {"_raw": "unparseable"}
    placeholders = {k: v for k, v in parsed.items() if isinstance(v, str) and ("${" in v or "{env:" in v)}
    print(f"{name}\t{transport}\tplaceholders={placeholders or '-'}")
PY

echo "=== 4. rebuild pandamonium service ==="
sudo systemctl start pandamonium.service
# oneshot RemainAfterExit=yes: restart to force a new up -d --build
sudo systemctl restart pandamonium.service

echo "=== 5. wait for container ==="
for i in $(seq 1 60); do
  if sudo docker ps --format '{{.Names}}' | grep -q 'pandamonium-pandamonium-1'; then
    break
  fi
  sleep 5
done
sudo docker ps --format '{{.Names}} {{.Status}}' | grep pandamonium || true

echo "=== 6. container ENV key presence (set/empty, no values) ==="
CID=$(sudo docker ps -qf name=pandamonium-pandamonium-1 | head -1)
if [ -z "$CID" ]; then
  echo "CONTAINER_MISSING"
  exit 1
fi
for key in "${KEYS[@]}"; do
  if sudo docker exec "$CID" sh -c "printenv $key >/dev/null 2>&1"; then
    val=$(sudo docker exec "$CID" sh -c "printenv $key || true")
    if [ -z "$val" ]; then
      echo "$key=empty"
    else
      echo "$key=set len=${#val}"
    fi
  else
    echo "$key=MISSING"
  fi
done
echo "DONE"
