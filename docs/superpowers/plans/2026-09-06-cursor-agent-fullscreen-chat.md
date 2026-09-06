# Cursor Agent Full-Screen Chat Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Full-screen Panda overlay for Cursor agents with SDK-backed chat (IDE + BRIDGE), per-node sidecar routing, and Composer 2.5-only (fast off) parity UI.

**Architecture:** Approach 1 — deploy `cursor-bridge` sidecars on M3/M1/M2; `cursor_bridge_manager` routes API calls by agent `mirror_url` / `source`; overlay UI in new module replaces in-sidebar detail panel; stream normalizer emits rich blocks for thinking/tools/usage/artifacts.

**Tech Stack:** Python 3.13, FastAPI, cursor-sdk 1.0.31, vanilla JS modules, existing Panda overlay CSS patterns, systemd on Proxmox nodes.

## Global Constraints

- Model id must be exactly `composer-2.5` — reject `-fast` variants and fast model params (case-insensitive) in `subscription_guard.py` and sidecar.
- Local SDK runtime only; subscription guard fail-closed (existing `subscription_guard.py` rules).
- No model picker in UI; footer shows locked `Composer 2.5 · local · fast off`.
- IDE agents resume on the same node as `mirror_url` (M3/M1/M2); BRIDGE agents always use M3.
- Do not commit `.env`, API keys, or `data/cursor-bridge/settings.json`.

---

## File map

| File | Responsibility |
|------|----------------|
| `src/cursor_bridge_manager.py` | Node registry, route sidecar URL, proxy httpx to correct host |
| `src/cursor_bridge_nodes.py` | **New** — parse mirror_url → node id, cwd from workspace slug |
| `services/cursor-bridge/cursor_bridge_service.py` | Rich stream consumer, resume endpoint, parity session schema |
| `services/cursor-bridge/subscription_guard.py` | Fast-mode rejection |
| `services/cursor-bridge/stream_events.py` | **New** — SDK event → JSON block normalizer |
| `routes/cursor_bridge_routes.py` | Cancel proxy, session fields, send/resume routing |
| `static/js/cursorBridgeOverlay.js` | **New** — overlay open/close, render parity blocks, send/stop/stream |
| `static/js/cursorBridge.js` | List-only sidebar; delegate click → overlay |
| `static/index.html` | `#cursor-agent-overlay` markup |
| `static/style.css` | Overlay + parity block styles |
| `services/cursor-bridge/remote-install-sidecar.sh` | **New** — M1/M2 systemd deploy |
| `tests/test_cursor_bridge_nodes.py` | **New** |
| `tests/test_stream_events.py` | **New** |
| `tests/test_cursor_bridge_guard.py` | Extend fast rejection |
| `tests/test_cursor_bridge_routes.py` | Overlay API contracts |

---

### Task 1: Node registry and routing

**Files:**
- Create: `src/cursor_bridge_nodes.py`
- Modify: `src/cursor_bridge_manager.py`
- Test: `tests/test_cursor_bridge_nodes.py`

**Interfaces:**
- Produces: `resolve_execution_node(agent: dict) -> str` (`m3`|`m1`|`m2`)
- Produces: `sidecar_url_for_node(node: str) -> str`
- Produces: `bridge_request_for_agent(method, path, agent_meta, **kwargs) -> httpx.Response`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_cursor_bridge_nodes.py
from src.cursor_bridge_nodes import resolve_execution_node, sidecar_url_for_node

def test_ide_agent_routes_to_m1(monkeypatch):
    monkeypatch.setenv(
        "PANDAMONIUM_CURSOR_BRIDGE_URLS",
        "http://127.0.0.1:8050,http://192.168.1.2:8050,http://192.168.1.90:8050",
    )
    agent = {"source": "ide", "mirror_url": "http://192.168.1.2:8051"}
    assert resolve_execution_node(agent) == "m1"
    assert sidecar_url_for_node("m1") == "http://192.168.1.2:8050"

def test_bridge_agent_always_m3(monkeypatch):
    monkeypatch.setenv("PANDAMONIUM_CURSOR_BRIDGE_URL", "http://127.0.0.1:8050")
    agent = {"source": "bridge", "mirror_url": "http://192.168.1.2:8051"}
    assert resolve_execution_node(agent) == "m3"
```

- [ ] **Step 2: Run tests — expect FAIL**

Run: `pytest tests/test_cursor_bridge_nodes.py -v`

- [ ] **Step 3: Implement `cursor_bridge_nodes.py` and wire manager**

```python
# src/cursor_bridge_nodes.py — core logic
NODE_HOSTS = {"m3": "pve-prod", "m1": "pve-heavy", "m2": "pve-agents"}

def resolve_execution_node(agent: dict) -> str:
    if str(agent.get("source") or "").lower() == "bridge":
        return "m3"
    url = str(agent.get("mirror_url") or "")
    if "192.168.1.2" in url:
        return "m1"
    if "192.168.1.90" in url:
        return "m2"
    return "m3"
```

Update `bridge_request` in manager to accept optional `node` override from agent metadata.

- [ ] **Step 4: Run tests — expect PASS**

- [ ] **Step 5: Commit**

```bash
git add src/cursor_bridge_nodes.py src/cursor_bridge_manager.py tests/test_cursor_bridge_nodes.py
git commit -m "feat(cursor-bridge): route SDK calls to M3/M1/M2 sidecars by agent metadata"
```

---

### Task 2: Composer 2.5 fast-off guard

**Files:**
- Modify: `services/cursor-bridge/subscription_guard.py`
- Test: `tests/test_cursor_bridge_guard.py`

- [ ] **Step 1: Add failing tests**

```python
def test_assert_model_rejects_fast_variant():
    with pytest.raises(SubscriptionGuardError):
        assert_model("composer-2.5-fast")

def test_assert_agent_options_rejects_fast_param():
    with pytest.raises(SubscriptionGuardError):
        assert_agent_options({
            "model": {"id": "composer-2.5", "params": [{"id": "fast", "value": True}]},
            "local": {"cwd": "/tmp"},
        })
```

- [ ] **Step 2: Run — expect FAIL**

- [ ] **Step 3: Extend `assert_model` and `assert_agent_options` to reject fast ids/params**

- [ ] **Step 4: Run — expect PASS**

- [ ] **Step 5: Commit**

---

### Task 3: Stream event normalizer (parity blocks)

**Files:**
- Create: `services/cursor-bridge/stream_events.py`
- Modify: `services/cursor-bridge/cursor_bridge_service.py`
- Test: `tests/test_stream_events.py`

**Interfaces:**
- Produces: `normalize_stream_event(raw: dict) -> dict | None` with `type` in `text|thinking|tool|shell|usage|artifact|error|status`

- [ ] **Step 1: Write tests for text delta, tool_started, thinking_delta, usage sample payloads**

- [ ] **Step 2: Implement normalizer mapping cursor-sdk `RunStreamEvent` shapes**

- [ ] **Step 3: Replace `_events_to_assistant_blocks` usage in `_consume_run` to append normalized events to `STATE.run_events`**

- [ ] **Step 4: Extend `_session_payload` to expose `messages[].blocks[]` with new types**

- [ ] **Step 5: Commit**

---

### Task 4: IDE resume + send on routed sidecar

**Files:**
- Modify: `services/cursor-bridge/cursor_bridge_service.py`
- Modify: `routes/cursor_bridge_routes.py`
- Modify: `src/cursor_bridge_manager.py`
- Test: `tests/test_cursor_bridge_routes.py`

- [ ] **Step 1: Add sidecar `POST /agents/{id}/resume` body `{ workspace?, cwd? }`**

- [ ] **Step 2: Panda route `POST /api/cursor/agents/{id}/send` — if `source=ide` and not yet registered on sidecar, call resume on routed node first**

- [ ] **Step 3: Add `POST /api/cursor/agents/{id}/runs/{run_id}/cancel` proxy**

- [ ] **Step 4: Session GET returns `execution_node`, `execution_host`, `can_send`**

- [ ] **Step 5: Route tests with mocked multi-node responses**

- [ ] **Step 6: Commit**

---

### Task 5: Overlay markup and styles

**Files:**
- Modify: `static/index.html`
- Modify: `static/style.css`
- Load: `design-taste-frontend` patterns for overlay (focus trap, dimmed backdrop)

- [ ] **Step 1: Add `#cursor-agent-overlay` with header/body/footer structure per spec**

- [ ] **Step 2: CSS — fixed inset 0, z-index above chat, backdrop dim, message blocks, thinking/tool/usage variants**

- [ ] **Step 3: Hide `#cursor-agent-detail` in sidebar (list-only)**

- [ ] **Step 4: Manual smoke — overlay opens/closes with dummy JS**

- [ ] **Step 5: Commit**

---

### Task 6: Overlay JS module (parity UI)

**Files:**
- Create: `static/js/cursorBridgeOverlay.js`
- Modify: `static/js/cursorBridge.js`
- Modify: `static/app.js` (import overlay module)

**Interfaces:**
- Consumes: `GET /api/cursor/agents/{id}/session`, `POST .../send`, `GET .../stream`, `POST .../cancel`
- Produces: `openCursorAgentOverlay(agentId)`, `closeCursorAgentOverlay()`

- [ ] **Step 1: Implement open/close, Esc handler, focus trap**

- [ ] **Step 2: Render parity blocks (thinking collapsible, tool expand, usage footer, artifacts)**

- [ ] **Step 3: Composer — Send, Stop, attachment stub (wire SDK image send when sidecar supports)**

- [ ] **Step 4: SSE stream merge into live assistant bubble**

- [ ] **Step 5: Header badges — source + execution_node from session payload**

- [ ] **Step 6: Wire sidebar row click → `openCursorAgentOverlay`**

- [ ] **Step 7: Commit**

---

### Task 7: M1/M2 sidecar deploy script

**Files:**
- Create: `services/cursor-bridge/remote-install-sidecar.sh`
- Modify: `services/cursor-bridge/README.md`
- Modify: `docker-compose.yml` / `.env.example` with `PANDAMONIUM_CURSOR_BRIDGE_URLS`

- [ ] **Step 1: Script installs sidecar on pve-heavy / pve-agents (systemd, port 8050, bridge token)**

- [ ] **Step 2: Document API key sync step (copy encrypted settings or env on node)**

- [ ] **Step 3: Deploy to M1/M2 via `sudo ssh root@pve-heavy` pattern from pc-bridge**

- [ ] **Step 4: Verify `curl http://192.168.1.2:8050/health` from M3**

- [ ] **Step 5: Commit**

---

### Task 8: End-to-end verification

- [ ] **Step 1: `pytest tests/test_cursor_bridge*.py tests/test_stream_events.py tests/test_pc_cursor_bridge.py -q`**

- [ ] **Step 2: Restart Panda; connect Cursor key**

- [ ] **Step 3: Click IDE agent → overlay → send message → see stream + badge**

- [ ] **Step 4: Click BRIDGE agent → same overlay flow on M3**

- [ ] **Step 5: Confirm fast model rejected if forced via API test**

---

## Plan self-review

| Spec requirement | Task |
|------------------|------|
| Full-screen overlay Esc/× | Task 5, 6 |
| IDE continue via SDK | Task 4 |
| Per-node sidecars | Task 1, 7 |
| Execution badge | Task 4, 6 |
| Full parity blocks | Task 3, 6 |
| Composer 2.5 fast off | Task 2 |
| Cancel/stop | Task 4, 6 |

No TBD placeholders remain in task steps above; implementers fill exact normalizer cases from cursor-sdk event samples during Task 3.

---

## Execution handoff

Plan saved to `docs/superpowers/plans/2026-09-06-cursor-agent-fullscreen-chat.md`.

**Two execution options:**

1. **Subagent-Driven (recommended)** — fresh subagent per task, review between tasks  
2. **Inline Execution** — implement tasks in this session with checkpoints

Which approach do you want?
