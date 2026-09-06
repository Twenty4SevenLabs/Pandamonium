# Cursor agent full-screen chat (Panda overlay)

**Date:** 2026-09-06  
**Status:** Approved  
**Branch:** `cursor-bridge`  
**Approach:** Per-node Cursor bridge sidecars + Panda router (Approach 1)

## Goal

When Jason clicks a Cursor agent in Panda’s sidebar, open a **full-screen overlay** with a **full Cursor-parity chat** so he can continue the session from Panda — including IDE agents originally started via Remote-SSH. Composer **2.5 only**; **fast mode off** at all times.

## Decisions (brainstorming lock)

| Topic | Decision |
|--------|----------|
| IDE agents | Continue via SDK `resume_agent` + `send` (not read-only) |
| Layout | Full-screen **overlay**; Esc / × closes; underlying Panda view unchanged |
| Feature scope | **Full Cursor parity** in v1 (thinking, tools, MCP, attachments, usage, git, artifacts) |
| Cluster routing | **Auto-route** to M3 / M1 / M2 + **visible execution-node badge** |
| Architecture | **Approach 1:** full `cursor-bridge` sidecar on each node; Panda routes by agent metadata |

## Non-goals

- Local Windows Cursor install or `%USERPROFILE%\.cursor` paths
- Cloud Cursor agents or models other than `composer-2.5`
- Model picker or “fast” variant in UI
- Replacing Remote-SSH Cursor as the primary IDE (Panda is an additional client)

## Global constraints

- **Model:** `composer-2.5` only (`REQUIRED_MODEL` in `subscription_guard.py`)
- **Fast off:** reject model id `composer-2.5-fast`, any `ModelVariant` fast flag, and model params whose name/id contains `fast` (case-insensitive) in guard + sidecar
- **Runtime:** local SDK only; subscription guard fail-closed (no cloud REST, no `--cloud`)
- **Auth:** Panda admin session for connect/send; bridge token for sidecar LAN calls
- **Cluster:** M3 `192.168.1.93`, M1 `192.168.1.2`, M2 `192.168.1.90`; transcripts follow SSH host (`~/.cursor/projects`)

## Architecture

```
Panda UI (overlay)
  → /api/cursor/* (routes/cursor_bridge_routes.py)
  → cursor_bridge_manager (node router)
       ├─ M3 http://127.0.0.1:8050  (Docker/host sidecar)
       ├─ M1 http://192.168.1.2:8050
       └─ M2 http://192.168.1.90:8050
  → cursor_bridge_service.py (cursor-sdk AsyncClient per node)
       resume_agent / send / stream / cancel
  IDE history seed: pc-cursor-bridge :8051 (read) + merged into session on first open
```

### Node routing rules

1. **BRIDGE** agents (`source=bridge`) → always **M3** sidecar.
2. **IDE** agents (`source=ide`) → sidecar on node from `mirror_url` / `execution_node`:
   - `http://pc-cursor-bridge:8051` or M3 LAN → M3
   - `http://192.168.1.2:8051` → M1
   - `http://192.168.1.90:8051` → M2
3. First interactive send on IDE agent: `resume_agent(agent_id, { model, local: { cwd } })` on routed node, then `send(prompt)`.
4. **`cwd`** from workspace slug in transcript project folder (e.g. `mnt-dev-env-projects-pandamonium` → `/mnt/dev-env/projects/pandamonium` on M3; same mapping when `/mnt/dev-env` mounted on M1/M2, else `~/projects/<slug>` fallback documented in env).

### Env (Panda `.env`)

```bash
PANDAMONIUM_CURSOR_BRIDGE_URL=http://127.0.0.1:8050
PANDAMONIUM_CURSOR_BRIDGE_URLS=http://127.0.0.1:8050,http://192.168.1.2:8050,http://192.168.1.90:8050
PANDAMONIUM_PC_CURSOR_BRIDGE_URLS=http://pc-cursor-bridge:8051,http://192.168.1.2:8051,http://192.168.1.90:8051
PANDAMONIUM_CURSOR_WORKSPACES_JSON={"pandamonium":"/mnt/dev-env/projects/pandamonium"}
```

## UX — overlay shell

- New `#cursor-agent-overlay` fixed full-viewport layer (pattern: styled confirm / research overlays).
- **Header:** × close, agent title, source badge (`IDE` / `BRIDGE`), execution badge (`pve-prod` | `pve-heavy` | `pve-agents`), optional git branch chip.
- **Body:** scrollable message column with parity blocks (below).
- **Footer:** locked label `Composer 2.5 · local · fast off`; attachment button; textarea; **Stop** (cancel run); **Send**.
- **Keyboard:** Esc closes (if not streaming, or confirm if running); Enter sends (Shift+Enter newline).
- Sidebar agent list remains; clicking another agent swaps overlay content.
- Remove or hide cramped in-sidebar `#cursor-agent-detail` panel (list-only in sidebar).

## SDK event → UI mapping (v1 parity)

| SDK / stream event | UI block |
|--------------------|----------|
| Text / text delta | Assistant bubble (markdown-safe plain text v1) |
| Thinking started/delta/completed | Collapsible “Thinking” panel |
| Tool started/completed | Expandable chip: name, args JSON, result, status |
| Shell output delta | Monospace sub-block under tool |
| User message / images | User bubble; thumbnails for images |
| MCP tool calls | Tool chip tagged `MCP` |
| Usage / cost | Footer turn stats |
| Git branch info | Header meta chip |
| Artifacts | Download link card |
| Error / cancelled | Red banner; Stop clears running state |

Session load merges: (1) IDE transcript via pc-bridge when `source=ide`, (2) sidecar registry messages, (3) live stream events — dedupe by stable message id when present.

## API changes

| Method | Path | Change |
|--------|------|--------|
| GET | `/api/cursor/agents/{id}/session` | Add `execution_node`, `execution_host`, `can_send`, merged parity messages |
| POST | `/api/cursor/agents/{id}/send` | Route to node sidecar; IDE first-send triggers resume |
| POST | `/api/cursor/agents/{id}/resume` | **New** — explicit IDE resume (optional; send may inline) |
| POST | `/api/cursor/agents/{id}/runs/{run_id}/cancel` | **New** Panda proxy to routed sidecar |
| GET | `/api/cursor/status` | Add `bridge_hosts[]` per-node health |

Sidecar additions (`cursor_bridge_service.py`):

- Richer `_consume_run` → normalized `RunStreamEvent` JSON (not text-only)
- `POST /agents/{id}/resume` for IDE handoff
- Session responses include `execution_node`

## Cluster deploy (M1 / M2)

Extend `services/cursor-bridge/remote-install-sidecar.sh` (new):

- Copy `cursor_bridge_service.py`, `subscription_guard.py` to node
- systemd `cursor-bridge.service` on `0.0.0.0:8050` (LAN only, same bridge token as M3)
- Shared encrypted API key: Panda pushes key on connect or sync `PANDAMONIUM_CURSOR_API_KEY` to node env (document manual step for v1)
- Firewall: allow 8050 from M3 `192.168.1.93` only

## Model / fast enforcement

- `subscription_guard.assert_model`: reject ids ending in `-fast` or containing `fast` as variant
- `assert_agent_options`: if `model` is dict, strip/reject params where key or value implies fast
- UI: no model controls; footer shows locked copy only
- Tests: `test_cursor_bridge_guard.py` extended

## Error handling

| Case | Behavior |
|------|----------|
| Sidecar down on routed node | Overlay banner + badge warning; send disabled with reason |
| `resume_agent` 404 | Offer “Start new BRIDGE fork” only if user confirms (optional v1: hard error) |
| Guard violation | 403 with reason in overlay |
| Stream disconnect | Append `[stream ended]`; reload session |

## Testing

- Unit: node router, fast guard, event normalizer, IDE resume routing (mocked httpx)
- Route: session merge, send proxy, cancel proxy
- Manual: open IDE agent from M3 list → overlay → send → stream; verify badge; M1/M2 after sidecar deploy

## Success criteria

- [ ] Click any listed agent → full-screen overlay opens
- [ ] IDE + BRIDGE agents accept follow-up messages where sidecar available
- [ ] Streaming shows tools/thinking/usage blocks
- [ ] Stop cancels run on correct node
- [ ] Badge shows execution host for IDE agents on M1/M2/M3
- [ ] Only `composer-2.5`; fast rejected in API and UI
- [ ] Esc / × closes overlay without losing sidebar selection

## Related docs

- `services/pc-cursor-bridge/README.md` — Remote-SSH transcript mirrors
- `services/cursor-bridge/README.md` — API key + sidecar
- `docs/superpowers/specs/2026-09-04-cursor-pandamonium-migration-design.md`
