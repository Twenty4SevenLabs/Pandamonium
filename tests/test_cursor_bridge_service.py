from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from tests.test_cursor_bridge_canvas import _load_module as _load_canvas_module


@pytest.mark.asyncio
async def test_list_agents_returns_registry_when_client_not_ready(tmp_path: Path, monkeypatch):
    mod = _load_canvas_module()
    # Reuse canvas loader pattern against service module
    import importlib.util

    service_path = Path(__file__).resolve().parents[1] / "services" / "cursor-bridge" / "cursor_bridge_service.py"
    spec = importlib.util.spec_from_file_location("cursor_bridge_service_list_test", service_path)
    assert spec and spec.loader
    service = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[spec.name] = service
    spec.loader.exec_module(service)

    registry = {
        "agent-a": {
            "agent_id": "agent-a",
            "title": "Saved agent",
            "workspace": "pandamonium",
            "status": "idle",
            "source": "bridge",
            "updated_at": 123,
        }
    }
    state_dir = tmp_path / "cursor-bridge"
    state_dir.mkdir()
    (state_dir / "agents.json").write_text(json.dumps(registry), encoding="utf-8")
    monkeypatch.setattr(service, "STATE_DIR", state_dir)
    monkeypatch.setattr(service, "REGISTRY_FILE", state_dir / "agents.json")
    monkeypatch.setattr(service, "SETTINGS_FILE", state_dir / "settings.json")
    monkeypatch.setattr(service, "WORKSPACES", {"pandamonium": str(tmp_path)})
    monkeypatch.setattr(service, "DEFAULT_WORKSPACE", "pandamonium")
    service.STATE.client = None
    service.STATE.guard_failed = None
    service.STATE.api_key = "cursor_test_key"

    with patch.object(service, "_require_auth", return_value=None), patch.object(
        service,
        "_maybe_launch_client",
        new=AsyncMock(return_value=None),
    ):
        payload = await service.list_agents(authorization="Bearer test")

    assert payload["connected"] is False
    assert [row["agent_id"] for row in payload["items"]] == ["agent-a"]
