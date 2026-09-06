from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRANSCRIPT_PATH = ROOT / "services" / "pc-cursor-bridge" / "transcript_io.py"
ROUTES_PATH = ROOT / "routes" / "cursor_bridge_routes.py"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


transcript_io = _load_module(TRANSCRIPT_PATH, "transcript_io")
routes = _load_module(ROUTES_PATH, "cursor_bridge_routes")


def test_clean_user_text_extracts_user_query():
    raw = (
        "<timestamp>Sunday</timestamp>\n"
        "<user_query>\nAnalyze the bridge app overlay.\n</user_query>"
    )
    assert transcript_io._clean_user_text(raw) == "Analyze the bridge app overlay."


def test_clean_user_text_strips_image_context_without_query():
    raw = "[Image]\n<image_files>saved paths here</image_files>"
    assert transcript_io._clean_user_text(raw) == ""


def test_merge_session_messages_prefers_sidecar_when_forked():
    ide = [{"id": "1", "role": "user", "blocks": [{"type": "text", "text": "hi"}]}]
    side = ide + [{"id": "2", "role": "assistant", "blocks": [{"type": "text", "text": "hello"}]}]
    merged = routes._merge_session_messages(ide, side, forked=True, status="idle")
    assert merged == side


def test_merge_session_messages_prefers_longer_sidecar():
    ide = [{"id": "1", "role": "user", "blocks": [{"type": "text", "text": "hi"}]}]
    side = ide + [{"id": "2", "role": "assistant", "blocks": [{"type": "text", "text": "reply"}]}]
    merged = routes._merge_session_messages(ide, side, forked=False, status="idle")
    assert merged == side
