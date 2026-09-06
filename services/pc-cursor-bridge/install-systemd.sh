#!/usr/bin/env bash
# Install pc-cursor-bridge as a systemd system service on a Remote-SSH Linux host (M1/M2/etc).
# Run as root on the target node (from pve-prod: sudo ssh root@pve-heavy bash remote-install.sh ...).
set -euo pipefail

USER="${1:-labsadmin}"
TOKEN="${2:?token required}"
SRC_DIR="${3:-/tmp/pc-cursor-bridge}"

HOME_DIR="$(getent passwd "$USER" | cut -d: -f6)"
INSTALL_DIR="$HOME_DIR/.local/share/pandamonium/pc-cursor-bridge"
TOKEN_FILE="$HOME_DIR/.config/jarvis/cursor-bridge-token"
PROJECTS_ROOT="$HOME_DIR/.cursor/projects"

mkdir -p "$INSTALL_DIR" "$(dirname "$TOKEN_FILE")" "$PROJECTS_ROOT"
install -m 644 "$SRC_DIR/pc_cursor_bridge.py" "$SRC_DIR/transcript_io.py" "$INSTALL_DIR/"
printf '%s\n' "$TOKEN" >"$TOKEN_FILE"
chmod 600 "$TOKEN_FILE"
chown -R "$USER:$USER" "$HOME_DIR/.local" "$HOME_DIR/.config/jarvis" "$PROJECTS_ROOT"

cat >/etc/systemd/system/pc-cursor-bridge.service <<EOF
[Unit]
Description=PC Cursor bridge (Remote-SSH IDE transcript mirror)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$INSTALL_DIR
Environment=JARVIS_CURSOR_BRIDGE_ALLOW_LAN=1
Environment=JARVIS_CURSOR_BRIDGE_HOST=0.0.0.0
Environment=JARVIS_CURSOR_BRIDGE_PORT=8051
Environment=JARVIS_CURSOR_BRIDGE_HOSTS=0.0.0.0
Environment=JARVIS_CURSOR_BRIDGE_TOKEN_FILE=$TOKEN_FILE
Environment=JARVIS_CURSOR_PROJECTS_ROOT=$PROJECTS_ROOT
ExecStart=/usr/bin/python3 $INSTALL_DIR/pc_cursor_bridge.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now pc-cursor-bridge.service
systemctl status pc-cursor-bridge.service --no-pager || true
echo "Installed on $(hostname) for $USER"
