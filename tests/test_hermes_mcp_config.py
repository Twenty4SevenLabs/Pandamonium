import json

from src.hermes_mcp_config import HERMES_MCP_SERVER_SPECS, hermes_mcp_server_spec


def test_hermes_messaging_uses_accept_hooks_and_ssh_t():
    spec = hermes_mcp_server_spec("hermes-messaging")
    assert spec is not None
    args = spec["args"]
    assert "-T" in args
    assert "RequestTTY=no" in args
    remote = args[-1]
    assert "hermes mcp serve --accept-hooks" in remote
    assert "HERMES_REDACT_SECRETS=true" in remote


def test_hermes_kanban_mcp_uses_tools_server():
    spec = hermes_mcp_server_spec("hermes")
    assert spec is not None
    remote = spec["args"][-1]
    assert "hermes_tools_mcp_server" in remote


def test_specs_are_json_serializable():
    json.dumps(HERMES_MCP_SERVER_SPECS)
