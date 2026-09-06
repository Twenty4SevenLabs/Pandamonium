"""Hermes Kanban CLI helpers for Pandamonium → vm-hermes.

Models often emit invalid ``hermes kanban create --title …`` syntax (title is
positional). This module builds correct commands and normalizes common mistakes.
"""

from __future__ import annotations

import re
import shlex
from typing import Any, Mapping

DEFAULT_HERMES_KANBAN_BOARD = "pandamonium"

_CREATE_TITLE_RE = re.compile(
    r"^(?P<prefix>.*?\bhermes\s+kanban\s+create)\s+--title\s+"
    r'(?P<title>"[^"]*"|\'[^\']*\'|\S+)(?P<rest>.*)$',
    re.IGNORECASE,
)


def normalize_hermes_cli_command(remote: str) -> str:
    """Fix common model mistakes in Hermes CLI commands over SSH."""
    remote = (remote or "").strip()
    if not remote:
        return remote

    match = _CREATE_TITLE_RE.match(remote)
    if match:
        remote = f"{match.group('prefix')} {match.group('title')}{match.group('rest')}"

    return remote


def _q(value: str) -> str:
    return shlex.quote(str(value))


def _board_env(board: str | None) -> str:
    slug = (board or DEFAULT_HERMES_KANBAN_BOARD).strip() or DEFAULT_HERMES_KANBAN_BOARD
    return f"HERMES_KANBAN_BOARD={_q(slug)} "


def build_kanban_cli_command(action: str, args: Mapping[str, Any]) -> str:
    """Build a Hermes kanban shell command (without SSH wrapper)."""
    action = (action or "").strip().lower()
    board_prefix = _board_env(args.get("board"))
    use_json = bool(args.get("json"))

    if action == "raw":
        command = str(args.get("command") or "").strip()
        if not command:
            raise ValueError("hermes_kanban: action=raw requires command")
        return normalize_hermes_cli_command(command)

    if action == "boards_list":
        parts = ["hermes", "kanban", "boards", "list"]
        if use_json:
            parts.append("--json")
        return board_prefix + " ".join(parts)

    if action == "list":
        parts = ["hermes", "kanban", "list"]
        status = args.get("status")
        if status:
            parts.extend(["--status", _q(str(status))])
        if use_json:
            parts.append("--json")
        return board_prefix + " ".join(parts)

    if action == "show":
        task_id = str(args.get("task_id") or "").strip()
        if not task_id:
            raise ValueError("hermes_kanban: show requires task_id")
        parts = ["hermes", "kanban", "show", _q(task_id)]
        if use_json:
            parts.append("--json")
        return board_prefix + " ".join(parts)

    if action == "create":
        title = str(args.get("title") or "").strip()
        if not title:
            raise ValueError("hermes_kanban: create requires title")
        parts = ["hermes", "kanban", "create", _q(title)]
        body = args.get("body")
        if body:
            parts.extend(["--body", _q(str(body))])
        assignee = args.get("assignee")
        if assignee:
            parts.extend(["--assignee", _q(str(assignee))])
        workspace = args.get("workspace")
        if workspace:
            parts.extend(["--workspace", _q(str(workspace))])
        created_by = args.get("created_by")
        if created_by:
            parts.extend(["--created-by", _q(str(created_by))])
        if use_json:
            parts.append("--json")
        return board_prefix + " ".join(parts)

    if action == "complete":
        task_id = str(args.get("task_id") or "").strip()
        if not task_id:
            raise ValueError("hermes_kanban: complete requires task_id")
        parts = ["hermes", "kanban", "complete", _q(task_id)]
        result = args.get("result")
        if result:
            parts.extend(["--result", _q(str(result))])
        if use_json:
            parts.append("--json")
        return board_prefix + " ".join(parts)

    if action == "archive":
        ids = args.get("task_ids") or []
        if isinstance(ids, str):
            ids = [ids]
        task_ids = [str(t).strip() for t in ids if str(t).strip()]
        if not task_ids:
            single = str(args.get("task_id") or "").strip()
            if single:
                task_ids = [single]
        if not task_ids:
            raise ValueError("hermes_kanban: archive requires task_id or task_ids")
        parts = ["hermes", "kanban", "archive"] + [_q(t) for t in task_ids]
        if use_json:
            parts.append("--json")
        return board_prefix + " ".join(parts)

    if action == "comment":
        task_id = str(args.get("task_id") or "").strip()
        comment = str(args.get("comment") or args.get("body") or "").strip()
        if not task_id or not comment:
            raise ValueError("hermes_kanban: comment requires task_id and comment")
        parts = ["hermes", "kanban", "comment", _q(task_id), "--body", _q(comment)]
        if use_json:
            parts.append("--json")
        return board_prefix + " ".join(parts)

    if action == "block":
        task_id = str(args.get("task_id") or "").strip()
        kind = str(args.get("kind") or "needs_input").strip()
        reason = str(args.get("reason") or args.get("body") or "").strip()
        if not task_id or not reason:
            raise ValueError("hermes_kanban: block requires task_id and reason")
        parts = [
            "hermes",
            "kanban",
            "block",
            _q(task_id),
            "--kind",
            _q(kind),
            _q(reason),
        ]
        if use_json:
            parts.append("--json")
        return board_prefix + " ".join(parts)

    if action == "dispatch":
        parts = ["hermes", "kanban", "dispatch"]
        if use_json:
            parts.append("--json")
        return board_prefix + " ".join(parts)

    raise ValueError(f"hermes_kanban: unknown action '{action}'")


def cli_usage_hint(remote: str, exit_code: int) -> str:
    """Return a short hint when Hermes CLI exits with usage error."""
    if exit_code != 2:
        return ""
    lower = (remote or "").lower()
    if "kanban create" in lower and "--title" in lower:
        return (
            "\nHINT: Hermes kanban create uses a positional title, not --title. "
            'Example: hermes kanban create "My title" --body "Details" --assignee default. '
            "Prefer the hermes_kanban tool or Hermes MCP kanban_create."
        )
    if "kanban" in lower:
        return (
            "\nHINT: For Kanban ops prefer hermes_kanban (structured) or Hermes MCP kanban_* tools. "
            f"Default board is {DEFAULT_HERMES_KANBAN_BOARD}; set board= or HERMES_KANBAN_BOARD=."
        )
    return ""
