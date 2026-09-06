"""Canonical Hermes MCP stdio-over-SSH server definitions for Pandamonium."""

from __future__ import annotations

import json
from typing import Any

# Non-interactive SSH prefix for MCP stdio bridges (must match docker bind mount).
HERMES_MCP_SSH_PREFIX: list[str] = [
    "-T",
    "-o",
    "RequestTTY=no",
    "-i",
    "/app/.ssh/id_ed25519",
    "-o",
    "IdentitiesOnly=yes",
    "-o",
    "BatchMode=yes",
    "-o",
    "StrictHostKeyChecking=accept-new",
    "-o",
    "UserKnownHostsFile=/app/.ssh/known_hosts",
    "-o",
    "ConnectTimeout=10",
    "openclaw1@192.168.1.192",
    "bash",
    "-lc",
]

_HERMES_TOOLS_REMOTE = (
    "cd /home/openclaw1/.hermes/hermes-agent && "
    "HERMES_QUIET=1 HERMES_REDACT_SECRETS=true "
    "/home/openclaw1/.hermes/hermes-agent/venv/bin/python "
    "-m agent.transports.hermes_tools_mcp_server"
)

_HERMES_MESSAGING_REMOTE = (
    "cd /home/openclaw1/.hermes/hermes-agent && "
    "HERMES_QUIET=1 HERMES_REDACT_SECRETS=true "
    "/home/openclaw1/.hermes/hermes-agent/venv/bin/hermes mcp serve --accept-hooks"
)

HERMES_MCP_SERVER_SPECS: list[dict[str, Any]] = [
    {
        "name": "hermes",
        "transport": "stdio",
        "command": "ssh",
        "args": [*HERMES_MCP_SSH_PREFIX, _HERMES_TOOLS_REMOTE],
        "env": {},
        "url": None,
    },
    {
        "name": "hermes-messaging",
        "transport": "stdio",
        "command": "ssh",
        "args": [*HERMES_MCP_SSH_PREFIX, _HERMES_MESSAGING_REMOTE],
        "env": {},
        "url": None,
    },
]


def hermes_mcp_server_spec(name: str) -> dict[str, Any] | None:
    for spec in HERMES_MCP_SERVER_SPECS:
        if spec["name"] == name:
            return spec
    return None


def hermes_mcp_args_json(name: str) -> str:
    spec = hermes_mcp_server_spec(name)
    if spec is None:
        raise KeyError(name)
    return json.dumps(spec.get("args") or [])
