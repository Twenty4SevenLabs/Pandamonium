"""Security regressions for Cursor bridge High/Medium findings."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, HTTPException
from starlette.testclient import TestClient

from routes.api_token_routes import ALLOWED_SCOPES, _normalize_scopes
from routes.cursor_bridge_routes import setup_cursor_bridge_routes
from src.cursor_bridge_nodes import workspace_cwd_from_slug
from tests.test_cursor_bridge_canvas import _load_module as _load_canvas_module

ROOT = Path(__file__).resolve().parents[1]
RELAY_PATH = ROOT / "services" / "cursor-bridge" / "canvas_relay.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _cookie_request(*, current_user="bob", is_admin=False):
    auth_mgr = SimpleNamespace(
        is_configured=True,
        is_admin=lambda user: is_admin and user == current_user,
    )
    return SimpleNamespace(
        state=SimpleNamespace(current_user=current_user, api_token=False),
        app=SimpleNamespace(state=SimpleNamespace(auth_manager=auth_mgr)),
        headers={},
        client=SimpleNamespace(host="192.168.1.10"),
    )


def _api_token_request(*, scopes=None, owner="alice"):
    return SimpleNamespace(
        state=SimpleNamespace(
            current_user="api",
            api_token=True,
            api_token_scopes=scopes or [],
            api_token_owner=owner,
        ),
        app=SimpleNamespace(state=SimpleNamespace(auth_manager=None)),
        headers={},
        client=SimpleNamespace(host="192.168.1.10"),
    )


def test_canvas_open_payload_omits_session_token(tmp_path: Path, monkeypatch):
    mod = _load_canvas_module()
    monkeypatch.setattr(mod, "SYNC_SCRIPT", tmp_path / "missing-sync.py")
    monkeypatch.setattr(mod, "PROJECTS_ROOT", tmp_path)
    allowed = tmp_path / "canvases" / "demo.canvas.tsx"
    allowed.parent.mkdir()
    allowed.write_text("export default function Demo() { return null; }\n", encoding="utf-8")
    monkeypatch.setattr(
        mod,
        "load_canvas_server_state",
        lambda: {"host": "127.0.0.1", "port": 36659, "sessionToken": "abc123", "token": "abc123"},
    )
    payload = mod.build_canvas_open_payload(allowed, app_public_url="https://panda.example")
    blob = str(payload)
    assert "abc123" not in blob
    assert "sessionToken" not in (payload.get("canvas_server") or {})
    assert "token" not in (payload.get("canvas_server") or {})
    assert payload["embed_url"].startswith("/api/cursor/canvas/embed/")


def test_workspace_slug_rejects_parent_traversal(monkeypatch):
    monkeypatch.delenv("PANDAMONIUM_CURSOR_WORKSPACES_JSON", raising=False)
    monkeypatch.delenv("ODYSSEUS_CURSOR_WORKSPACES_JSON", raising=False)
    monkeypatch.delenv("PANDAMONIUM_CURSOR_WORKSPACE_FALLBACK_ROOT", raising=False)
    assert workspace_cwd_from_slug("mnt-dev-env-projects-../../../home/labsadmin") is None
    assert workspace_cwd_from_slug("mnt-dev-env-projects-..") is None
    assert workspace_cwd_from_slug("../etc") is None
    assert workspace_cwd_from_slug("mnt-dev-env-projects-foo/bar") is None


def test_workspace_slug_still_maps_safe_project(monkeypatch):
    monkeypatch.delenv("PANDAMONIUM_CURSOR_WORKSPACES_JSON", raising=False)
    monkeypatch.delenv("ODYSSEUS_CURSOR_WORKSPACES_JSON", raising=False)
    assert workspace_cwd_from_slug("mnt-dev-env-projects-pandamonium") == "/mnt/dev-env/projects/pandamonium"


def test_sidecar_resolve_cwd_rejects_escape():
    from src.cursor_bridge_nodes import resolve_agent_cwd

    assert resolve_agent_cwd("pandamonium", explicit_cwd="/tmp") == ""
    assert resolve_agent_cwd("mnt-dev-env-projects-../../../etc") == ""
    cwd = resolve_agent_cwd("mnt-dev-env-projects-pandamonium")
    assert cwd in {"", "/mnt/dev-env/projects/pandamonium"}
    if cwd:
        assert Path(cwd).resolve().is_relative_to(Path("/mnt/dev-env/projects").resolve())


@pytest.mark.asyncio
async def test_canvas_relay_blocks_admin_paths():
    relay = _load(RELAY_PATH, "cursor_bridge_canvas_relay_security")
    with patch.object(relay.httpx, "AsyncClient") as client_cls:
        status, _headers, body = await relay.proxy_canvas_request("canvas-admin/register")
    assert status == 403
    assert b"canvas_relay_path_forbidden" in body
    client_cls.assert_not_called()


@pytest.mark.asyncio
async def test_canvas_relay_disables_redirects_and_allowlists_canvas():
    relay = _load(RELAY_PATH, "cursor_bridge_canvas_relay_redirects")
    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.content = b"ok"
    fake_response.headers = {"Content-Type": "text/plain"}
    fake_response.encoding = "utf-8"
    fake_client = AsyncMock()
    fake_client.request = AsyncMock(return_value=fake_response)
    fake_client.__aenter__ = AsyncMock(return_value=fake_client)
    fake_client.__aexit__ = AsyncMock(return_value=None)
    state = {"host": "127.0.0.1", "port": 9, "sessionToken": "secret"}
    with patch.object(relay.httpx, "AsyncClient", return_value=fake_client) as client_cls, patch.object(
        relay.canvas,
        "load_canvas_server_state",
        return_value=state,
    ), patch.object(
        relay.canvas,
        "upstream_canvas_url",
        return_value="http://127.0.0.1:9/canvas/aaaaaaaaaaaa/?token=secret",
    ):
        status, _headers, body = await relay.proxy_canvas_request("canvas/aaaaaaaaaaaa/")
    assert status == 200
    assert body == b"ok"
    kwargs = client_cls.call_args.kwargs
    assert kwargs.get("follow_redirects") is False


def test_cursor_write_scope_is_allowed_and_implies_read():
    assert "cursor:read" in ALLOWED_SCOPES
    assert "cursor:write" in ALLOWED_SCOPES
    assert _normalize_scopes("cursor:write") == ["cursor:read", "cursor:write"]


def test_chat_scope_token_cannot_read_cursor_agents(monkeypatch):
    from routes.cursor_bridge_routes import _require_cursor_scope

    monkeypatch.setenv("AUTH_ENABLED", "true")
    req = _api_token_request(scopes=["chat"])
    with pytest.raises(HTTPException) as exc:
        _require_cursor_scope(req, {"cursor:read", "cursor:write"})
    assert exc.value.status_code == 403


def test_cursor_write_token_can_read_cursor_agents(monkeypatch):
    from routes.cursor_bridge_routes import _require_cursor_scope

    monkeypatch.setenv("AUTH_ENABLED", "true")
    req = _api_token_request(scopes=["cursor:write", "cursor:read"])
    owner = _require_cursor_scope(req, {"cursor:read", "cursor:write"})
    assert owner == "alice"


def test_chat_scope_token_cannot_write_cursor_agents(monkeypatch):
    from routes.cursor_bridge_routes import _require_cursor_scope

    monkeypatch.setenv("AUTH_ENABLED", "true")
    req = _api_token_request(scopes=["chat"])
    with pytest.raises(HTTPException) as exc:
        _require_cursor_scope(req, {"cursor:write"}, admin_for_session=True)
    assert exc.value.status_code == 403


def test_cursor_write_token_can_write_cursor_agents(monkeypatch):
    from routes.cursor_bridge_routes import _require_cursor_scope

    monkeypatch.setenv("AUTH_ENABLED", "true")
    req = _api_token_request(scopes=["cursor:write", "cursor:read"])
    owner = _require_cursor_scope(req, {"cursor:write"}, admin_for_session=True)
    assert owner == "alice"


def test_non_admin_session_cannot_write_cursor_agents(monkeypatch):
    from routes.cursor_bridge_routes import _require_cursor_scope

    monkeypatch.setenv("AUTH_ENABLED", "true")
    req = _cookie_request(is_admin=False)
    with pytest.raises(HTTPException) as exc:
        _require_cursor_scope(req, {"cursor:write"}, admin_for_session=True)
    assert exc.value.status_code == 403


def test_admin_session_can_write_cursor_agents(monkeypatch):
    from routes.cursor_bridge_routes import _require_cursor_scope

    monkeypatch.setenv("AUTH_ENABLED", "true")
    req = _cookie_request(is_admin=True)
    owner = _require_cursor_scope(req, {"cursor:write"}, admin_for_session=True)
    assert owner == "bob"


def test_create_agent_route_rejects_unprivileged_caller(monkeypatch):
    monkeypatch.setenv("AUTH_ENABLED", "true")
    app = FastAPI()
    app.include_router(setup_cursor_bridge_routes())
    client = TestClient(app)
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.headers = {"content-type": "application/json"}
    mock_response.json = lambda: {"agent_id": "a1"}
    with patch("routes.cursor_bridge_routes.is_configured", return_value=True), patch(
        "routes.cursor_bridge_routes.ensure_bridge_online",
        new=AsyncMock(return_value={"ok": True}),
    ), patch("routes.cursor_bridge_routes.bridge_request", new=AsyncMock(return_value=mock_response)):
        response = client.post("/api/cursor/agents", json={"prompt": "hi"})
    assert response.status_code in {401, 403}
