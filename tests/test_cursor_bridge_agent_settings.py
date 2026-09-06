from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "services" / "cursor-bridge" / "agent_settings.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("cursor_bridge_agent_settings", MODULE_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_parse_setting_sources_defaults_to_project_user_plugins(monkeypatch):
    mod = _load_module()
    monkeypatch.delenv("PANDAMONIUM_CURSOR_SETTING_SOURCES", raising=False)
    monkeypatch.setattr(mod, "cursor_config_dir", lambda: Path("/missing"))
    monkeypatch.setattr(mod, "mcp_config_path", lambda: Path("/missing/mcp.json"))
    assert mod.parse_setting_sources("") == []
    assert mod.effective_setting_sources() == []


def test_load_cursor_mcp_servers_converts_http_and_stdio(tmp_path: Path):
    mod = _load_module()
    config = tmp_path / "mcp.json"
    config.write_text(
        json.dumps(
            {
                "mcpServers": {
                    "hypejet": {"url": "https://mcp.example/mcp"},
                    "gitlab": {
                        "command": "npx",
                        "args": ["-y", "@zereight/mcp-gitlab"],
                        "env": {"GITLAB_API_URL": "https://gitlab.example/api/v4"},
                        "envFile": str(tmp_path / "gitlab.env"),
                    },
                }
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "gitlab.env").write_text("GITLAB_TOKEN=secret\n", encoding="utf-8")
    servers = mod.load_cursor_mcp_servers(config)
    assert set(servers) == {"hypejet", "gitlab"}
    assert servers["hypejet"]["url"] == "https://mcp.example/mcp"
    assert servers["gitlab"]["command"] == "npx"
    assert servers["gitlab"]["env"]["GITLAB_TOKEN"] == "secret"


def test_build_agent_options_includes_setting_sources_and_mcp(tmp_path: Path, monkeypatch):
    mod = _load_module()
    config = tmp_path / "mcp.json"
    config.write_text(json.dumps({"mcpServers": {"lightpanda": {"url": "http://127.0.0.1:9223/mcp"}}}), encoding="utf-8")
    monkeypatch.setenv("PANDAMONIUM_CURSOR_SETTING_SOURCES", "project,user,plugins")
    monkeypatch.setenv("PANDAMONIUM_CURSOR_MCP_CONFIG", str(config))
    options = mod.build_agent_options(api_key="cursor_test", cwd="/tmp/work", model="composer-2.5")
    assert options["local"]["setting_sources"] == ["project", "user", "plugins"]
    assert "lightpanda" in options["mcp_servers"]
    send_opts = mod.build_send_options()
    assert "lightpanda" in send_opts["mcp_servers"]


def test_cursor_project_slug_for_dev_env_project(monkeypatch):
    mod = _load_module()
    monkeypatch.setattr(mod, "bridge_home", lambda: Path("/home/labsadmin"))
    assert mod.cursor_project_slug("/mnt/dev-env/projects/pandamonium") == "mnt-dev-env-projects-pandamonium"


def test_ensure_sdk_agent_store_creates_writable_dir(tmp_path: Path, monkeypatch):
    mod = _load_module()
    project = Path("/mnt/dev-env/projects/pandamonium")
    monkeypatch.setattr(mod, "bridge_home", lambda: tmp_path / "home")
    store = mod.ensure_sdk_agent_store(str(project))
    assert store.is_dir()
    assert store.name == "sdk-agent-store"
    assert store.parent.name == "mnt-dev-env-projects-pandamonium"

