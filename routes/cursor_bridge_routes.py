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
    bridge_status,
    bridge_token,
    clear_api_key,
    dismiss_agent,
    dismissed_agent_ids,
    ensure_bridge_online,
    ensure_bridge_process,
    is_configured,
    is_plausible_cursor_api_key,
    list_ide_mirror_agents,
    save_api_key,
    stop_bridge_process,
)

logger = logging.getLogger(__name__)


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
        response = await bridge_request("POST", f"/agents/{agent_id}/send", json_body=body if isinstance(body, dict) else {})
        if response.status_code >= 400:
            detail = response.json().get("detail") if response.headers.get("content-type", "").startswith("application/json") else response.text
            raise HTTPException(status_code=response.status_code, detail=detail)
        return response.json()

    @router.get("/agents/{agent_id}/runs/{run_id}/stream")
    async def stream_agent_run(agent_id: str, run_id: str):
        if not is_configured():
            raise HTTPException(status_code=503, detail="cursor_bridge_not_configured")
        await ensure_bridge_online()
        headers = {"Authorization": f"Bearer {bridge_token()}", "Accept": "text/event-stream"}

        async def relay():
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream(
                    "GET",
                    f"{DEFAULT_URL}/agents/{agent_id}/runs/{run_id}/stream",
                    headers=headers,
                ) as upstream:
                    upstream.raise_for_status()
                    async for chunk in upstream.aiter_bytes():
                        yield chunk

        return StreamingResponse(relay(), media_type="text/event-stream")

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
    async def cancel_agent_run(agent_id: str, run_id: str) -> dict[str, Any]:
        if not is_configured():
            raise HTTPException(status_code=503, detail="cursor_bridge_not_configured")
        await ensure_bridge_online()
        response = await bridge_request("POST", f"/agents/{agent_id}/runs/{run_id}/cancel")
        response.raise_for_status()
        return response.json()

    return router
