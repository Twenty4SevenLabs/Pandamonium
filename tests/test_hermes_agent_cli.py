from src.hermes_agent_cli import build_agent_cli_command, parse_profile_slugs


def test_parse_profile_slugs_from_table():
    sample = """
 Profile          Model                        Gateway
 ───────────────    ───────────────────────────    ───────────
 ◆default         minimax/minimax-m3:free      running
  hermes-bert     unsloth/Qwen3.5-9B-GGUF      stopped
  hermes-amy      unsloth/Qwen3.5-9B-GGUF      stopped
"""
    assert parse_profile_slugs(sample) == ["default", "hermes-bert", "hermes-amy"]


def test_build_message_command_uses_profile_and_hermes_chat():
    cmd = build_agent_cli_command(
        "message",
        {"profile": "hermes-bert", "message": "Ping from Panda"},
    )
    assert "HERMES_PROFILE='hermes-bert'" in cmd or 'HERMES_PROFILE=hermes-bert' in cmd
    assert "hermes chat --query-file - --oneshot -Q" in cmd
    assert "Ping from Panda" in cmd


def test_build_send_command():
    cmd = build_agent_cli_command(
        "send",
        {"target": "telegram:Jason", "message": "Deploy finished"},
    )
    assert cmd.startswith("hermes send --to ")
    assert "Deploy finished" in cmd


def test_profiles_list_action():
    assert build_agent_cli_command("profiles_list", {}) == "hermes profile list"
