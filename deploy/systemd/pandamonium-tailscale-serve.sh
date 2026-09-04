#!/bin/bash
# Map Tailscale HTTPS :7080 → Pandamonium loopback. Do not Funnel.
# Call after the app is listening on 127.0.0.1:7080.
set -euo pipefail
/usr/bin/tailscale serve --https=7080 off 2>/dev/null || true
/usr/bin/tailscale serve --bg --https=7080 http://127.0.0.1:7080
/usr/bin/tailscale serve status | grep -A3 7080 || true
