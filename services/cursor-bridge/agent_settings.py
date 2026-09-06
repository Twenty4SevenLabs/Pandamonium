"""Cursor bridge agent settings: skills via setting_sources and MCP servers."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

DEFAULT_SETTING_SOURCES: tuple[str, ...] = ("project", "user", "plugins")
SKILL_MARKERS = ("SKILL.md", "skill.md")


def bridge_home() -> Path:
    """Directory whose ``.cursor/`` tree the SDK should read for user settings."""
    override = os.getenv("PANDAMONIUM_CURSOR_BRIDGE_HOME", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    candidate = Path("/home/labsadmin")
    if (candidate / ".cursor").is_dir():
        return candidate
    return Path.home()


def cursor_config_dir() -> Path:
    override = os.getenv("PANDAMONIUM_CURSOR_CONFIG_DIR", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return bridge_home() / ".cursor"


def mcp_config_path() -> Path:
    override = os.getenv("PANDAMONIUM_CURSOR_MCP_CONFIG", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return cursor_config_dir() / "mcp.json"


def parse_setting_sources(raw: str | None = None) -> list[str]:
    value = (raw if raw is not None else os.getenv("PANDAMONIUM_CURSOR_SETTING_SOURCES", "")).strip()
    if not value or value.lower() in {"none", "off", "false", "[]"}:
        return []
    if value.lower() in {"all", "*"}:
        return ["all"]
    sources = [part.strip() for part in value.split(",") if part.strip()]
    return sources or list(DEFAULT_SETTING_SOURCES)


def _load_env_file(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            result[key] = value
    return result


def _merge_env(
    base: dict[str, Any] | None,
    env_file: str | None,
) -> dict[str, str]:
    merged: dict[str, str] = {}
    if isinstance(base, dict):
        for key, value in base.items():
            if isinstance(key, str) and value is not None:
                merged[key] = str(value)
    if env_file:
        merged.update(_load_env_file(Path(str(env_file)).expanduser()))
    return merged


def cursor_mcp_entry_to_sdk(name: str, entry: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(entry, dict):
        return None
    url = str(entry.get("url") or "").strip()
    if url:
        transport = str(entry.get("type") or "http").strip().lower()
        payload: dict[str, Any] = {"url": url, "type": transport if transport in {"http", "sse"} else "http"}
        headers = entry.get("headers")
        if isinstance(headers, dict):
            payload["headers"] = {str(k): str(v) for k, v in headers.items() if v is not None}
        auth = entry.get("auth")
        if isinstance(auth, dict) and auth:
            payload["auth"] = auth
        return payload
    command = str(entry.get("command") or "").strip()
    if not command:
        return None
    args_raw = entry.get("args") or []
    args = [str(item) for item in args_raw] if isinstance(args_raw, list) else []
    env = _merge_env(entry.get("env"), entry.get("envFile"))
    payload = {"command": command, "args": args}
    if env:
        payload["env"] = env
    cwd = str(entry.get("cwd") or "").strip()
    if cwd:
        payload["cwd"] = cwd
    return payload


def load_cursor_mcp_servers(config_path: Path | None = None) -> dict[str, dict[str, Any]]:
    path = config_path or mcp_config_path()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(payload, dict):
        return {}
    raw_servers = payload.get("mcpServers") or payload.get("mcp_servers") or {}
    if not isinstance(raw_servers, dict):
        return {}
    servers: dict[str, dict[str, Any]] = {}
    for name, entry in raw_servers.items():
        key = str(name or "").strip()
        if not key or not isinstance(entry, dict):
            continue
        converted = cursor_mcp_entry_to_sdk(key, entry)
        if converted:
            servers[key] = converted
    return servers


def _count_skill_files(root: Path) -> int:
    if not root.is_dir():
        return 0
    count = 0
    for path in root.rglob("*"):
        if path.is_file() and path.name in SKILL_MARKERS:
            count += 1
    return count


def count_available_skills() -> int:
    home = bridge_home()
    total = _count_skill_files(cursor_config_dir() / "skills-cursor")
    agents_root = Path(os.getenv("PANDAMONIUM_CURSOR_AGENTS_SKILLS_DIR", str(home / ".agents" / "skills")))
    total += _count_skill_files(agents_root)
    return total


def capabilities_summary() -> dict[str, Any]:
    sources = effective_setting_sources()
    mcp_servers = load_cursor_mcp_servers()
    return {
        "bridge_home": str(bridge_home()),
        "cursor_config_dir": str(cursor_config_dir()),
        "setting_sources": sources,
        "skills_enabled": bool(sources),
        "skill_count": count_available_skills() if sources else 0,
        "mcp_enabled": bool(mcp_servers),
        "mcp_servers": sorted(mcp_servers.keys()),
        "mcp_config_path": str(mcp_config_path()),
        "mcp_config_present": mcp_config_path().is_file(),
    }


def effective_setting_sources() -> list[str]:
    configured = parse_setting_sources()
    if configured:
        return configured
    if cursor_config_dir().is_dir() or mcp_config_path().is_file():
        return list(DEFAULT_SETTING_SOURCES)
    return []


def build_local_options(cwd: str) -> dict[str, Any]:
    sources = effective_setting_sources()
    local: dict[str, Any] = {"cwd": cwd}
    if sources:
        local["setting_sources"] = sources
    else:
        local["setting_sources"] = []
    return local


def build_agent_options(*, api_key: str, cwd: str, model: str) -> dict[str, Any]:
    options: dict[str, Any] = {
        "api_key": api_key,
        "model": model,
        "local": build_local_options(cwd),
    }
    mcp_servers = load_cursor_mcp_servers()
    if mcp_servers:
        options["mcp_servers"] = mcp_servers
    return options


def build_send_options() -> dict[str, Any]:
    mcp_servers = load_cursor_mcp_servers()
    if not mcp_servers:
        return {}
    return {"mcp_servers": mcp_servers}
