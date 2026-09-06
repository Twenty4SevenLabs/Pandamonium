from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GUARD_PATH = ROOT / "services" / "cursor-bridge" / "subscription_guard.py"
SPEC = importlib.util.spec_from_file_location("cursor_subscription_guard", GUARD_PATH)
guard = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(guard)


def test_assert_model_rejects_non_composer():
    with pytest.raises(guard.SubscriptionGuardError):
        guard.assert_model("gpt-4.1")


def test_assert_local_runtime_requires_cwd():
    with pytest.raises(guard.SubscriptionGuardError):
        guard.assert_local_runtime({"local": {}})


def test_assert_agent_options_rejects_cloud():
    with pytest.raises(guard.SubscriptionGuardError):
        guard.assert_agent_options(
            {
                "model": guard.REQUIRED_MODEL,
                "cloud": {"repos": ["owner/repo"]},
            }
        )


def test_assert_no_cloud_url_blocks_rest_agents():
    with pytest.raises(guard.SubscriptionGuardError):
        guard.assert_no_cloud_url("https://api.cursor.com/v1/agents")


def test_assert_cli_command_blocks_worker_start():
    with pytest.raises(guard.SubscriptionGuardError):
        guard.assert_cli_command(["cursor-agent", "worker", "start"])


def test_model_catalog_allows_sdk_model_objects():
    class Model:
        id = "composer-2.5"

    assert guard.model_catalog_allows_subscription([Model()]) is True


def test_title_from_prompt_truncates():
    title = guard.title_from_prompt("Build a very long prompt that should be truncated down for sidebar display")
    assert title.endswith("…")
    assert len(title) <= 120
