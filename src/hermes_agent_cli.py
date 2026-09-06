"""Gateway-level Hermes agent messaging for Pandamonium → vm-hermes.

Hermes specialist profiles (hermes-bert, hermes-amy, …) are reached with
``HERMES_PROFILE=<slug> hermes chat --oneshot``. External platforms (Telegram,
Discord, …) use ``hermes send`` or the hermes-messaging MCP bridge.
"""

from __future__ import annotations

import re
import shlex
from typing import Any, Mapping

_PROFILE_TABLE_RE = re.compile(
    r"^\s*(?P<marker>[◆*])?\s*(?P<profile>[a-zA-Z0-9][a-zA-Z0-9._-]*)\s+",
    re.MULTILINE,
)


def parse_profile_slugs(table_output: str) -> list[str]:
    """Extract profile ids from ``hermes profile list`` table output."""
    profiles: list[str] = []
    for line in (table_output or "").splitlines():
        if not line.strip() or line.strip().startswith("─") or "Profile" in line and "Model" in line:
            continue
        match = _PROFILE_TABLE_RE.match(line)
        if match:
            profiles.append(match.group("profile"))
    return profiles


def build_agent_cli_command(action: str, args: Mapping[str, Any]) -> str:
    """Build a remote shell command for Hermes gateway agent messaging."""
    action = (action or "").strip().lower()
    if not action:
        raise ValueError("hermes_agent: action is required")

    if action == "profiles_list":
        return "hermes profile list"

    if action == "gateway_list":
        return "hermes gateway list"

    if action == "send_targets":
        platform = str(args.get("platform") or "").strip()
        if platform:
            return f"hermes send --list {shlex.quote(platform)}"
        return "hermes send --list"

    if action == "message":
        profile = str(args.get("profile") or "").strip()
        message = str(args.get("message") or "")
        if not profile:
            raise ValueError("hermes_agent: message requires profile")
        if not message.strip():
            raise ValueError("hermes_agent: message requires non-empty message text")
        quoted = shlex.quote(message)
        profile_q = shlex.quote(profile)
        return (
            f"HERMES_PROFILE={profile_q} hermes chat --query-file - --oneshot -Q "
            f"<<<{quoted}"
        )

    if action == "send":
        target = str(args.get("target") or "").strip()
        message = str(args.get("message") or "")
        if not target:
            raise ValueError("hermes_agent: send requires target")
        if not message.strip():
            raise ValueError("hermes_agent: send requires non-empty message text")
        return (
            f"hermes send --to {shlex.quote(target)} "
            f"{shlex.quote(message)} -q"
        )

    if action == "raw":
        command = str(args.get("command") or "").strip()
        if not command:
            raise ValueError("hermes_agent: action=raw requires command")
        return command

    raise ValueError(
        "hermes_agent: unknown action "
        f"{action!r} (expected profiles_list, gateway_list, send_targets, message, send, raw)"
    )
