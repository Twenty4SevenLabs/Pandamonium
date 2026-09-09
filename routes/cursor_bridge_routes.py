"""Cursor bridge HTTP routes for Pandamonium."""

from __future__ import annotations

import importlib.util
import json
import logging
import os
import re
from pathlib import Path
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response, StreamingResponse

from core.middleware import require_admin
from src.auth_helpers import get_current_user
from src.cursor_bridge_manager import (
    DEFAULT_URL,
    bridge_request,
    bridge_request_for_agent,
    bridge_status,
    bridge_token,
    clear_api_key,
    dismiss_agent,
    dismissed_agent_ids,
    ensure_bridge_online,
    ensure_bridge_process,
    fetch_ide_agent_session,
    is_configured,
    is_ide_transcript_agent_id,
    is_plausible_cursor_api_key,
    list_ide_mirror_agents,
    save_api_key,
    stop_bridge_process,
)
from src.cursor_bridge_nodes import execution_host_for_node, is_allowed_agent_cwd, resolve_execution_node, sidecar_url_for_node, workspace_cwd_from_slug

logger = logging.getLogger(__name__)

_CANVAS_BRIDGE_PATH = Path(__file__).resolve().parents[1] / "services" / "cursor-bridge" / "canvas_bridge.py"
_CANVAS_RELAY_PATH = Path(__file__).resolve().parents[1] / "services" / "cursor-bridge" / "canvas_relay.py"
_canvas_bridge = None
_canvas_relay = None


def _load_canvas_bridge():
    global _canvas_bridge
    if _canvas_bridge is not None:
        return _canvas_bridge
    spec = importlib.util.spec_from_file_location("panda_cursor_bridge_canvas", _CANVAS_BRIDGE_PATH)
    if not spec or not spec.loader:
        raise RuntimeError("canvas_bridge_unavailable")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _canvas_bridge = mod
    return mod


def _load_canvas_relay():
    global _canvas_relay
    if _canvas_relay is not None:
        return _canvas_relay
    spec = importlib.util.spec_from_file_location("panda_cursor_bridge_canvas_relay", _CANVAS_RELAY_PATH)
    if not spec or not spec.loader:
        raise RuntimeError("canvas_relay_unavailable")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _canvas_relay = mod
    return mod


def _enrich_execution_meta(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return payload
    node = resolve_execution_node(payload)
    payload["execution_node"] = node
    payload["execution_host"] = execution_host_for_node(node)
    payload["can_send"] = is_configured() and payload.get("can_send", True) is not False
    payload["read_only"] = False
    payload["model_lock"] = "composer-2.5"
    payload["fast_mode"] = False
    return payload


def _merge_session_messages(
    ide_messages: list[dict[str, Any]],
    sidecar_messages: list[dict[str, Any]],
    *,
    forked: bool,
    status: str,
) -> list[dict[str, Any]]:
    ide = list(ide_messages or [])
    side = list(sidecar_messages or [])
    if not ide:
        return side
    if not side:
        return ide
    if forked or status in {"running", "failed"}:
        return side
    if len(side) > len(ide):
        return side
    if len(ide) > len(side):
        return ide
    if side[-1] != ide[-1]:
        return side
    return ide


async def _require_forked_sidecar(agent_id: str, agent_meta: dict[str, Any]) -> None:
    probe = await bridge_request_for_agent("GET", f"/agents/{agent_id}/session", agent_meta)
    if probe.status_code == 200:
        payload = probe.json() if probe.headers.get("content-type", "").startswith("application/json") else {}
        if isinstance(payload, dict):
            source = str(payload.get("source") or "")
            status = str(payload.get("status") or "")
            if payload.get("forked") and status in {"idle", "running"}:
                return
            if source == "bridge" and not is_ide_transcript_agent_id(agent_id):
                return
            if payload.get("sdk_agent_id") and payload.get("forked"):
                return

    ide_session = await fetch_ide_agent_session(agent_id)
    if ide_session or is_ide_transcript_agent_id(agent_id):
        raise HTTPException(status_code=409, detail="ide_fork_required")

    if probe.status_code == 404 and str(agent_meta.get("source") or "").lower() == "bridge":
        raise HTTPException(status_code=404, detail="agent_not_found")


async def _fork_ide_sidecar(agent_id: str, agent_meta: dict[str, Any]) -> dict[str, Any]:
    ide_session = await fetch_ide_agent_session(agent_id)
    workspace = str(agent_meta.get("workspace") or "pandamonium")
    cwd = workspace_cwd_from_slug(workspace) or workspace_cwd_from_slug("pandamonium")
    body: dict[str, Any] = {
        "workspace": workspace,
        "cwd": cwd,
        "title": agent_meta.get("title") or "Cursor agent",
        "source": "ide" if ide_session else str(agent_meta.get("source") or "ide"),
    }
    if isinstance(ide_session, dict):
        body["title"] = ide_session.get("title") or body["title"]
        body["workspace"] = ide_session.get("workspace") or body["workspace"]
        ide_cwd = workspace_cwd_from_slug(str(body["workspace"]))
        if ide_cwd:
            body["cwd"] = ide_cwd
        messages = ide_session.get("messages")
        if isinstance(messages, list) and messages:
            body["messages"] = messages
        agent_meta["source"] = "ide"
        mirror_url = ide_session.get("mirror_url")
        if mirror_url and not agent_meta.get("mirror_url"):
            agent_meta["mirror_url"] = str(mirror_url)
    if not body.get("messages"):
        raise HTTPException(status_code=400, detail="messages_required_for_fork")

    response = await bridge_request_for_agent("POST", f"/agents/{agent_id}/fork", agent_meta, json_body=body)
    if response.status_code >= 400:
        detail = response.json().get("detail") if response.headers.get("content-type", "").startswith("application/json") else response.text
        raise HTTPException(status_code=response.status_code, detail=detail)
    payload = response.json()
    return payload if isinstance(payload, dict) else {}


def _validate_api_key(value: object) -> str:
    if not isinstance(value, str):
        raise HTTPException(status_code=400, detail="A Cursor API key is required")
    token = value.strip()
    if not is_plausible_cursor_api_key(token):
        raise HTTPException(status_code=400, detail="The Cursor API key format is invalid")
    return token


CURSOR_READ_SCOPES = {"cursor:read", "cursor:write"}
CURSOR_WRITE_SCOPES = {"cursor:write"}


def _require_cursor_scope(
    request: Request,
    allowed: set[str],
    *,
    admin_for_session: bool = False,
) -> str:
    """Authorize Cursor bridge routes.

    API tokens must carry one of ``allowed``. Cookie sessions need a login;
    mutations also require admin, matching ``/connect``.
    """
    if getattr(request.state, "api_token", False):
        scopes = set(getattr(request.state, "api_token_scopes", []) or [])
        if not scopes.intersection(allowed):
            required = " or ".join(sorted(allowed))
            raise HTTPException(status_code=403, detail=f"API token missing required scope: {required}")
        owner = getattr(request.state, "api_token_owner", None)
        if not owner:
            raise HTTPException(status_code=403, detail="API token has no owner")
        return str(owner)
    if admin_for_session:
        require_admin(request)
        return get_current_user(request) or ""
    return get_current_user(request) or ""


def setup_cursor_bridge_routes() -> APIRouter:
    router = APIRouter(prefix="/api/cursor", tags=["cursor"])

    @router.get("/status")
    async def cursor_status(_request: Request) -> dict[str, Any]:
        status = await bridge_status()
        status["model_lock"] = "composer-2.5"
        return status

    @router.post("/connect")
    async def connect_cursor(request: Request) -> dict[str, Any]:
        require_admin(request)
        try:
            body = await request.json()
        except (ValueError, json.JSONDecodeError) as exc:
            raise HTTPException(status_code=400, detail="A JSON request body is required") from exc
        api_key = _validate_api_key(body.get("api_key") if isinstance(body, dict) else None)
        save_api_key(api_key)
        stop_bridge_process()
        ensure_bridge_process()
        health = await ensure_bridge_online()
        if not health.get("ok"):
            clear_api_key()
            stop_bridge_process()
            raise HTTPException(
                status_code=502,
                detail=health.get("guard_failed") or health.get("error") or "Cursor bridge failed to start",
            )
        status = await bridge_status()
        status["model_lock"] = "composer-2.5"
        return status

    @router.delete("/connect")
    async def disconnect_cursor(request: Request) -> dict[str, Any]:
        require_admin(request)
        clear_api_key()
        stop_bridge_process()
        return {"configured": False, "status": "disconnected", "connected": False}

    @router.get("/agents")
    async def list_agents(
        request: Request,
        workspace: str | None = None,
        source: str = "all",
    ) -> dict[str, Any]:
        _require_cursor_scope(request, CURSOR_READ_SCOPES)
        if not is_configured():
            return {"items": [], "configured": False}
        await ensure_bridge_online()
        params = []
        if workspace:
            params.append(f"workspace={workspace}")
        if source:
            params.append(f"source={source}")
        query = ("?" + "&".join(params)) if params else ""
        response = await bridge_request("GET", f"/agents{query}")
        if response.status_code == 401:
            bridge_token()
            response = await bridge_request("GET", f"/agents{query}")
        response.raise_for_status()
        payload = response.json()
        items = payload.get("items") if isinstance(payload, dict) else []
        if source == "all":
            hidden = dismissed_agent_ids()
            ide_items = [row for row in await list_ide_mirror_agents() if str(row.get("agent_id") or "") not in hidden]
            merged = {
                str(row.get("agent_id")): row
                for row in items
                if isinstance(row, dict) and str(row.get("agent_id") or "") not in hidden
            }
            for row in ide_items:
                merged[str(row.get("agent_id"))] = row
            payload["items"] = sorted(
                merged.values(),
                key=lambda row: int(row.get("updated_at") or 0),
                reverse=True,
            )
        payload["configured"] = True
        return payload

    @router.post("/agents")
    async def create_agent(request: Request) -> dict[str, Any]:
        _require_cursor_scope(request, CURSOR_WRITE_SCOPES, admin_for_session=True)
        if not is_configured():
            raise HTTPException(status_code=503, detail="cursor_bridge_not_configured")
        await ensure_bridge_online()
        body = await request.json()
        response = await bridge_request("POST", "/agents", json_body=body if isinstance(body, dict) else {})
        if response.status_code >= 400:
            detail = response.json().get("detail") if response.headers.get("content-type", "").startswith("application/json") else response.text
            raise HTTPException(status_code=response.status_code, detail=detail)
        return response.json()

    @router.post("/agents/{agent_id}/fork")
    async def fork_agent(agent_id: str, request: Request) -> dict[str, Any]:
        _require_cursor_scope(request, CURSOR_WRITE_SCOPES, admin_for_session=True)
        if not is_configured():
            raise HTTPException(status_code=503, detail="cursor_bridge_not_configured")
        await ensure_bridge_online()
        body = await request.json()
        source = str(request.query_params.get("source") or (body.get("source") if isinstance(body, dict) else "") or "ide").strip().lower()
        mirror_url = str(request.query_params.get("mirror_url") or (body.get("mirror_url") if isinstance(body, dict) else "") or "")
        agent_meta = {
            "agent_id": agent_id,
            "source": source or "ide",
            "mirror_url": mirror_url,
            "workspace": (body.get("workspace") if isinstance(body, dict) else None) or "pandamonium",
            "title": (body.get("title") if isinstance(body, dict) else None) or "Cursor agent",
        }
        payload = await _fork_ide_sidecar(agent_id, agent_meta)
        if isinstance(payload.get("agent"), dict):
            _enrich_execution_meta(payload["agent"])
        return payload

    @router.post("/agents/{agent_id}/send")
    async def send_agent(agent_id: str, request: Request) -> dict[str, Any]:
        _require_cursor_scope(request, CURSOR_WRITE_SCOPES, admin_for_session=True)
        if not is_configured():
            raise HTTPException(status_code=503, detail="cursor_bridge_not_configured")
        await ensure_bridge_online()
        body = await request.json()
        source = str(request.query_params.get("source") or (body.get("source") if isinstance(body, dict) else "") or "").strip().lower()
        mirror_url = str(request.query_params.get("mirror_url") or (body.get("mirror_url") if isinstance(body, dict) else "") or "")
        agent_meta = {
            "agent_id": agent_id,
            "source": source or "bridge",
            "mirror_url": mirror_url,
            "workspace": (body.get("workspace") if isinstance(body, dict) else None) or "pandamonium",
            "title": (body.get("title") if isinstance(body, dict) else None) or "Cursor agent",
        }
        await _require_forked_sidecar(agent_id, agent_meta)
        response = await bridge_request_for_agent(
            "POST",
            f"/agents/{agent_id}/send",
            agent_meta,
            json_body=body if isinstance(body, dict) else {},
        )
        if response.status_code >= 400:
            detail = response.json().get("detail") if response.headers.get("content-type", "").startswith("application/json") else response.text
            raise HTTPException(status_code=response.status_code, detail=detail)
        payload = response.json()
        if isinstance(payload, dict) and isinstance(payload.get("agent"), dict):
            _enrich_execution_meta(payload["agent"])
        return payload

    @router.get("/agents/{agent_id}/runs/{run_id}/stream")
    async def stream_agent_run(agent_id: str, run_id: str, request: Request):
        _require_cursor_scope(request, CURSOR_READ_SCOPES)
        if not is_configured():
            raise HTTPException(status_code=503, detail="cursor_bridge_not_configured")
        await ensure_bridge_online()
        source = str(request.query_params.get("source") or "bridge").strip().lower()
        mirror_url = str(request.query_params.get("mirror_url") or "")
        agent_meta = {"agent_id": agent_id, "source": source, "mirror_url": mirror_url}
        node = resolve_execution_node(agent_meta)
        base_url = sidecar_url_for_node(node)
        headers = {"Authorization": f"Bearer {bridge_token()}", "Accept": "text/event-stream"}

        async def relay():
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream(
                    "GET",
                    f"{base_url}/agents/{agent_id}/runs/{run_id}/stream",
                    headers=headers,
                ) as upstream:
                    upstream.raise_for_status()
                    async for chunk in upstream.aiter_bytes():
                        yield chunk

        return StreamingResponse(relay(), media_type="text/event-stream")

    @router.get("/agents/{agent_id}/session")
    async def agent_session(agent_id: str, request: Request) -> dict[str, Any]:
        _require_cursor_scope(request, CURSOR_READ_SCOPES)
        if not is_configured():
            raise HTTPException(status_code=503, detail="cursor_bridge_not_configured")
        source = str(request.query_params.get("source") or "").strip().lower()
        mirror_url = str(request.query_params.get("mirror_url") or "")
        agent_meta = {"agent_id": agent_id, "source": source or "ide", "mirror_url": mirror_url}
        ide_session = None
        if source == "ide" or not source:
            ide_session = await fetch_ide_agent_session(agent_id)
            if ide_session:
                ide_session["source"] = "ide"
                if mirror_url:
                    ide_session["mirror_url"] = mirror_url
                elif ide_session.get("mirror_url"):
                    agent_meta["mirror_url"] = ide_session["mirror_url"]
        await ensure_bridge_online()
        response = await bridge_request_for_agent("GET", f"/agents/{agent_id}/session", agent_meta)
        if response.status_code == 200:
            payload = response.json()
            if ide_session and isinstance(payload, dict):
                ide_messages = ide_session.get("messages") if isinstance(ide_session.get("messages"), list) else []
                sidecar_messages = payload.get("messages") if isinstance(payload.get("messages"), list) else []
                payload["messages"] = _merge_session_messages(
                    ide_messages,
                    sidecar_messages,
                    forked=bool(payload.get("forked")),
                    status=str(payload.get("status") or ""),
                )
                payload["source"] = payload.get("source") or "ide"
            return _enrich_execution_meta(payload if isinstance(payload, dict) else {})
        if ide_session:
            return _enrich_execution_meta(ide_session)
        if source == "ide":
            raise HTTPException(status_code=404, detail="agent_not_found")
        if response.status_code >= 400:
            detail = response.json().get("detail") if response.headers.get("content-type", "").startswith("application/json") else response.text
            raise HTTPException(status_code=response.status_code, detail=detail)
        raise HTTPException(status_code=404, detail="agent_not_found")

    @router.delete("/agents/{agent_id}")
    async def remove_agent(agent_id: str, request: Request) -> dict[str, Any]:
        _require_cursor_scope(request, CURSOR_WRITE_SCOPES, admin_for_session=True)
        if not is_configured():
            raise HTTPException(status_code=503, detail="cursor_bridge_not_configured")
        await ensure_bridge_online()
        source = str(request.query_params.get("source") or "bridge").strip().lower()
        if source == "ide":
            dismiss_agent(agent_id)
            return {"removed": True, "agent_id": agent_id, "source": "ide"}
        response = await bridge_request("DELETE", f"/agents/{agent_id}")
        if response.status_code == 404:
            dismiss_agent(agent_id)
            return {"removed": True, "agent_id": agent_id, "source": "bridge"}
        if response.status_code >= 400:
            detail = response.json().get("detail") if response.headers.get("content-type", "").startswith("application/json") else response.text
            raise HTTPException(status_code=response.status_code, detail=detail)
        dismiss_agent(agent_id)
        return response.json()

    @router.post("/agents/{agent_id}/runs/{run_id}/cancel")
    async def cancel_agent_run(agent_id: str, run_id: str, request: Request) -> dict[str, Any]:
        _require_cursor_scope(request, CURSOR_WRITE_SCOPES, admin_for_session=True)
        if not is_configured():
            raise HTTPException(status_code=503, detail="cursor_bridge_not_configured")
        await ensure_bridge_online()
        source = str(request.query_params.get("source") or "bridge").strip().lower()
        mirror_url = str(request.query_params.get("mirror_url") or "")
        agent_meta = {"agent_id": agent_id, "source": source, "mirror_url": mirror_url}
        response = await bridge_request_for_agent("POST", f"/agents/{agent_id}/runs/{run_id}/cancel", agent_meta)
        response.raise_for_status()
        return response.json()

    @router.post("/canvas/open")
    async def open_canvas(request: Request, body: dict[str, Any]) -> dict[str, Any]:
        _require_cursor_scope(request, CURSOR_WRITE_SCOPES, admin_for_session=True)
        if not is_configured():
            raise HTTPException(status_code=503, detail="cursor_bridge_not_configured")
        raw_path = str(body.get("path") or "").strip()
        if not raw_path:
            raise HTTPException(status_code=400, detail="path_required")
        workspace = str(body.get("workspace") or "pandamonium").strip()
        cwd = str(body.get("cwd") or "").strip()
        if cwd and not is_allowed_agent_cwd(cwd):
            cwd = ""
        if not cwd:
            cwd = workspace_cwd_from_slug(workspace) or ""
        canvas = _load_canvas_bridge()
        relay = _load_canvas_relay()
        resolved = canvas.resolve_canvas_path(raw_path, cwd=cwd)
        if not resolved:
            raise HTTPException(status_code=404, detail="canvas_not_found")
        state = canvas.load_canvas_server_state()
        registration = None
        if state:
            registration = await relay.ensure_canvas_registered(str(resolved), state=state)
            if not registration.get("registered"):
                logger.warning("canvas_register_failed path=%s reason=%s", resolved, registration.get("reason"))
        public_url = os.getenv("APP_PUBLIC_URL", "").strip()
        payload = canvas.build_canvas_open_payload(resolved, app_public_url=public_url)
        if registration:
            payload["registration"] = registration
        return payload

    @router.get("/canvas/embed/{canvas_id}")
    async def embed_canvas(canvas_id: str, request: Request) -> Response:
        _require_cursor_scope(request, CURSOR_READ_SCOPES)
        canvas = _load_canvas_bridge()
        relay = _load_canvas_relay()
        if not re.fullmatch(r"[a-f0-9]{12}", str(canvas_id or "")):
            raise HTTPException(status_code=400, detail="invalid_canvas_id")
        status, headers, content = await relay.proxy_canvas_request(f"canvas/{canvas_id}/")
        return Response(content=content, status_code=status, headers=headers)

    @router.api_route("/canvas/relay/{relay_path:path}", methods=["GET", "POST", "HEAD"])
    async def relay_canvas(relay_path: str, request: Request) -> Response:
        _require_cursor_scope(request, CURSOR_READ_SCOPES)
        relay = _load_canvas_relay()
        body = await request.body() if request.method in {"POST"} else None
        status, headers, content = await relay.proxy_canvas_request(
            relay_path,
            method=request.method,
            body=body,
            headers={
                "Accept": request.headers.get("Accept", "*/*"),
                "Accept-Language": request.headers.get("Accept-Language", ""),
                "Content-Type": request.headers.get("Content-Type", ""),
            },
        )
        return Response(content=content, status_code=status, headers=headers)

    return router
