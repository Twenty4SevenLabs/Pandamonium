"""Discover and parse Cursor IDE agent transcript JSONL files."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

USER_QUERY_PATTERN = re.compile(r"<user_query>\s*(.*?)\s*</user_query>", re.DOTALL | re.IGNORECASE)
TAG_BLOCK_PATTERN = re.compile(r"<(timestamp|image_files|open_and_recently_viewed_files|agent_transcripts)[^>]*>.*?</\1>", re.DOTALL | re.IGNORECASE)
GENERIC_TAG_PATTERN = re.compile(r"<([a-zA-Z0-9_-]+)(?:\s[^>]*)?>.*?</\1>", re.DOTALL)
SELF_CLOSING_TAG_PATTERN = re.compile(r"<([a-zA-Z0-9_-]+)(?:\s[^>]*)?/>")
TITLE_JSON_PATTERN = re.compile(r'"title"\s*:\s*"([^"]{1,200})"')


@dataclass(frozen=True)
class TranscriptRef:
    agent_id: str
    path: Path
    workspace: str
    updated_at: int
    is_subagent: bool


def _clean_user_text(raw: str) -> str:
    text = str(raw or "")
    match = USER_QUERY_PATTERN.search(text)
    if match:
        text = match.group(1)
    else:
        text = TAG_BLOCK_PATTERN.sub("", text)
        for _ in range(6):
            cleaned = GENERIC_TAG_PATTERN.sub("", text)
            if cleaned == text:
                break
            text = cleaned
        text = SELF_CLOSING_TAG_PATTERN.sub("", text)
    text = text.replace("[Image]", "").strip()
    return " ".join(text.split())


def _blocks_from_content(content: object) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    if not isinstance(content, list):
        return blocks
    for block in content:
        if not isinstance(block, dict):
            continue
        block_type = str(block.get("type") or "").strip()
        if block_type == "text":
            text = str(block.get("text") or "").strip()
            if text:
                blocks.append({"type": "text", "text": text})
        elif block_type == "tool_use":
            name = str(block.get("name") or "tool").strip() or "tool"
            tool_input = block.get("input") if isinstance(block.get("input"), dict) else {}
            summary = _tool_summary(name, tool_input)
            blocks.append(
                {
                    "type": "tool",
                    "name": name,
                    "input": tool_input,
                    "summary": summary,
                }
            )
    return blocks


def _tool_summary(name: str, tool_input: dict[str, Any]) -> str:
    if name in {"Read", "Write", "StrReplace", "Delete"}:
        path = tool_input.get("path")
        if isinstance(path, str) and path.strip():
            return f"{name} {path.strip()}"
    if name == "Shell":
        command = tool_input.get("command")
        if isinstance(command, str) and command.strip():
            return f"Shell {command.strip()[:120]}"
    if name == "Task":
        description = tool_input.get("description")
        if isinstance(description, str) and description.strip():
            return f"Task {description.strip()[:120]}"
    encoded = json.dumps(tool_input, ensure_ascii=True, sort_keys=True)
    return f"{name} {encoded[:120]}"


def title_from_transcript(path: Path, messages: list[dict[str, Any]] | None = None) -> str:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            for _ in range(20):
                line = handle.readline()
                if not line:
                    break
                match = TITLE_JSON_PATTERN.search(line)
                if match:
                    return match.group(1).strip()[:120]
    except OSError:
        pass
    if messages:
        for row in messages:
            if row.get("role") != "user":
                continue
            for block in row.get("blocks") or []:
                if block.get("type") == "text" and block.get("text"):
                    text = str(block["text"]).strip()
                    if text:
                        return text[:120]
    fallback = path.stem.replace("-", " ")[:120]
    return fallback or "Cursor IDE agent"


def parse_transcript(path: Path, *, max_messages: int = 500) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            for index, line in enumerate(handle):
                if len(messages) >= max_messages:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(payload, dict):
                    continue
                role = str(payload.get("role") or "").strip().lower()
                if role not in {"user", "assistant"}:
                    continue
                message = payload.get("message")
                content = message.get("content") if isinstance(message, dict) else None
                blocks = _blocks_from_content(content)
                if role == "user":
                    for block in blocks:
                        if block.get("type") == "text":
                            block["text"] = _clean_user_text(str(block.get("text") or ""))
                    blocks = [block for block in blocks if block.get("text") or block.get("type") != "text"]
                if not blocks:
                    continue
                messages.append(
                    {
                        "id": f"msg-{index}",
                        "role": role,
                        "blocks": blocks,
                    }
                )
    except OSError:
        return []
    return messages


def discover_transcripts(projects_root: Path, *, limit: int = 200) -> list[TranscriptRef]:
    items: list[TranscriptRef] = []
    if not projects_root.is_dir():
        return items
    seen: set[str] = set()
    project_dirs = sorted(projects_root.iterdir(), key=lambda row: row.stat().st_mtime if row.exists() else 0, reverse=True)
    for project_dir in project_dirs:
        if not project_dir.is_dir():
            continue
        transcript_dir = project_dir / "agent-transcripts"
        if not transcript_dir.is_dir():
            continue
        candidates: list[Path] = []
        for path in transcript_dir.rglob("*.jsonl"):
            if not path.is_file():
                continue
            candidates.append(path)
        candidates.sort(key=lambda row: row.stat().st_mtime, reverse=True)
        for path in candidates:
            agent_id = path.stem
            if not agent_id or agent_id in seen:
                continue
            try:
                stat = path.stat()
            except OSError:
                continue
            seen.add(agent_id)
            items.append(
                TranscriptRef(
                    agent_id=agent_id,
                    path=path,
                    workspace=project_dir.name,
                    updated_at=int(stat.st_mtime),
                    is_subagent="/subagents/" in str(path).replace("\\", "/"),
                )
            )
            if len(items) >= limit:
                return items
    return items


def load_session(path: Path, *, agent_id: str, workspace: str, updated_at: int, is_subagent: bool) -> dict[str, Any]:
    messages = parse_transcript(path)
    title = title_from_transcript(path, messages)
    return {
        "agent_id": agent_id,
        "title": title,
        "workspace": workspace,
        "status": "idle",
        "source": "ide",
        "updated_at": updated_at,
        "read_only": True,
        "is_subagent": is_subagent,
        "transcript_path": str(path),
        "message_count": len(messages),
        "messages": messages,
    }


def index_transcripts(projects_root: Path, *, limit: int = 200) -> dict[str, TranscriptRef]:
    return {row.agent_id: row for row in discover_transcripts(projects_root, limit=limit)}
