"""Structured Hermes Kanban tool — correct CLI syntax, default pandamonium board."""

from __future__ import annotations

import json
from typing import Any

from src.agent_tools.subprocess_tools import HermesSshTool


class HermesKanbanTool:
    """Run Hermes Kanban CLI on vm-hermes with validated command building."""

    async def execute(self, content: str, ctx: dict) -> dict:
        from src.hermes_kanban_cli import build_kanban_cli_command

        raw = (content or "").strip()
        if not raw:
            return {"error": "hermes_kanban: empty arguments", "exit_code": 1}

        try:
            if raw.startswith("{"):
                args: dict[str, Any] = json.loads(raw)
            else:
                # Legacy single-line: treat as raw CLI after normalization.
                args = {"action": "raw", "command": raw}
        except json.JSONDecodeError as exc:
            return {
                "error": f"hermes_kanban: arguments must be JSON ({exc})",
                "exit_code": 1,
            }

        if not isinstance(args, dict):
            return {"error": "hermes_kanban: arguments must be a JSON object", "exit_code": 1}

        action = str(args.get("action") or "").strip().lower()
        if not action:
            return {"error": "hermes_kanban: action is required", "exit_code": 1}

        try:
            remote = build_kanban_cli_command(action, args)
        except ValueError as exc:
            return {"error": str(exc), "exit_code": 1}

        return await HermesSshTool().execute(remote, ctx)
