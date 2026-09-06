"""Cursor Canvas helpers for Panda bridge agents."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import quote

CANVAS_SUFFIX = ".canvas.tsx"
PROJECTS_ROOT = Path(
    os.getenv(
        "PANDAMONIUM_CURSOR_PROJECTS_ROOT",
        str(Path(os.getenv("PANDAMONIUM_CURSOR_BRIDGE_HOME", Path.home())) / ".cursor" / "projects"),
    )
).expanduser()
SYNC_SCRIPT = Path("/home/labsadmin/.cursor/scripts/sync-canvas-ssh-paths.py")
CANVAS_SERVER_URL = os.getenv("PANDAMONIUM_CURSOR_CANVAS_SERVER_URL", "").strip().rstrip("/")
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
    }
    if CANVAS_SERVER_URL:
        payload["embed_url"] = f"{CANVAS_SERVER_URL}/?path={quote(str(path))}"
    return payload
