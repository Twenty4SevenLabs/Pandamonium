# Hermes MCP Kanban for Pandamonium

**Date:** 2026-09-06  
**Status:** Implemented

## Problem

Panda’s `hermes` MCP stayed `error` (`Connection closed`). Even after LAN-IP SSH, it could not see Hermes Kanban.

## Root causes

1. Cookbook key `data/ssh/id_ed25519.pub` (`SHA256:ST3EGcpIdWmXfvtvJf3RCRXWeJ+ArbGIhEQBYoslyt0`) is not in `openclaw1` `authorized_keys`. Container SSH is `Permission denied (publickey)`.
2. MCP ssh args did not pass `-i /app/.ssh/id_ed25519`. `docker exec` as root uses `HOME=/root` and never offers the cookbook key. Explicit IdentityFile + `IdentitiesOnly=yes` + `UserKnownHostsFile=/app/.ssh/known_hosts` makes this independent of HOME.
3. Remote command was `hermes mcp serve` (messaging bridge: conversations/messages). Kanban tools live on stdio `python -m agent.transports.hermes_tools_mcp_server` (`kanban_list`, `kanban_show`, `kanban_create`, …).

## Fix

- Authorize the cookbook public key on vm-hermes (fingerprint match only; do not log key bodies).
- Import catalog: ssh `-i /app/.ssh/id_ed25519` to `openclaw1@192.168.1.192` running `hermes_tools_mcp_server` from `~/.hermes/hermes-agent` with `HERMES_QUIET=1`. Leave `HERMES_KANBAN_TASK` unset so Panda can list/create like an orchestrator. Follow `kanban/current` (do not pin a DB path).
- Add `hermes-messaging` MCP: same SSH transport, remote `venv/bin/hermes mcp serve` for conversations/messages/channels across agent platforms.
- Expose full Kanban surface on vm-hermes (`kanban_attach`, `kanban_attach_url`, `kanban_attachments` added to `EXPOSED_TOOLS`).

## Success

Panda `hermes` status `connected` with all 14 `kanban_*` tools plus `hermes-messaging` `connected` with 10 conversation tools (`messages_send`, `conversations_list`, …).

## SSH CLI (bash fallback)

When Panda uses `bash` + `ssh`, the dedicated `hermes_ssh` tool, or the new `hermes_kanban` structured tool instead of MCP:

- `hermes_kanban` — structured Kanban CLI with correct create syntax (positional title), default board `pandamonium`, actions list/show/create/complete/archive/dispatch/….
- `hermes_ssh` runs any command on vm-hermes as `openclaw1` (bounded_write, auto-allowed). Auto-sets `HERMES_KANBAN_BOARD=pandamonium` and rewrites invalid `create --title` to positional title.
- Tool RAG seeds `hermes_kanban`, `hermes_ssh` + `bash` whenever the `hermes` intent domain fires (kanban, archive, morpheus, vm-hermes, …).
- `src/ssh_cookbook.py` writes `data/ssh/config`, refreshes `known_hosts`, and installs `data/bin/ssh` wrapper.
- vm-hermes: `hermes` on `/usr/local/bin`; `openclaw1` has passwordless sudo.

## MCP stability (2026-09-06)

- `McpManager.ensure_connected(server_id)` reconnects Hermes MCP from DB config when the session is missing.
- `call_tool` auto-reconnects Hermes SSH stdio MCP servers (and builtins) after subprocess crashes.
