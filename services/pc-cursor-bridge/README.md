# PC Cursor bridge

Read-only LAN companion that exposes Cursor IDE agent transcript metadata for
Panda's sidebar mirror (Phase 2).

Run on the Windows Cursor host:

```bash
python services/pc-cursor-bridge/pc_cursor_bridge.py
```

Environment:

- `JARVIS_CURSOR_BRIDGE_HOST` — bind address (default `127.0.0.1`)
- `JARVIS_CURSOR_BRIDGE_PORT` — port (default `8051`)
- `JARVIS_CURSOR_BRIDGE_TOKEN_FILE` — bearer token path
- `JARVIS_CURSOR_PROJECTS_ROOT` — Cursor projects root (default `~/.cursor/projects`)

Pandamonium reads mirrored agents when `ODYSSEUS_PC_CURSOR_BRIDGE_URL` is set.
