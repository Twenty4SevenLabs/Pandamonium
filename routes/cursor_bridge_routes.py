"""Cursor bridge HTTP routes for Pandamonium."""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from core.middleware import require_admin
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
    is_plausible_cursor_api_key,
    list_ide_mirror_agents,
    save_api_key,
    stop_bridge_process,
)
from src.cursor_bridge_nodes import execution_host_for_node, resolve_execution_node, sidecar_url_for_node, workspace_cwd_from_slug

logger = logging.getLogger(__name__)


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


async def _ensure_sidecar_agent(agent_id: str, agent_meta: dict[str, Any]) -> None:
    probe = await bridge_request_for_agent("GET", f"/agents/{agent_id}/session", agent_meta)
    if probe.status_code == 200:
        payload = probe.json() if probe.headers.get("content-type", "").startswith("application/json") else {}
        if isinstance(payload, dict):
            source = str(payload.get("source") or "")
            status = str(payload.get("status") or "")
            if source == "bridge" and not payload.get("forked"):
                return
            if payload.get("forked") and status in {"idle", "running"}:
                return
            if payload.get("sdk_agent_id") and not payload.get("forked") and status in {"idle", "running"}:
                return

    ide_session = await fetch_ide_agent_session(agent_id)
    workspace = str(agent_meta.get("workspace") or "pandamonium")
    cwd = workspace_cwd_from_slug(workspace) or workspace_cwd_from_slug("pandamonium")
    body = {
        "workspace": workspace,
        "cwd": cwd,
        "title": agent_meta.get("title") or "Cursor agent",
        "source": "ide" if ide_session else str(agent_meta.get("source") or "bridge"),
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
    elif probe.status_code == 404 and str(agent_meta.get("source") or "").lower() == "bridge":
        raise HTTPException(status_code=404, detail="agent_not_found")

    response = await bridge_request_for_agent("POST", f"/agents/{agent_id}/resume", agent_meta, json_body=body)
    if response.status_code >= 400:
        detail = response.json().get("detail") if response.headers.get("content-type", "").startswith("application/json") else response.text
        raise HTTPException(status_code=response.status_code, detail=detail)


def _validate_api_key(value: object) -> str:
    if not isinstance(value, str):
        raise HTTPException(status_code=400, detail="A Cursor API key is required")
    token = value.strip()
    if not is_plausible_cursor_api_key(token):
        raise HTTPException(status_code=400, detail="The Cursor API key format is invalid")
    return token


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
        if not is_configured():
            raise HTTPException(status_code=503, detail="cursor_bridge_not_configured")
        await ensure_bridge_online()
        body = await request.json()
        response = await bridge_request("POST", "/agents", json_body=body if isinstance(body, dict) else {})
        if response.status_code >= 400:
            detail = response.json().get("detail") if response.headers.get("content-type", "").startswith("application/json") else response.text
            raise HTTPException(status_code=response.status_code, detail=detail)
        return response.json()

    @router.post("/agents/{agent_id}/send")
    async def send_agent(agent_id: str, request: Request) -> dict[str, Any]:
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
        await _ensure_sidecar_agent(agent_id, agent_meta)
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
        if not is_configured():
            raise HTTPException(status_code=503, detail="cursor_bridge_not_configured")
        await ensure_bridge_online()
        raw_path = str(body.get("path") or "").strip()
        if not raw_path:
            raise HTTPException(status_code=400, detail="path_required")
        workspace = str(body.get("workspace") or "pandamonium").strip()
        cwd = workspace_cwd_from_slug(workspace) or body.get("cwd")
        payload = {"path": raw_path, "cwd": cwd or "", "workspace": workspace}
        response = await bridge_request("POST", "/canvas/open", json_body=payload)
        if response.status_code >= 400:
            detail = response.json().get("detail") if response.headers.get("content-type", "").startswith("application/json") else response.text
            raise HTTPException(status_code=response.status_code, detail=detail)
        return response.json()

    return router
