"""Execution-node registry and sidecar URL routing for Cursor bridge."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

PROJECTS_ROOT = Path("/mnt/dev-env/projects")
_WORKSPACE_SEGMENT = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
_SLUG_PREFIX = "mnt-dev-env-projects-"

NODE_HOSTS = {"m3": "pve-prod", "m1": "pve-heavy", "m2": "pve-agents"}
NODE_ORDER = ("m3", "m1", "m2")
DEFAULT_SIDECAR_URLS = {
    "m3": "http://127.0.0.1:8050",
    "m1": "http://192.168.1.2:8050",
    "m2": "http://192.168.1.90:8050",
}


def _bridge_urls_raw() -> str:
    return (
        os.getenv("PANDAMONIUM_CURSOR_BRIDGE_URLS")
        or os.getenv("ODYSSEUS_CURSOR_BRIDGE_URLS")
        or ""
    )


def _bridge_url_m3() -> str:
    return (
        os.getenv("PANDAMONIUM_CURSOR_BRIDGE_URL")
        or os.getenv("ODYSSEUS_CURSOR_BRIDGE_URL")
        or DEFAULT_SIDECAR_URLS["m3"]
    ).rstrip("/")


def sidecar_urls() -> dict[str, str]:
    """Return sidecar base URLs keyed by node id (m3, m1, m2)."""
    urls_list: list[str] = []
    raw = _bridge_urls_raw().strip()
    if raw:
        for part in raw.split(","):
            url = part.strip().rstrip("/")
            if url:
                urls_list.append(url)

    m3_default = _bridge_url_m3()
    result: dict[str, str] = {}
    for index, node in enumerate(NODE_ORDER):
        if index < len(urls_list):
            result[node] = urls_list[index]
        elif node == "m3":
            result[node] = m3_default
        else:
            result[node] = DEFAULT_SIDECAR_URLS[node]
    return result


def sidecar_url_for_node(node: str) -> str:
    node_key = str(node or "m3").lower()
    urls = sidecar_urls()
    return urls.get(node_key, urls.get("m3", _bridge_url_m3()))


def execution_host_for_node(node: str) -> str:
    node_key = str(node or "m3").lower()
    return NODE_HOSTS.get(node_key, NODE_HOSTS["m3"])


def resolve_execution_node(agent: dict[str, Any]) -> str:
    if str(agent.get("source") or "").lower() == "bridge":
        return "m3"
    url = str(agent.get("mirror_url") or "")
    if "192.168.1.2" in url:
        return "m1"
    if "192.168.1.90" in url:
        return "m2"
    return "m3"


def _workspaces_json() -> dict[str, str]:
    raw = (
        os.getenv("PANDAMONIUM_CURSOR_WORKSPACES_JSON")
        or os.getenv("ODYSSEUS_CURSOR_WORKSPACES_JSON")
        or "{}"
    )
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    if not isinstance(payload, dict):
        return {}
    return {str(key): str(value) for key, value in payload.items()}


def is_safe_workspace_key(slug: str) -> bool:
    key = str(slug or "").strip()
    if not key or ".." in key or "/" in key or "\\" in key:
        return False
    if _WORKSPACE_SEGMENT.fullmatch(key):
        return True
    if key.startswith(_SLUG_PREFIX):
        return bool(_WORKSPACE_SEGMENT.fullmatch(key.removeprefix(_SLUG_PREFIX)))
    return False


def _is_safe_workspace_key(slug: str) -> bool:
    return is_safe_workspace_key(slug)


def _path_is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def _allowed_cwd_roots(workspaces: dict[str, str] | None = None) -> list[Path]:
    roots = [PROJECTS_ROOT.resolve()]
    mapping = workspaces if workspaces is not None else _workspaces_json()
    for key, value in mapping.items():
        if not _is_safe_workspace_key(str(key)):
            continue
        try:
            resolved = Path(str(value)).expanduser().resolve()
        except OSError:
            continue
        roots.append(resolved)
    return roots


def _within_allowed(path: Path, workspaces: dict[str, str] | None = None) -> bool:
    try:
        resolved = path.resolve()
    except OSError:
        return False
    return any(_path_is_within(resolved, root) for root in _allowed_cwd_roots(workspaces))


def is_allowed_agent_cwd(path: str | Path, workspaces: dict[str, str] | None = None) -> bool:
    return _within_allowed(Path(path).expanduser(), workspaces)


def workspace_cwd_from_slug(slug: str, workspaces: dict[str, str] | None = None) -> str | None:
    slug_key = str(slug or "").strip()
    if not _is_safe_workspace_key(slug_key):
        return None
    mapping = workspaces if workspaces is not None else _workspaces_json()
    if slug_key in mapping:
        mapped = Path(str(mapping[slug_key])).expanduser()
        if not mapped.is_absolute():
            return None
        return str(mapped.resolve())
    if slug_key.startswith(_SLUG_PREFIX):
        project = slug_key.removeprefix(_SLUG_PREFIX)
        mapped = PROJECTS_ROOT / project
        resolved = mapped.resolve()
        if not _path_is_within(resolved, PROJECTS_ROOT):
            return None
        return str(resolved)
    fallback_root = os.getenv("PANDAMONIUM_CURSOR_WORKSPACE_FALLBACK_ROOT", "").strip()
    if fallback_root:
        mapped = Path(fallback_root).expanduser().resolve() / slug_key
        if not _path_is_within(mapped, PROJECTS_ROOT):
            return None
        return str(mapped.resolve())
    return None


def resolve_agent_cwd(
    workspace: str,
    explicit_cwd: str = "",
    workspaces: dict[str, str] | None = None,
) -> str:
    cwd = str(explicit_cwd or "").strip()
    if cwd:
        candidate = Path(cwd).expanduser()
        try:
            resolved = candidate.resolve()
        except OSError:
            return ""
        if candidate.is_dir() and _within_allowed(resolved, workspaces):
            return str(resolved)
        return ""
    mapped = workspace_cwd_from_slug(workspace, workspaces=workspaces)
    if not mapped:
        return ""
    try:
        resolved = Path(mapped).resolve()
    except OSError:
        return ""
    if not _within_allowed(resolved, workspaces):
        return ""
    return str(resolved)
