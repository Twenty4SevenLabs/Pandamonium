from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from routes.cursor_bridge_routes import setup_cursor_bridge_routes


@pytest.fixture()
def client():
    app = FastAPI()
    app.include_router(setup_cursor_bridge_routes())
    return TestClient(app)


def test_status_unconfigured(client):
    with patch("routes.cursor_bridge_routes.bridge_status", new=AsyncMock(return_value={"configured": False, "connected": False, "status": "disconnected"})):
        response = client.get("/api/cursor/status")
    assert response.status_code == 200
    body = response.json()
    assert body["configured"] is False
    assert body["model_lock"] == "composer-2.5"


def test_connect_requires_admin(client):
    response = client.post("/api/cursor/connect", json={"api_key": "cursor_" + ("x" * 40)})
    assert response.status_code in {401, 403}


def test_list_agents_unconfigured(client):
    with patch("routes.cursor_bridge_routes.is_configured", return_value=False):
        response = client.get("/api/cursor/agents")
    assert response.status_code == 200
    assert response.json()["items"] == []


def test_list_agents_merges_ide_mirror(client):
    bridge_items = [{"agent_id": "a1", "title": "Bridge", "source": "bridge", "updated_at": 10}]
    ide_items = [{"agent_id": "b1", "title": "IDE", "source": "ide", "updated_at": 20}]
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.raise_for_status = lambda: None
    mock_response.json = lambda: {"items": bridge_items}
    with patch("routes.cursor_bridge_routes.is_configured", return_value=True), patch(
        "routes.cursor_bridge_routes.ensure_bridge_online",
        new=AsyncMock(return_value={"ok": True}),
    ), patch("routes.cursor_bridge_routes.bridge_request", new=AsyncMock(return_value=mock_response)), patch(
        "routes.cursor_bridge_routes.list_ide_mirror_agents",
        new=AsyncMock(return_value=ide_items),
    ), patch("routes.cursor_bridge_routes.dismissed_agent_ids", return_value=set()):
        response = client.get("/api/cursor/agents?source=all")
    assert response.status_code == 200
    ids = [row["agent_id"] for row in response.json()["items"]]
    assert ids == ["b1", "a1"]


def test_remove_agent_ide_dismisses(client):
    with patch("routes.cursor_bridge_routes.is_configured", return_value=True), patch(
        "routes.cursor_bridge_routes.ensure_bridge_online",
        new=AsyncMock(return_value={"ok": True}),
    ), patch("routes.cursor_bridge_routes.dismiss_agent") as dismiss:
        response = client.delete("/api/cursor/agents/ide-agent-1?source=ide")
    assert response.status_code == 200
    dismiss.assert_called_once_with("ide-agent-1")


def test_remove_agent_bridge_delegates(client):
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = lambda: {"removed": True, "agent_id": "a1"}
    with patch("routes.cursor_bridge_routes.is_configured", return_value=True), patch(
        "routes.cursor_bridge_routes.ensure_bridge_online",
        new=AsyncMock(return_value={"ok": True}),
    ), patch("routes.cursor_bridge_routes.bridge_request", new=AsyncMock(return_value=mock_response)), patch(
        "routes.cursor_bridge_routes.dismiss_agent",
    ) as dismiss:
        response = client.delete("/api/cursor/agents/a1")
    assert response.status_code == 200
    dismiss.assert_called_once_with("a1")
