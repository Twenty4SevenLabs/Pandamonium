from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "services" / "cursor-bridge" / "canvas_bridge.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("cursor_bridge_canvas", MODULE_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_resolve_canvas_path_under_projects(tmp_path: Path, monkeypatch):
    mod = _load_module()
    projects = tmp_path / "projects"
    canvas = projects / "mnt-dev-env-projects-pandamonium" / "canvases" / "demo.canvas.tsx"
    canvas.parent.mkdir(parents=True)
    canvas.write_text("export default function Demo() { return null; }\n", encoding="utf-8")
    monkeypatch.setattr(mod, "PROJECTS_ROOT", projects)
    resolved = mod.resolve_canvas_path(str(canvas), cwd="/mnt/dev-env/projects/pandamonium")
    assert resolved == canvas.resolve()


def test_detect_canvas_path_from_tool_write(tmp_path: Path, monkeypatch):
    mod = _load_module()
    projects = tmp_path / "projects"
    canvas = projects / "mnt-dev-env-projects-pandamonium" / "canvases" / "metrics.canvas.tsx"
    canvas.parent.mkdir(parents=True)
    canvas.write_text("export default function Metrics() { return null; }\n", encoding="utf-8")
    monkeypatch.setattr(mod, "PROJECTS_ROOT", projects)
    event = {
        "type": "update",
        "update": {
            "type": "tool_call_completed",
            "name": "Write",
            "input": {"path": str(canvas)},
        },
    }
    detected = mod.detect_canvas_path_from_event(event, cwd="/mnt/dev-env/projects/pandamonium")
    assert detected == canvas.resolve()


def test_build_canvas_open_payload(tmp_path: Path, monkeypatch):
    mod = _load_module()
    canvas = tmp_path / "demo.canvas.tsx"
    canvas.write_text("export default function Demo() { return null; }\n", encoding="utf-8")
    monkeypatch.setattr(mod, "SYNC_SCRIPT", tmp_path / "missing-sync.py")
    monkeypatch.setattr(mod, "PROJECTS_ROOT", tmp_path)
    (tmp_path / "canvases").mkdir()
    allowed = tmp_path / "canvases" / "demo.canvas.tsx"
    allowed.write_text(canvas.read_text(encoding="utf-8"), encoding="utf-8")
    payload = mod.build_canvas_open_payload(allowed, app_public_url="https://panda.example")
    assert payload["type"] == "canvas_open"
    assert payload["path"] == str(allowed)
    assert payload["popup_url"].startswith("https://panda.example/static/cursor-canvas-popup.html")
