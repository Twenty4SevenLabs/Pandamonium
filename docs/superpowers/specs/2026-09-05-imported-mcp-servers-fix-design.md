# Imported Pandamonium MCP servers fix

**Date:** 2026-09-05  
**Status:** Implemented  
**Parent:** Cursor → Pandamonium migration (`2026-09-04-cursor-pandamonium-migration-design.md`)

## Problem

The OpenCode import registered 10 MCP servers into `data/app.db`, but the Panda UI showed `error` / `disconnected` for every imported server except `shadcn`.

## Root causes

1. Remote servers (`context7`, `gitlab`, `prisma-remote`, `neon`, `figma`) were stored as `transport=sse` against Streamable HTTP `/mcp` URLs. Panda already has a working `http` + OAuth client.
2. `${VAR}` placeholders in MCP `env` were passed literally to subprocesses and never expanded.
3. Hermes used `ssh openclaw1@vm-hermes` from Docker. That hostname is not in the container `extra_hosts` map.
4. GitLab was pointed at native `/api/v4/mcp` over SSE with no token. This lab's working GitLab MCP path is stdio `@zereight/gitlab-mcp` against CT311.
5. OAuth redirect defaulted to `http://localhost:7000` while the UI is `https://prod.tail61d527.ts.net:7080`.
6. Stdio connect timeout was 20s, which cancels first-run `npx` servers (`prisma-local`).

## Fix

- Import catalog: HTTP for Context7 / Prisma remote / Neon / Figma; GitLab stdio + PAT; Hermes SSH to `192.168.1.192` with `BatchMode`.
- Expand `${VAR}` / `{env:VAR}` at connect time; map API keys to `Authorization: Bearer` for HTTP.
- Pass MCP secrets and `APP_PUBLIC_URL` through Compose; lab overlay sets GitLab API URL and Tailscale OAuth origin.
- Raise connect timeout to 90s.

OAuth servers (Prisma remote, Neon, Figma) still need one browser authorize click after reconnect. Aikido / GitHub / GitLab / Context7 / Neon HTTP work unattended when the matching env key is set.
