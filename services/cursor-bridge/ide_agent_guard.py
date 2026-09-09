"""Guardrails: IDE transcript agent IDs must never hit SDK resume_agent."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

DEFAULT_IDE_PROJECTS_ROOT = Path("/home/labsadmin/.cursor/projects")


class IdeAgentResumeForbidden(RuntimeError):
    """Raised when code would call SDK resume on an IDE-owned transcript agent id."""

    code = "ide_agent_resume_forbidden"


def ide_projects_root() -> Path:
    import os

    override = str(os.getenv("PANDAMONIUM_PC_CURSOR_PROJECTS_ROOT") or "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return DEFAULT_IDE_PROJECTS_ROOT


def is_ide_transcript_agent_id(agent_id: str, projects_root: Path | None = None) -> bool:
    """True when agent_id matches a Cursor IDE transcript under projects_root."""
    candidate = str(agent_id or "").strip()
    if not candidate or not UUID_RE.fullmatch(candidate):
        return False
    root = (projects_root or ide_projects_root()).resolve()
    if not root.is_dir():
        return False
    pattern = f"**/agent-transcripts/**/{candidate}.jsonl"
    return any(root.glob(pattern))


def resolve_sdk_resume_id(agent_id: str, row: dict[str, Any] | None = None) -> str:
    """Return the SDK-local id safe for resume_agent.

    IDE transcript UUIDs are never resumed directly. Forked rows must resume via
    sdk_agent_id (the Panda-owned local agent).
    """
    candidate = str(agent_id or "").strip()
    if not candidate:
        raise IdeAgentResumeForbidden("empty_agent_id")
    registry = row if isinstance(row, dict) else {}
    sdk_id = str(registry.get("sdk_agent_id") or "").strip()
    if is_ide_transcript_agent_id(candidate):
        if registry.get("forked") and sdk_id:
            return sdk_id
        raise IdeAgentResumeForbidden(f"ide_transcript_id:{candidate}")
    if sdk_id and registry.get("forked"):
        return sdk_id
    return candidate
