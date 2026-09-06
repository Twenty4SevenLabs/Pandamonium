# Cursor bridge

Always-on local Cursor SDK sidecar for Panda's **Cursor Agents** sidebar.

## Where to put your API key

**Option A — `.env` (server / one-time setup)**

Add to `/mnt/dev-env/projects/pandamonium/.env`:

```bash
PANDAMONIUM_CURSOR_API_KEY=cursor_your_real_key_here
```

Restart Panda. The key is copied into encrypted storage at:

`data/cursor-bridge/settings.json` → field `api_key_encrypted`

**Option B — Panda UI (easiest day to day)**

1. Open Panda → sidebar **Cursor Agents** (above Tools)
2. Paste your key in the connect box (`cursor_...`)
3. Click **Connect** (admin session required)

Same encrypted file as Option A.

Get the key from [Cursor Dashboard → Integrations](https://cursor.com/dashboard/integrations).

## Other paths

| Path | Purpose |
|------|---------|
| `data/cursor-bridge/token` | Localhost bridge auth (auto-generated) |
| `data/cursor-bridge/agents.json` | Bridge agent registry |
| `services/cursor-bridge/cursor_bridge_service.py` | Sidecar process (port 8050) |

## Optional env

```bash
PANDAMONIUM_CURSOR_BRIDGE_URL=http://127.0.0.1:8050
PANDAMONIUM_CURSOR_WORKSPACES_JSON={"pandamonium":"/mnt/dev-env/projects/pandamonium"}
# Load Cursor skills/rules/MCP like the IDE (project + user + plugins)
PANDAMONIUM_CURSOR_BRIDGE_HOME=/home/labsadmin
PANDAMONIUM_CURSOR_SETTING_SOURCES=project,user,plugins
# Optional overrides:
# PANDAMONIUM_CURSOR_CONFIG_DIR=/home/labsadmin/.cursor
# PANDAMONIUM_CURSOR_MCP_CONFIG=/home/labsadmin/.cursor/mcp.json
# Phase 2 — Remote-SSH IDE transcript mirror (see services/pc-cursor-bridge/README.md)
PANDAMONIUM_PC_CURSOR_BRIDGE_URL=http://pc-cursor-bridge:8051
PANDAMONIUM_PC_CURSOR_BRIDGE_URLS=http://pc-cursor-bridge:8051,http://192.168.1.2:8051,http://192.168.1.90:8051
```

Install dependency: `pip install cursor-sdk==1.0.31` (listed in `requirements-optional.txt`).
