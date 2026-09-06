#!/usr/bin/env bash
# Deploy cursor-bridge SDK sidecar on M1/M2 (systemd, port 8050).
set -euo pipefail

USER="${1:-labsadmin}"
TOKEN="${2:?bridge token required}"
API_KEY="${3:?CURSOR API key required}"
BIND_HOST="${4:?bind host required, e.g. 192.168.1.2}"
SRC_DIR="${5:-/tmp/cursor-bridge-sidecar}"
WORKSPACE_PATH="${6:-/home/labsadmin}"

HOME_DIR="$(getent passwd "$USER" | cut -d: -f6)"
INSTALL_DIR="$HOME_DIR/.local/share/pandamonium/cursor-bridge"
BRIDGE_TOKEN="$HOME_DIR/.config/jarvis/cursor-bridge-token"
STATE_DIR="$HOME_DIR/.local/share/pandamonium/cursor-bridge-state"

mkdir -p "$INSTALL_DIR" "$(dirname "$BRIDGE_TOKEN")" "$STATE_DIR" "$WORKSPACE_PATH"
install -m 644 "$SRC_DIR/cursor_bridge_service.py" "$SRC_DIR/subscription_guard.py" "$SRC_DIR/agent_settings.py" "$SRC_DIR/canvas_bridge.py" "$INSTALL_DIR/"
if [[ -f "$SRC_DIR/stream_events.py" ]]; then
  install -m 644 "$SRC_DIR/stream_events.py" "$INSTALL_DIR/"
fi
if [[ -f "$SRC_DIR/atomic_io.py" ]]; then
  install -m 644 "$SRC_DIR/atomic_io.py" "$INSTALL_DIR/"
fi
printf '%s\n' "$TOKEN" >"$BRIDGE_TOKEN"
chmod 600 "$BRIDGE_TOKEN"

sudo -u "$USER" python3 -m pip install --user --break-system-packages -q \
  "cursor-sdk==1.0.31" fastapi uvicorn httpx 2>/dev/null \
  || sudo -u "$USER" python3 -m pip install --user -q "cursor-sdk==1.0.31" fastapi uvicorn httpx

chown -R "$USER:$USER" "$HOME_DIR/.local" "$HOME_DIR/.config/jarvis"

WORKSPACES_JSON="{\"pandamonium\":\"${WORKSPACE_PATH}\"}"

cat >/etc/default/cursor-bridge <<EOF
CURSOR_API_KEY=$API_KEY
ODYSSEUS_CURSOR_BRIDGE_TOKEN_FILE=$BRIDGE_TOKEN
ODYSSEUS_CURSOR_BRIDGE_STATE_DIR=$STATE_DIR
ODYSSEUS_CURSOR_BRIDGE_HOST=$BIND_HOST
ODYSSEUS_CURSOR_BRIDGE_PORT=8050
ODYSSEUS_CURSOR_BRIDGE_HOSTS=$BIND_HOST
ODYSSEUS_CURSOR_WORKSPACES_JSON=$WORKSPACES_JSON
EOF
chmod 600 /etc/default/cursor-bridge

cat >/etc/systemd/system/cursor-bridge.service <<EOF
[Unit]
Description=Cursor SDK bridge sidecar for Pandamonium
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$INSTALL_DIR
EnvironmentFile=/etc/default/cursor-bridge
Environment=PATH=$HOME_DIR/.local/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/usr/bin/python3 $INSTALL_DIR/cursor_bridge_service.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl restart cursor-bridge.service
sleep 3
systemctl status cursor-bridge.service --no-pager || true
curl -sf -H "Authorization: Bearer $TOKEN" "http://${BIND_HOST}:8050/health" || curl -sf -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:8050/health" || echo "health check failed"
echo ""
echo "Installed cursor-bridge sidecar on $(hostname) at ${BIND_HOST}:8050"
