"""Async HTTP helpers for proxying Cursor canvas server through Panda."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import re

import httpx

_MODULE_PATH = Path(__file__).resolve().parent / "canvas_bridge.py"
_CANVAS_RELAY_PATH = re.compile(r"^canvas/[a-f0-9]{12}(?:/.*)?$")
_RELAY_TIMEOUT = httpx.Timeout(60.0, connect=5.0)
_spec = importlib.util.spec_from_file_location("cursor_bridge_canvas", _MODULE_PATH)
assert _spec and _spec.loader
canvas = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(canvas)


TEXTUAL_SUFFIXES = (".js", ".html", ".json", ".css", ".mjs")
TEXTUAL_CONTENT_TYPES = (
    "text/",
    "application/javascript",
    "application/json",
    "application/ecmascript",
)


def is_allowed_relay_path(upstream_path: str) -> bool:
    clean = str(upstream_path or "").lstrip("/")
    if not clean or ".." in Path(clean).parts:
        return False
    lowered = clean.lower()
    if lowered.startswith("canvas-admin") or "/canvas-admin" in lowered:
        return False
    if _CANVAS_RELAY_PATH.fullmatch(clean):
        return True
    return lowered.startswith("runtime/")


def _should_rewrite(content_type: str, path: str) -> bool:
    lowered = str(content_type or "").lower()
    if any(lowered.startswith(prefix) for prefix in TEXTUAL_CONTENT_TYPES):
        return True
    return path.endswith(TEXTUAL_SUFFIXES) or path.endswith("/")


async def ensure_canvas_registered(path: str, *, state: dict[str, Any] | None = None) -> dict[str, Any]:
    row = state or canvas.load_canvas_server_state()
    if not row:
        return {"registered": False, "reason": "canvas_server_unavailable"}
    canvas_id = canvas.canvas_id_for_path(path)
    base = canvas.canvas_server_base_url(row)
    token = str(row.get("sessionToken") or "")
    if not base or not token:
        return {"registered": False, "reason": "canvas_server_unavailable", "canvas_id": canvas_id}
    page_url = f"{base}/canvas/{canvas_id}/?{urlencode({'token': token})}"
    register_url = f"{base}/canvas-admin/register?{urlencode({'token': token})}"
    async with httpx.AsyncClient(timeout=_RELAY_TIMEOUT, follow_redirects=False) as client:
        probe = await client.get(page_url)
        if probe.status_code == 200 and "Canvas not found" not in probe.text:
            return {"registered": True, "canvas_id": canvas_id, "already": True}
        response = await client.post(register_url, json={"path": path})
        if response.status_code >= 400:
            return {
                "registered": False,
                "canvas_id": canvas_id,
                "reason": response.text[:240] or "register_failed",
                "status_code": response.status_code,
            }
        return {"registered": True, "canvas_id": canvas_id, "payload": response.json()}


async def proxy_canvas_request(
    upstream_path: str,
    *,
    method: str = "GET",
    body: bytes | None = None,
    headers: dict[str, str] | None = None,
    state: dict[str, Any] | None = None,
) -> tuple[int, dict[str, str], bytes]:
    if not is_allowed_relay_path(upstream_path):
        return 403, {"Content-Type": "application/json"}, b'{"error":"canvas_relay_path_forbidden"}'
    row = state or canvas.load_canvas_server_state()
    url = canvas.upstream_canvas_url(upstream_path, state=row)
    if not url or not row:
        return 503, {"Content-Type": "application/json"}, b'{"error":"canvas_server_unavailable"}'
    request_headers = {"Accept": "*/*"}
    if headers:
        for key in ("Accept", "Accept-Language", "Content-Type"):
            value = headers.get(key)
            if value:
                request_headers[key] = value
    async with httpx.AsyncClient(timeout=_RELAY_TIMEOUT, follow_redirects=False) as client:
        response = await client.request(method.upper(), url, content=body, headers=request_headers)
    content = response.content
    out_headers = {
        key: value
        for key, value in response.headers.items()
        if key.lower() not in {"transfer-encoding", "content-encoding", "connection", "keep-alive"}
    }
    path = upstream_path.lstrip("/")
    if _should_rewrite(out_headers.get("Content-Type", ""), path):
        try:
            text = content.decode(response.encoding or "utf-8", errors="replace")
            text = canvas.rewrite_relay_content(text)
            content = text.encode("utf-8")
            out_headers["Content-Type"] = out_headers.get("Content-Type") or "text/plain; charset=utf-8"
        except UnicodeDecodeError:
            pass
    return response.status_code, out_headers, content
