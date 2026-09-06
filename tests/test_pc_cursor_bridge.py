from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BRIDGE_PATH = ROOT / "services" / "pc-cursor-bridge" / "pc_cursor_bridge.py"
TRANSCRIPT_PATH = ROOT / "services" / "pc-cursor-bridge" / "transcript_io.py"
SPEC = importlib.util.spec_from_file_location("pc_cursor_bridge", BRIDGE_PATH)
bridge = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(bridge)

TIO_SPEC = importlib.util.spec_from_file_location("transcript_io", TRANSCRIPT_PATH)
tio = importlib.util.module_from_spec(TIO_SPEC)
assert TIO_SPEC.loader is not None
TIO_SPEC.loader.exec_module(tio)


def test_scan_ide_agents_reads_nested_transcripts(tmp_path, monkeypatch):
    projects_root = tmp_path / "projects"
    transcript_dir = projects_root / "demo-project" / "agent-transcripts" / "agent-123"
    transcript_dir.mkdir(parents=True)
    transcript = transcript_dir / "agent-123.jsonl"
    transcript.write_text(
        '{"role":"user","message":{"content":[{"type":"text","text":"<user_query>Plan Cursor bridge</user_query>"}]}}\n'
        '{"role":"assistant","message":{"content":[{"type":"text","text":"On it."},{"type":"tool_use","name":"Read","input":{"path":"app.py"}}]}}\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(bridge, "PROJECTS_ROOT", projects_root)
    items = bridge._scan_ide_agents(limit=10)
    assert len(items) == 1
    assert items[0]["agent_id"] == "agent-123"
    assert items[0]["source"] == "ide"
    assert items[0]["title"] == "Plan Cursor bridge"


def test_transcript_session_parser(tmp_path):
    transcript = tmp_path / "agent-123.jsonl"
    transcript.write_text(
        '{"role":"user","message":{"content":[{"type":"text","text":"<user_query>Hello Panda</user_query>"}]}}\n'
        '{"role":"assistant","message":{"content":[{"type":"text","text":"Hi there"}]}}\n',
        encoding="utf-8",
    )
    session = tio.load_session(
        transcript,
        agent_id="agent-123",
        workspace="demo-project",
        updated_at=123,
        is_subagent=False,
    )
    assert session["message_count"] == 2
    assert session["messages"][0]["role"] == "user"
    assert session["messages"][0]["blocks"][0]["text"] == "Hello Panda"
    assert session["messages"][1]["blocks"][0]["text"] == "Hi there"


def test_authorized_requires_matching_token(tmp_path, monkeypatch):
    token_file = tmp_path / "token"
    token_file.write_text("secret-token", encoding="utf-8")
    monkeypatch.setattr(bridge, "TOKEN_FILE", token_file)
    assert bridge._authorized("Bearer secret-token") is True
    assert bridge._authorized("Bearer wrong") is False
