# DuckDuckGo MCP for Pandamonium

**Date:** 2026-09-06  
**Status:** Implementing  
**Parent:** Imported MCP servers (`2026-09-05-imported-mcp-servers-fix-design.md`)

## Goal

Register a DuckDuckGo web-search MCP server in Panda so the agent can search the web without a search API key.

## Choice

Use the npm MCP `@oevortex/ddg_search` over stdio:

```
npx -y @oevortex/ddg_search@latest
```

Reasons:

- Matches existing Panda stdio servers (`shadcn`, `github`) that already work via `npx` in the image.
- No API key and no Dockerfile/`uv` change. The canonical Python package `duckduckgo-mcp-server` needs `uvx` plus the `[browser]` extra; this image has Node, not `uv`.
- First `npx -y` is covered by the 90s MCP connect timeout.

## Persistence

Add a `duckduckgo` row to `scripts/import_cursor_opencode_bundle.py` `MCP_SERVERS`. `--mcp-only` upserts it into `data/app.db`. Do not delete other servers (MAD MCP Portal stays).

## Out of scope

- Do not replace SearXNG.
- Do not add Compose secrets (none required).
- Do not change Unsloth or Chatterbox.
