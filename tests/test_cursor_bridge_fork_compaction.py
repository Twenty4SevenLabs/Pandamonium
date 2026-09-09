from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FORK_PATH = ROOT / "services" / "cursor-bridge" / "fork_compaction.py"
GUARD_PATH = ROOT / "services" / "cursor-bridge" / "ide_agent_guard.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


fork = _load(FORK_PATH, "cursor_bridge_fork_compaction_test")
guard = _load(GUARD_PATH, "cursor_bridge_ide_agent_guard_test")


def _msg(role: str, text: str) -> dict:
    return {"role": role, "blocks": [{"type": "text", "text": text}]}


def test_tail_messages_keeps_last_fifteen():
    messages = [_msg("user", f"line-{index}") for index in range(20)]
    tail = fork.tail_messages(messages, limit=15)
    assert len(tail) == 15
    assert tail[0]["blocks"][0]["text"] == "line-5"
    assert tail[-1]["blocks"][0]["text"] == "line-19"


def test_parse_handoff_response_extracts_json():
    raw = 'Here you go:\n{"goal":"Ship fork compaction","files":["a.py"],"next_steps":["Add tests"],"summary":"Almost done"}'
    handoff = fork.parse_handoff_response(raw)
    assert handoff["goal"] == "Ship fork compaction"
    assert handoff["files"] == ["a.py"]
    assert handoff["next_steps"] == ["Add tests"]
    assert "Almost done" in handoff["summary"]


def test_build_fork_pending_context_includes_handoff_and_tail():
    transcript = [_msg("user", f"m-{index}") for index in range(18)]
    handoff = {
        "goal": "Continue work",
        "files": ["src/foo.py"],
        "next_steps": ["Wire tests"],
        "summary": "In progress",
    }
    pending = fork.build_fork_pending_context(handoff, transcript, tail_limit=15)
    assert pending[0]["role"] == "assistant"
    assert "PANDA FORK HANDOFF" in pending[0]["blocks"][0]["text"]
    assert "src/foo.py" in pending[0]["blocks"][0]["text"]
    assert len(pending) == 16
    assert pending[1]["blocks"][0]["text"] == "m-3"


def test_is_ide_transcript_agent_id_detects_projects_tree(tmp_path: Path, monkeypatch):
    ide_id = "6d91f84e-cf09-4c68-86a7-1f0e1ed631a5"
    transcript = tmp_path / "mnt-dev-env-projects-pandamonium" / "agent-transcripts" / ide_id / f"{ide_id}.jsonl"
    transcript.parent.mkdir(parents=True)
    transcript.write_text(json.dumps({"role": "user", "message": {"content": "hi"}}) + "\n", encoding="utf-8")
    monkeypatch.setenv("PANDAMONIUM_PC_CURSOR_PROJECTS_ROOT", str(tmp_path))
    assert guard.is_ide_transcript_agent_id(ide_id, tmp_path) is True
    assert guard.is_ide_transcript_agent_id("not-a-uuid", tmp_path) is False


def test_resolve_sdk_resume_id_forbids_bare_ide_id(tmp_path: Path, monkeypatch):
    ide_id = "6d91f84e-cf09-4c68-86a7-1f0e1ed631a5"
    transcript = tmp_path / "proj" / "agent-transcripts" / f"{ide_id}.jsonl"
    transcript.parent.mkdir(parents=True)
    transcript.write_text("{}", encoding="utf-8")
    monkeypatch.setenv("PANDAMONIUM_PC_CURSOR_PROJECTS_ROOT", str(tmp_path))
    with pytest.raises(guard.IdeAgentResumeForbidden):
        guard.resolve_sdk_resume_id(ide_id, None)
    assert guard.resolve_sdk_resume_id(ide_id, {"forked": True, "sdk_agent_id": "panda-sdk-1"}) == "panda-sdk-1"
