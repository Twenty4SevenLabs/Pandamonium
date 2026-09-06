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
sdk_message_to_stream_event = stream_events.sdk_message_to_stream_event


class _FakeBlock:
    def __init__(self, block_type: str, **kwargs):
        self.type = block_type
        for key, value in kwargs.items():
            setattr(self, key, value)


class _FakeAssistantEnvelope:
    def __init__(self, content):
        self.content = content


class _FakeAssistantMessage:
    type = "assistant"

    def __init__(self, text: str):
        self.message = _FakeAssistantEnvelope([_FakeBlock("text", text=text)])


class _FakeThinkingMessage:
    type = "thinking"

    def __init__(self, text: str):
        self.text = text


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


def test_normalize_rejects_sdk_repr_strings():
    block = normalize_stream_event(
        {"type": "assistant", "message": "SDKAssistantMessage(type='assistant', text='hi')"}
    )
    assert block is None


def test_sdk_message_to_stream_event_assistant():
    event = sdk_message_to_stream_event(_FakeAssistantMessage("Hello"))
    assert event == {
        "type": "message",
        "message": {"role": "assistant", "content": [{"type": "text", "text": "Hello"}]},
    }


def test_sdk_message_to_stream_event_thinking():
    event = sdk_message_to_stream_event(_FakeThinkingMessage("planning"))
    assert event == {"type": "update", "update": {"type": "thinking_delta", "delta": "planning"}}
