from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIDGE_PATH = ROOT / "services" / "pc-cursor-bridge" / "pc_cursor_bridge.py"
SPEC = importlib.util.spec_from_file_location("pc_cursor_bridge", BRIDGE_PATH)
bridge = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(bridge)


def test_scan_ide_agents_reads_transcripts(tmp_path, monkeypatch):
    projects_root = tmp_path / "projects"
    transcript_dir = projects_root / "demo-project" / "agent-transcripts"
    transcript_dir.mkdir(parents=True)
    transcript = transcript_dir / "agent-123.jsonl"
    transcript.write_text('{"title":"Plan Cursor bridge"}\n', encoding="utf-8")
    monkeypatch.setattr(bridge, "PROJECTS_ROOT", projects_root)
    items = bridge._scan_ide_agents(limit=10)
    assert len(items) == 1
    assert items[0]["agent_id"] == "agent-123"
    assert items[0]["source"] == "ide"
    assert items[0]["title"] == "Plan Cursor bridge"


def test_authorized_requires_matching_token(tmp_path, monkeypatch):
    token_file = tmp_path / "token"
    token_file.write_text("secret-token", encoding="utf-8")
    monkeypatch.setattr(bridge, "TOKEN_FILE", token_file)
    assert bridge._authorized("Bearer secret-token") is True
    assert bridge._authorized("Bearer wrong") is False
