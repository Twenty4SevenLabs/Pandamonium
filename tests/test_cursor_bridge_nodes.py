from __future__ import annotations

from src.cursor_bridge_nodes import resolve_execution_node, sidecar_url_for_node, workspace_cwd_from_slug


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


def test_workspace_slug_maps_dev_env_project(monkeypatch):
    monkeypatch.delenv("PANDAMONIUM_CURSOR_WORKSPACES_JSON", raising=False)
    assert workspace_cwd_from_slug("mnt-dev-env-projects-pandamonium") == "/mnt/dev-env/projects/pandamonium"
