# Cursor → Pandamonium migration design

**Date:** 2026-09-04  
**Status:** Implemented  
**Source:** `~/.config/opencode` on vm-hermes  
**Target:** `/mnt/dev-env/projects/pandamonium/data/`

## Goal

Import the Cursor personality bundle (already consolidated in OpenCode) into Pandamonium so the web agent has Hermes orchestrator behavior, Trinity skills, MCP servers, slash commands, and archived agent definitions.

## Mapping

| Cursor/OpenCode | Pandamonium |
|---|---|
| AGENTS.md | `settings.json` constitution + `presets.json` hermes_orchestrator |
| skills/ (132) | `data/skills/<category>/<name>/SKILL.md` |
| opencode.jsonc mcp | `data/app.db` mcp_servers |
| commands/ | `slashCommands.js` /kanban /trinity + skill slash tokens |
| agents/ + plugins/ | `data/personal_docs/cursor-migration/` |
| hooks (TS plugins) | constitution + tool policy notes |

## Gaps

- cursor-* skills marked draft (Cursor-only APIs)
- Hermes MCP over SSH may need OAuth/host key tuning
- GitLab MCP TLS on self-hosted cert

## Rollback

`tar czf /mnt/dev-env/backups/pandamonium-data-pre-cursor-migration-*.tgz data/`

## Success criteria

- [x] ≥130 skills in data/skills/
- [x] Constitution version 2 with Hermes + Context7
- [x] 10 MCP servers registered
- [x] /kanban and /trinity slash commands
- [x] Archive of agents and plugins
- [x] unittest + manifest preview

## Execution log (2026-09-05)

- Kanban: board `pandamonium` created; parent card `t_79022dfd` (completed)
- Backup: `/mnt/dev-env/backups/pandamonium-data-pre-cursor-migration-20260904.tgz`
- Import: 132 skills (hermes=4, superpowers=14, trinity=18, prisma=40, integrations=24, cursor=28 draft, imported=4)
- MCP: 10 servers registered (+ existing MAD MCP Portal)
- Archive: 17 files under `data/personal_docs/cursor-migration/`
- Tests: `pytest tests/test_cursor_opencode_import.py` + migration suite — 22 passed
- Slash: `/kanban parent`, `/trinity check` patched in `static/js/slashCommands.js`

### Known follow-ups (manual)

- OAuth once: prisma-remote, neon, figma, gitlab
- Hermes MCP over SSH may need host-key / connection tuning
- GitLab MCP TLS: set `NODE_EXTRA_CA_CERTS` in `.env`
- Restart Pandamonium after `slashCommands.js` change
