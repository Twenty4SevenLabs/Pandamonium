"""Cursor Canvas helpers for Panda bridge agents."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlencode

CANVAS_SUFFIX = ".canvas.tsx"
PROJECTS_ROOT = Path(
    os.getenv(
        "PANDAMONIUM_CURSOR_PROJECTS_ROOT",
        str(Path(os.getenv("PANDAMONIUM_CURSOR_BRIDGE_HOME", Path.home())) / ".cursor" / "projects"),
    )
).expanduser()
BRIDGE_HOME = Path(os.getenv("PANDAMONIUM_CURSOR_BRIDGE_HOME", str(Path.home()))).expanduser()
SYNC_SCRIPT = Path("/home/labsadmin/.cursor/scripts/sync-canvas-ssh-paths.py")
STATE_FILE = Path(
    os.getenv(
        "PANDAMONIUM_CURSOR_CANVAS_STATE_FILE",
        str(BRIDGE_HOME / ".cursor" / "canvas-server-state.json"),
    )
).expanduser()
CANVAS_SERVER_HOST = os.getenv("PANDAMONIUM_CURSOR_CANVAS_SERVER_HOST", "host.docker.internal").strip()
CANVAS_SERVER_PORT = os.getenv("PANDAMONIUM_CURSOR_CANVAS_SERVER_PORT", "").strip()
CANVAS_SERVER_TOKEN = os.getenv("PANDAMONIUM_CURSOR_CANVAS_SERVER_TOKEN", "").strip()
CANVAS_LOG_ROOT = BRIDGE_HOME / ".cursor-server" / "data" / "logs"
RELAY_PREFIX = "/api/cursor/canvas/relay/"
_TOOL_PATH_KEYS = ("path", "file_path", "filePath", "target", "target_file", "targetFile")


def _slug_from_cwd(cwd: str) -> str | None:
    root = Path(str(cwd or "")).expanduser().resolve()
    dev_env_projects = Path("/mnt/dev-env/projects")
    if root.is_relative_to(dev_env_projects):
        return f"mnt-dev-env-projects-{root.name}"
    if root == Path("/mnt/dev-env"):
        return "mnt-dev-env"
    return None


def canvas_dir_for_cwd(cwd: str) -> Path:
    slug = _slug_from_cwd(cwd)
    if slug:
        return PROJECTS_ROOT / slug / "canvases"
    return PROJECTS_ROOT / "canvases"


def is_canvas_path(path: str) -> bool:
    return str(path or "").strip().endswith(CANVAS_SUFFIX)


def canvas_title(path: Path) -> str:
    stem = path.name.removesuffix(CANVAS_SUFFIX)
    return re.sub(r"[-_]+", " ", stem).strip().title() or "Canvas"


def canvas_id_for_path(path: Path | str) -> str:
    return hashlib.sha256(f"canvas:{path}".encode()).hexdigest()[:12]


def resolve_canvas_path(raw_path: str, *, cwd: str = "") -> Path | None:
    candidate = str(raw_path or "").strip()
    if not candidate or not is_canvas_path(candidate):
        return None
    path = Path(candidate)
    if not path.is_absolute() and cwd:
        path = Path(cwd).expanduser().resolve() / path
    path = path.expanduser().resolve()
    if not path.is_file():
        return None
    try:
        path.relative_to(PROJECTS_ROOT.resolve())
    except ValueError:
        return None
    parts = path.parts
    if "canvases" not in parts:
        return None
    return path


def sync_canvas_paths(*, verbose: bool = False) -> None:
    if not SYNC_SCRIPT.is_file():
        return
    cmd = ["/usr/bin/python3", str(SYNC_SCRIPT)]
    if verbose:
        cmd.append("-v")
    subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _extract_path_from_mapping(payload: dict[str, Any]) -> str:
    for key in _TOOL_PATH_KEYS:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _paths_from_text(text: str) -> list[str]:
    if not text:
        return []
    return re.findall(r"(?:~/[^\s\"']+|/[^\s\"']+|[^\s\"']+/[^\s\"']+)\.canvas\.tsx", str(text))


def detect_canvas_path_from_event(event: dict[str, Any], *, cwd: str = "") -> Path | None:
    if not isinstance(event, dict):
        return None
    candidates: list[str] = []

    if event.get("type") == "artifact":
        url = str(event.get("url") or event.get("path") or "")
        if url:
            candidates.append(url)

    update = event.get("update")
    if isinstance(update, dict):
        kind = str(update.get("type") or update.get("updateType") or "").lower()
        name = str(update.get("name") or update.get("toolName") or "").lower()
        is_completed = "completed" in kind or kind.endswith("completed")
        is_write_like = any(token in name for token in ("write", "edit", "replace", "apply", "notebook"))
        if is_completed and is_write_like:
            for key in ("input", "args", "result"):
                nested = update.get(key)
                if isinstance(nested, dict):
                    path = _extract_path_from_mapping(nested)
                    if path:
                        candidates.append(path)
            path = _extract_path_from_mapping(update)
            if path:
                candidates.append(path)
            output = update.get("output")
            if isinstance(output, str):
                candidates.extend(_paths_from_text(output))

    if event.get("type") == "tool":
        tool_name = str(event.get("name") or event.get("toolName") or "").lower()
        if any(token in tool_name for token in ("write", "edit", "replace", "apply", "notebook")):
            tool_input = event.get("input")
            if isinstance(tool_input, dict):
                path = _extract_path_from_mapping(tool_input)
                if path:
                    candidates.append(path)

    for raw in candidates:
        resolved = resolve_canvas_path(raw, cwd=cwd)
        if resolved:
            return resolved
    return None


def collect_canvas_paths_from_blocks(blocks: list[Any], *, cwd: str = "") -> list[str]:
    found: set[str] = set()
    for block in blocks:
        if not isinstance(block, dict):
            continue
        block_type = str(block.get("type") or "")
        if block_type == "text":
            for raw in _paths_from_text(str(block.get("text") or "")):
                resolved = resolve_canvas_path(raw, cwd=cwd)
                if resolved:
                    found.add(str(resolved))
        for key in ("url", "path"):
            raw = str(block.get(key) or "")
            resolved = resolve_canvas_path(raw, cwd=cwd)
            if resolved:
                found.add(str(resolved))
        if block_type == "tool":
            tool_input = block.get("input") if isinstance(block.get("input"), dict) else {}
            raw = _extract_path_from_mapping(tool_input)
            resolved = resolve_canvas_path(raw, cwd=cwd)
            if resolved:
                found.add(str(resolved))
    return sorted(found)


def discover_canvas_port_from_logs(max_age_seconds: int = 7200) -> int | None:
    if not CANVAS_LOG_ROOT.is_dir():
        return None
    cutoff = time.time() - max_age_seconds
    best_port: int | None = None
    best_mtime = 0.0
    for log_path in CANVAS_LOG_ROOT.glob("**/anysphere.cursor-agent-exec/*.log"):
        try:
            mtime = log_path.stat().st_mtime
        except OSError:
            continue
        if mtime < cutoff:
            continue
        try:
            lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()[-400:]
        except OSError:
            continue
        for line in reversed(lines):
            match = re.search(r'Canvas server started \{"port":(\d+)', line)
            if not match:
                continue
            port = int(match.group(1))
            if mtime >= best_mtime:
                best_mtime = mtime
                best_port = port
            break
    return best_port


def load_canvas_server_state() -> dict[str, Any] | None:
    payload: dict[str, Any] = {}
    if STATE_FILE.is_file():
        try:
            raw = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                payload.update(raw)
        except (OSError, json.JSONDecodeError):
            pass
    port = CANVAS_SERVER_PORT or payload.get("port")
    if not port:
        discovered = discover_canvas_port_from_logs()
        if discovered:
            port = discovered
    token = CANVAS_SERVER_TOKEN or payload.get("sessionToken") or payload.get("token")
    host = CANVAS_SERVER_HOST or "127.0.0.1"
    try:
        port_int = int(port) if port else 0
    except (TypeError, ValueError):
        port_int = 0
    if port_int > 0 and not token:
        token = _fetch_canvas_server_token(host, port_int)
    if not port_int or not token:
        return None
    return {
        "host": host,
        "port": port_int,
        "sessionToken": str(token),
        "updatedAt": payload.get("updatedAt"),
    }


def public_canvas_server_state(state: dict[str, Any] | None = None) -> dict[str, Any] | None:
    row = state if state is not None else load_canvas_server_state()
    if not row:
        return None
    hidden = {"sessiontoken", "token"}
    return {key: value for key, value in row.items() if str(key).lower() not in hidden}


def _fetch_canvas_server_token(host: str, port: int) -> str:
    import urllib.error
    import urllib.request

    url = f"http://{host}:{port}/canvas-admin/state"
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=2) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except (OSError, json.JSONDecodeError, urllib.error.URLError, ValueError):
        return ""
    if isinstance(raw, dict):
        return str(raw.get("sessionToken") or raw.get("token") or "")
    return ""


def canvas_server_base_url(state: dict[str, Any] | None = None) -> str | None:
    row = state or load_canvas_server_state()
    if not row:
        return None
    host = str(row.get("host") or "127.0.0.1")
    port = int(row.get("port") or 0)
    if port <= 0:
        return None
    return f"http://{host}:{port}"


def upstream_canvas_url(path: str, *, state: dict[str, Any] | None = None) -> str | None:
    base = canvas_server_base_url(state)
    row = state or load_canvas_server_state()
    if not base or not row:
        return None
    token = str(row.get("sessionToken") or "")
    clean = str(path or "").lstrip("/")
    query = urlencode({"token": token})
    return f"{base}/{clean}?{query}" if clean else f"{base}/?{query}"


def rewrite_relay_content(content: str) -> str:
    if not content:
        return content
    rewritten = content
    rewritten = re.sub(r"\?token=[^\"'\\s<>]+", "", rewritten)
    rewritten = re.sub(r"&token=[^\"'\\s<>]+", "", rewritten)
    rewritten = rewritten.replace('"/canvas/', f'"{RELAY_PREFIX}canvas/')
    rewritten = rewritten.replace("'/canvas/", f"'{RELAY_PREFIX}canvas/")
    rewritten = rewritten.replace("`/canvas/", f"`{RELAY_PREFIX}canvas/")
    rewritten = rewritten.replace('"/runtime/', f'"{RELAY_PREFIX}runtime/')
    rewritten = rewritten.replace("'/runtime/", f"'{RELAY_PREFIX}runtime/")
    rewritten = rewritten.replace("`/runtime/", f"`{RELAY_PREFIX}runtime/")
    rewritten = re.sub(
        r"ws://(?:127\.0\.0\.1|localhost):\d+/canvas/",
        "/api/cursor/canvas/relay/canvas/",
        rewritten,
    )
    return rewritten


def build_embed_url(path: Path) -> str:
    canvas_id = canvas_id_for_path(path)
    return f"/api/cursor/canvas/embed/{quote(canvas_id, safe='')}"


def build_canvas_open_payload(path: Path, *, app_public_url: str = "") -> dict[str, Any]:
    sync_canvas_paths()
    title = canvas_title(path)
    file_uri = path.as_uri()
    popup_path = f"/static/cursor-canvas-popup.html?path={quote(str(path))}"
    popup_url = f"{app_public_url.rstrip('/')}{popup_path}" if app_public_url else popup_path
    payload: dict[str, Any] = {
        "type": "canvas_open",
        "path": str(path),
        "title": title,
        "file_uri": file_uri,
        "popup_url": popup_url,
        "embed_url": "",
        "canvas_id": canvas_id_for_path(path),
        "canvas_server": public_canvas_server_state(),
    }
    if payload["canvas_server"]:
        payload["embed_url"] = build_embed_url(path)
    return payload
