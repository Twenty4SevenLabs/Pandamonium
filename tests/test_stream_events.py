from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STREAM_PATH = ROOT / "services" / "cursor-bridge" / "stream_events.py"
SPEC = importlib.util.spec_from_file_location("stream_events", STREAM_PATH)
stream_events = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(stream_events)

normalize_stream_event = stream_events.normalize_stream_event
events_to_parity_blocks = stream_events.events_to_parity_blocks


def test_normalize_error_event():
    block = normalize_stream_event({"type": "error", "text": "boom"})
    assert block == {"type": "error", "text": "boom"}


def test_normalize_text_message():
    block = normalize_stream_event(
        {
            "type": "message",
            "message": {"role": "assistant", "content": [{"type": "text", "text": "Hello"}]},
        }
    )
    assert block == {"type": "text", "text": "Hello"}


def test_normalize_tool_started_update():
    block = normalize_stream_event(
        {
            "type": "update",
            "update": {"type": "tool_call_started", "name": "Read", "input": {"path": "/tmp/a"}},
        }
    )
    assert block["type"] == "tool"
    assert block["name"] == "Read"
    assert block["status"] == "running"


def test_normalize_thinking_delta():
    block = normalize_stream_event(
        {"type": "update", "update": {"type": "thinking_delta", "delta": "planning"}}
    )
    assert block == {"type": "thinking", "text": "planning", "collapsed": True}


def test_events_to_parity_blocks_merges_text():
    blocks = events_to_parity_blocks(
        [
            {"type": "update", "update": {"type": "text_delta", "delta": "Hel"}},
            {"type": "update", "update": {"type": "text_delta", "delta": "lo"}},
        ]
    )
    assert blocks == [{"type": "text", "text": "Hello"}]
