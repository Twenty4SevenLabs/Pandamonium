"""Gateway-level Hermes agent messaging — one-shot chat with specialist profiles."""

from __future__ import annotations

import json
from typing import Any

from src.agent_tools.subprocess_tools import HermesSshTool


class HermesAgentTool:
    """Message Hermes specialist profiles or external gateway targets on vm-hermes."""

    async def execute(self, content: str, ctx: dict) -> dict:
        from src.hermes_agent_cli import build_agent_cli_command

        raw = (content or "").strip()
        if not raw:
            return {"error": "hermes_agent: empty arguments", "exit_code": 1}

        try:
            if raw.startswith("{"):
                args: dict[str, Any] = json.loads(raw)
            else:
                args = {"action": "raw", "command": raw}
        except json.JSONDecodeError as exc:
            return {
                "error": f"hermes_agent: arguments must be JSON ({exc})",
                "exit_code": 1,
            }

        if not isinstance(args, dict):
            return {"error": "hermes_agent: arguments must be a JSON object", "exit_code": 1}

        action = str(args.get("action") or "").strip().lower()
        if not action:
            return {"error": "hermes_agent: action is required", "exit_code": 1}

        try:
            remote = build_agent_cli_command(action, args)
        except ValueError as exc:
            return {"error": str(exc), "exit_code": 1}

        return await HermesSshTool().execute(remote, ctx)
