#!/usr/bin/env python3
"""Always-on Cursor SDK bridge for Pandamonium."""

from __future__ import annotations

import asyncio
import hmac
import importlib.util
import json
import os
import sys
import time
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_GUARD_PATH = Path(__file__).resolve().parent / "subscription_guard.py"
_GUARD_SPEC = importlib.util.spec_from_file_location("cursor_subscription_guard", _GUARD_PATH)
assert _GUARD_SPEC and _GUARD_SPEC.loader
_guard = importlib.util.module_from_spec(_GUARD_SPEC)
_GUARD_SPEC.loader.exec_module(_guard)
REQUIRED_MODEL = _guard.REQUIRED_MODEL
SubscriptionGuardError = _guard.SubscriptionGuardError
assert_agent_options = _guard.assert_agent_options
assert_no_cloud_url = _guard.assert_no_cloud_url
title_from_prompt = _guard.title_from_prompt
validate_startup_models = _guard.validate_startup_models

try:
    from core.atomic_io import atomic_write_json
except ModuleNotFoundError:
    from atomic_io import atomic_write_json  # type: ignore

HOST = os.getenv("ODYSSEUS_CURSOR_BRIDGE_HOST", "127.0.0.1")
PORT = int(os.getenv("ODYSSEUS_CURSOR_BRIDGE_PORT", "8050"))
TOKEN_FILE = Path(os.getenv("ODYSSEUS_CURSOR_BRIDGE_TOKEN_FILE", "data/cursor-bridge/token"))
STATE_DIR = Path(os.getenv("ODYSSEUS_CURSOR_BRIDGE_STATE_DIR", "data/cursor-bridge"))
REGISTRY_FILE = STATE_DIR / "agents.json"
SETTINGS_FILE = STATE_DIR / "settings.json"
BRIDGE_PROTOCOL = "pandamonium.cursor-bridge.v1"
STARTED_AT = time.time()


def _load_workspaces() -> dict[str, str]:
    try:
        raw = json.loads(os.getenv("ODYSSEUS_CURSOR_WORKSPACES_JSON", "{}"))
    except json.JSONDecodeError:
        return {}
    if not isinstance(raw, dict):
        return {}
    result: dict[str, str] = {}
    for name, path in raw.items():
        logical = str(name or "").strip()
        resolved = Path(str(path or "")).expanduser().resolve()
        if logical and resolved.is_absolute() and resolved.is_dir():
            result[logical] = str(resolved)
    return result


WORKSPACES = _load_workspaces()
DEFAULT_WORKSPACE = next(iter(WORKSPACES), "")


def _token() -> str:
    try:
        return TOKEN_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def _authorized(header: str | None) -> bool:
    expected = _token()
    supplied = (header or "").removeprefix("Bearer ").strip()
    return bool(expected and supplied and hmac.compare_digest(expected, supplied))


def _require_auth(authorization: str | None = Header(default=None)) -> None:
    if not _authorized(authorization):
        raise HTTPException(status_code=401, detail="unauthorized")


def _load_registry() -> dict[str, dict[str, Any]]:
    try:
        payload = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _save_registry(payload: dict[str, dict[str, Any]]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
    atomic_write_json(str(REGISTRY_FILE), payload, indent=2)
    try:
        REGISTRY_FILE.chmod(0o600)
    except OSError:
        pass


def _dismissed_agent_ids() -> set[str]:
    try:
        payload = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    raw = payload.get("dismissed_agent_ids") if isinstance(payload, dict) else None
    if not isinstance(raw, list):
        return set()
    return {str(row).strip() for row in raw if str(row).strip()}


@dataclass
class BridgeState:
    client: Any | None = None
    api_key: str = ""
    guard_failed: str | None = None
    active_runs: dict[str, asyncio.Task] = field(default_factory=dict)
    run_events: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)


STATE = BridgeState()


async def _ensure_client() -> Any:
    if STATE.guard_failed:
        raise HTTPException(status_code=503, detail=STATE.guard_failed)
    if STATE.client is None:
        raise HTTPException(status_code=503, detail="cursor_bridge_not_ready")
    return STATE.client


def _public_agent(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "agent_id": row.get("agent_id"),
        "title": row.get("title") or "Cursor agent",
        "workspace": row.get("workspace"),
        "status": row.get("status") or "idle",
        "source": row.get("source") or "bridge",
        "run_id": row.get("run_id"),
        "updated_at": row.get("updated_at"),
        "error": row.get("error"),
    }


async def _append_event(run_id: str, event: dict[str, Any]) -> None:
    async with STATE.lock:
        bucket = STATE.run_events.setdefault(run_id, [])
        bucket.append(event)
        if len(bucket) > 500:
            del bucket[: len(bucket) - 500]


async def _update_registry(agent_id: str, **changes: Any) -> dict[str, Any]:
    async with STATE.lock:
        registry = _load_registry()
        row = dict(registry.get(agent_id) or {})
        row["agent_id"] = agent_id
        row.update(changes)
        row["updated_at"] = int(time.time())
        registry[agent_id] = row
        _save_registry(registry)
        return row


async def _consume_run(agent_id: str, run: Any) -> None:
    run_id = getattr(run, "run_id", None) or getattr(run, "id", None) or str(uuid.uuid4())
    await _update_registry(agent_id, status="running", run_id=run_id, error=None)
    try:
        async for message in run.messages():
            payload = {
                "type": getattr(message, "type", "message"),
                "created_at": int(time.time()),
            }
            if hasattr(message, "to_json"):
                payload["message"] = message.to_json()
            else:
                payload["message"] = str(message)
            await _append_event(str(run_id), payload)
        result = await run.wait()
        status = getattr(result, "status", None) or (result.get("status") if isinstance(result, dict) else "finished")
        terminal = "failed" if status == "error" else "idle"
        error = None
        if status == "error":
            error = "cursor_run_failed"
            terminal = "failed"
        await _update_registry(agent_id, status=terminal, error=error)
    except Exception as exc:
        await _update_registry(agent_id, status="failed", error=str(exc)[:240])
        await _append_event(str(run_id), {"type": "error", "text": str(exc)[:240]})
    finally:
        async with STATE.lock:
            STATE.active_runs.pop(str(run_id), None)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    api_key = os.getenv("CURSOR_API_KEY", "").strip()
    STATE.api_key = api_key
    if not api_key:
        yield
        return
    if not WORKSPACES:
        STATE.guard_failed = "cursor_workspaces_not_configured"
        yield
        return
    default_cwd = WORKSPACES.get(DEFAULT_WORKSPACE) or next(iter(WORKSPACES.values()))
    try:
        from cursor_sdk import AsyncClient

        client = await AsyncClient.launch_bridge(
            workspace=default_cwd,
            allow_api_key_env_fallback=False,
        )
        await validate_startup_models(client, api_key)
        STATE.client = client
    except SubscriptionGuardError as exc:
        STATE.guard_failed = exc.reason
    except Exception as exc:
        STATE.guard_failed = str(exc)[:240]
    try:
        yield
    finally:
        if STATE.client is not None:
            await STATE.client.aclose()
            STATE.client = None


app = FastAPI(title="Pandamonium Cursor Bridge", lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "ok": STATE.client is not None and not STATE.guard_failed,
        "protocol": BRIDGE_PROTOCOL,
        "model_lock": REQUIRED_MODEL,
        "uptime_seconds": int(time.time() - STARTED_AT),
        "guard_failed": STATE.guard_failed,
    }


@app.get("/status")
async def status(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    _require_auth(authorization)
    registry = _load_registry()
    return {
        "configured": bool(STATE.api_key),
        "connected": STATE.client is not None and not STATE.guard_failed,
        "model_lock": REQUIRED_MODEL,
        "workspaces": list(WORKSPACES),
        "agent_count": len(registry),
        "guard_failed": STATE.guard_failed,
        "protocol": BRIDGE_PROTOCOL,
    }


@app.get("/agents")
async def list_agents(
    authorization: str | None = Header(default=None),
    workspace: str | None = None,
    source: str = "bridge",
) -> dict[str, Any]:
    _require_auth(authorization)
    registry = _load_registry()
    hidden = _dismissed_agent_ids()
    items = [_public_agent(row) for row in registry.values() if str(row.get("agent_id") or "") not in hidden]
    if workspace:
        items = [row for row in items if row.get("workspace") == workspace]
    if source == "bridge":
        items = [row for row in items if row.get("source") == "bridge"]
    client = await _ensure_client()
    sdk_items: list[dict[str, Any]] = []
    target_workspace = workspace or DEFAULT_WORKSPACE
    cwd = WORKSPACES.get(target_workspace) if target_workspace else None
    if cwd:
        try:
            listed = await client.agents.list(runtime="local", cwd=cwd, api_key=STATE.api_key)
            raw_items = getattr(listed, "items", None) or []
            for info in raw_items:
                agent_id = getattr(info, "agent_id", None) or getattr(info, "id", None)
                if not agent_id:
                    continue
                agent_id = str(agent_id)
                if agent_id in hidden:
                    continue
                if agent_id not in registry:
                    registry[agent_id] = {
                        "agent_id": agent_id,
                        "title": "Cursor agent",
                        "workspace": target_workspace,
                        "status": "idle",
                        "source": "bridge",
                        "updated_at": int(time.time()),
                    }
                    _save_registry(registry)
                sdk_items.append(_public_agent(registry[agent_id]))
        except Exception:
            sdk_items = []
    merged = {row["agent_id"]: row for row in items}
    for row in sdk_items:
        merged[row["agent_id"]] = row
    ordered = sorted(merged.values(), key=lambda row: int(row.get("updated_at") or 0), reverse=True)
    return {"items": ordered}


@app.post("/agents")
async def create_agent(payload: dict[str, Any], authorization: str | None = Header(default=None)) -> dict[str, Any]:
    _require_auth(authorization)
    client = await _ensure_client()
    workspace = str(payload.get("workspace") or DEFAULT_WORKSPACE).strip()
    cwd = WORKSPACES.get(workspace)
    if not cwd:
        raise HTTPException(status_code=400, detail="unknown_workspace")
    prompt = str(payload.get("prompt") or "").strip()
    if not prompt or len(prompt) > 50_000:
        raise HTTPException(status_code=400, detail="invalid_prompt")
    title = str(payload.get("title") or title_from_prompt(prompt)).strip()[:120]
    options = assert_agent_options(
        {
            "api_key": STATE.api_key,
            "model": REQUIRED_MODEL,
            "local": {"cwd": cwd, "setting_sources": []},
        }
    )
    try:
        agent = await client.create_agent(options)
        agent_id = getattr(agent, "agent_id", None) or getattr(agent, "id", None)
        if not agent_id:
            raise HTTPException(status_code=502, detail="cursor_agent_missing")
        await _update_registry(
            str(agent_id),
            title=title,
            workspace=workspace,
            status="running",
            source="bridge",
            error=None,
        )
        run = await agent.send(prompt)
        run_id = getattr(run, "run_id", None) or getattr(run, "id", None)
        task = asyncio.create_task(_consume_run(str(agent_id), run))
        async with STATE.lock:
            if run_id:
                STATE.active_runs[str(run_id)] = task
        return {"agent": _public_agent(_load_registry()[str(agent_id)]), "run_id": run_id}
    except SubscriptionGuardError as exc:
        raise HTTPException(status_code=403, detail=exc.reason) from exc


@app.post("/agents/{agent_id}/send")
async def send_agent(agent_id: str, payload: dict[str, Any], authorization: str | None = Header(default=None)) -> dict[str, Any]:
    _require_auth(authorization)
    client = await _ensure_client()
    registry = _load_registry()
    row = registry.get(agent_id)
    if not row:
        raise HTTPException(status_code=404, detail="agent_not_found")
    prompt = str(payload.get("prompt") or "").strip()
    if not prompt or len(prompt) > 50_000:
        raise HTTPException(status_code=400, detail="invalid_prompt")
    workspace = str(row.get("workspace") or DEFAULT_WORKSPACE)
    cwd = WORKSPACES.get(workspace)
    if not cwd:
        raise HTTPException(status_code=400, detail="unknown_workspace")
    options = assert_agent_options(
        {
            "api_key": STATE.api_key,
            "model": REQUIRED_MODEL,
            "local": {"cwd": cwd, "setting_sources": []},
        }
    )
    try:
        agent = await client.resume_agent(agent_id, options)
        run = await agent.send(prompt)
        run_id = getattr(run, "run_id", None) or getattr(run, "id", None)
        await _update_registry(agent_id, status="running", run_id=run_id, error=None)
        task = asyncio.create_task(_consume_run(agent_id, run))
        async with STATE.lock:
            if run_id:
                STATE.active_runs[str(run_id)] = task
        return {"agent": _public_agent(_load_registry()[agent_id]), "run_id": run_id}
    except SubscriptionGuardError as exc:
        await _update_registry(agent_id, status="failed", error=exc.reason)
        raise HTTPException(status_code=403, detail=exc.reason) from exc


@app.get("/agents/{agent_id}/runs/{run_id}/stream")
async def stream_run(agent_id: str, run_id: str, authorization: str | None = Header(default=None)):
    _require_auth(authorization)

    async def event_source():
        seen = 0
        while True:
            async with STATE.lock:
                events = list(STATE.run_events.get(run_id, []))
            for event in events[seen:]:
                seen += 1
                yield f"data: {json.dumps(event, ensure_ascii=True)}\n\n"
            registry = _load_registry()
            row = registry.get(agent_id) or {}
            if row.get("status") not in {"running"} and seen >= len(events):
                break
            await asyncio.sleep(0.4)

    return StreamingResponse(event_source(), media_type="text/event-stream")


@app.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    _require_auth(authorization)
    registry = _load_registry()
    row = registry.get(agent_id)
    if not row:
        raise HTTPException(status_code=404, detail="agent_not_found")
    run_id = str(row.get("run_id") or "")
    if run_id:
        task = STATE.active_runs.get(run_id)
        if task and not task.done():
            task.cancel()
        async with STATE.lock:
            STATE.active_runs.pop(run_id, None)
            STATE.run_events.pop(run_id, None)
    registry.pop(agent_id, None)
    _save_registry(registry)
    try:
        payload = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    dismissed = _dismissed_agent_ids()
    dismissed.add(agent_id)
    payload["dismissed_agent_ids"] = sorted(dismissed)
    atomic_write_json(str(SETTINGS_FILE), payload, indent=2)
    return {"removed": True, "agent_id": agent_id}


@app.post("/agents/{agent_id}/runs/{run_id}/cancel")
async def cancel_run(agent_id: str, run_id: str, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    _require_auth(authorization)
    client = await _ensure_client()
    try:
        run = await client.get_run(run_id, runtime="local", agent_id=agent_id, api_key=STATE.api_key)
        if hasattr(run, "supports") and run.supports("cancel"):
            await run.cancel()
        await _update_registry(agent_id, status="idle")
        return {"cancelled": True}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)[:240]) from exc


@app.exception_handler(SubscriptionGuardError)
async def guard_handler(_request, exc: SubscriptionGuardError):
    return JSONResponse(status_code=403, content={"error": exc.code, "reason": exc.reason})


def main() -> None:
    import uvicorn

    hosts = tuple(part.strip() for part in os.getenv("ODYSSEUS_CURSOR_BRIDGE_HOSTS", HOST).split(",") if part.strip())
    if not hosts or any(host in {"0.0.0.0", "::"} for host in hosts):
        raise RuntimeError("bridge_hosts_must_be_explicit")
    host = hosts[0]
    uvicorn.run(app, host=host, port=PORT, log_level="warning")


if __name__ == "__main__":
    main()
