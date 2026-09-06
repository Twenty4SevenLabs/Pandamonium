"""Execution-node registry and sidecar URL routing for Cursor bridge."""

from __future__ import annotations

import json
import os
from typing import Any

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


def workspace_cwd_from_slug(slug: str) -> str | None:
    slug_key = str(slug or "").strip()
    if not slug_key:
        return None
    workspaces = _workspaces_json()
    if slug_key in workspaces:
        return workspaces[slug_key]
    prefix = "mnt-dev-env-projects-"
    if slug_key.startswith(prefix):
        project = slug_key.removeprefix(prefix)
        if project:
            return f"/mnt/dev-env/projects/{project}"
    fallback_root = os.getenv("PANDAMONIUM_CURSOR_WORKSPACE_FALLBACK_ROOT", "").strip()
    if fallback_root:
        return f"{fallback_root.rstrip('/')}/{slug_key}"
    return None
