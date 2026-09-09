from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from routes.cursor_bridge_routes import setup_cursor_bridge_routes


@pytest.fixture()
def client():
    app = FastAPI()
    app.include_router(setup_cursor_bridge_routes())
    with patch("routes.cursor_bridge_routes._require_cursor_scope", return_value="tester"):
        yield TestClient(app)


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


def test_agent_session_prefers_ide_mirror(client):
    ide_session = {
        "agent_id": "ide-1",
        "title": "IDE chat",
        "source": "ide",
        "read_only": True,
        "messages": [{"role": "user", "blocks": [{"type": "text", "text": "Hello"}]}],
    }
    with patch("routes.cursor_bridge_routes.is_configured", return_value=True), patch(
        "routes.cursor_bridge_routes.fetch_ide_agent_session",
        new=AsyncMock(return_value=ide_session),
    ), patch(
        "routes.cursor_bridge_routes.ensure_bridge_online",
        new=AsyncMock(return_value={"ok": True}),
    ), patch(
        "routes.cursor_bridge_routes.bridge_request_for_agent",
        new=AsyncMock(return_value=SimpleNamespace(status_code=404, headers={}, json=lambda: {}, text="")),
    ):
        response = client.get("/api/cursor/agents/ide-1/session?source=ide")
    assert response.status_code == 200
    assert response.json()["title"] == "IDE chat"
    assert response.json()["messages"][0]["blocks"][0]["text"] == "Hello"


def test_send_ide_without_fork_returns_409(client):
    ide_id = "6d91f84e-cf09-4c68-86a7-1f0e1ed631a5"
    ide_session = {
        "agent_id": ide_id,
        "title": "IDE chat",
        "source": "ide",
        "workspace": "mnt-dev-env-projects-pandamonium",
        "messages": [{"role": "user", "blocks": [{"type": "text", "text": "Hello"}]}],
    }

    probe_response = AsyncMock()
    probe_response.status_code = 404
    probe_response.headers = {"content-type": "application/json"}
    probe_response.json = lambda: {"detail": "agent_not_found"}

    with patch("routes.cursor_bridge_routes.is_configured", return_value=True), patch(
        "routes.cursor_bridge_routes.ensure_bridge_online",
        new=AsyncMock(return_value={"ok": True}),
    ), patch(
        "routes.cursor_bridge_routes.fetch_ide_agent_session",
        new=AsyncMock(return_value=ide_session),
    ), patch(
        "routes.cursor_bridge_routes.is_ide_transcript_agent_id",
        return_value=True,
    ), patch(
        "routes.cursor_bridge_routes.bridge_request_for_agent",
        new=AsyncMock(return_value=probe_response),
    ):
        response = client.post(
            f"/api/cursor/agents/{ide_id}/send",
            json={"prompt": "Reply with exactly: Panda overlay test OK."},
        )

    assert response.status_code == 409
    assert response.json()["detail"] == "ide_fork_required"


def test_fork_then_send_succeeds(client):
    ide_id = "6d91f84e-cf09-4c68-86a7-1f0e1ed631a5"
    fork_response = AsyncMock()
    fork_response.status_code = 200
    fork_response.headers = {"content-type": "application/json"}
    fork_response.json = lambda: {
        "agent": {"agent_id": ide_id, "source": "ide", "forked": True, "sdk_agent_id": "panda-sdk-1"},
        "forked": True,
    }

    send_response = AsyncMock()
    send_response.status_code = 200
    send_response.json = lambda: {"run_id": "run-1", "agent": {"agent_id": ide_id, "source": "ide", "forked": True}}

    probe_forked = AsyncMock()
    probe_forked.status_code = 200
    probe_forked.headers = {"content-type": "application/json"}
    probe_forked.json = lambda: {
        "agent_id": ide_id,
        "source": "ide",
        "forked": True,
        "sdk_agent_id": "panda-sdk-1",
        "status": "idle",
    }

    ide_session = {
        "agent_id": ide_id,
        "title": "IDE chat",
        "source": "ide",
        "workspace": "mnt-dev-env-projects-pandamonium",
        "messages": [{"role": "user", "blocks": [{"type": "text", "text": "Hello"}]}],
    }

    calls: list[tuple[str, str]] = []

    async def fake_bridge_request_for_agent(method, path, agent_meta, **kwargs):
        calls.append((method, path))
        if method == "POST" and path.endswith("/fork"):
            return fork_response
        if method == "GET" and path.endswith("/session"):
            return probe_forked
        if method == "POST" and path.endswith("/send"):
            return send_response
        raise AssertionError(f"unexpected bridge request: {method} {path}")

    with patch("routes.cursor_bridge_routes.is_configured", return_value=True), patch(
        "routes.cursor_bridge_routes.ensure_bridge_online",
        new=AsyncMock(return_value={"ok": True}),
    ), patch(
        "routes.cursor_bridge_routes.fetch_ide_agent_session",
        new=AsyncMock(return_value=ide_session),
    ), patch(
        "routes.cursor_bridge_routes.is_ide_transcript_agent_id",
        return_value=True,
    ), patch(
        "routes.cursor_bridge_routes.bridge_request_for_agent",
        new=AsyncMock(side_effect=fake_bridge_request_for_agent),
    ):
        fork = client.post(f"/api/cursor/agents/{ide_id}/fork", json={})
        assert fork.status_code == 200
        response = client.post(
            f"/api/cursor/agents/{ide_id}/send",
            json={"prompt": "Reply with exactly: Panda overlay test OK."},
        )

    assert response.status_code == 200
    assert response.json()["run_id"] == "run-1"
    assert ("POST", f"/agents/{ide_id}/fork") in calls
    assert not any(path.endswith("/resume") for _, path in calls)
