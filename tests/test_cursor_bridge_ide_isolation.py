from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
SERVICE_PATH = ROOT / "services" / "cursor-bridge" / "cursor_bridge_service.py"
GUARD_PATH = ROOT / "services" / "cursor-bridge" / "ide_agent_guard.py"


def _load_service():
    spec = importlib.util.spec_from_file_location("cursor_bridge_service_isolation_test", SERVICE_PATH)
    assert spec and spec.loader
    service = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = service
    spec.loader.exec_module(service)
    return service


def _load_guard():
    spec = importlib.util.spec_from_file_location("cursor_bridge_ide_guard_isolation_test", GUARD_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _seed_ide_transcript(projects_root: Path, ide_id: str) -> None:
    path = projects_root / "workspace" / "agent-transcripts" / ide_id / f"{ide_id}.jsonl"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"role": "user", "message": {"content": "hello"}}) + "\n", encoding="utf-8")


@pytest.fixture()
def service(tmp_path: Path, monkeypatch):
    mod = _load_service()
    state_dir = tmp_path / "cursor-bridge"
    state_dir.mkdir()
    projects_root = tmp_path / "projects"
    projects_root.mkdir()
    monkeypatch.setattr(mod, "STATE_DIR", state_dir)
    monkeypatch.setattr(mod, "REGISTRY_FILE", state_dir / "agents.json")
    monkeypatch.setattr(mod, "SETTINGS_FILE", state_dir / "settings.json")
    monkeypatch.setattr(mod, "WORKSPACES", {"pandamonium": str(tmp_path / "ws")})
    monkeypatch.setattr(mod, "DEFAULT_WORKSPACE", "pandamonium")
    (tmp_path / "ws").mkdir()
    monkeypatch.setenv("PANDAMONIUM_PC_CURSOR_PROJECTS_ROOT", str(projects_root))
    mod.STATE.api_key = "cursor_test_key"
    mod.STATE.client = None
    mod.STATE.agent_handles = {}
    mod.STATE.lock = __import__("asyncio").Lock()
    return mod, projects_root


@pytest.mark.asyncio
async def test_forked_send_never_resumes_ide_transcript_ids(service, monkeypatch):
    mod, projects_root = service
    guard = _load_guard()
    ide_id = "6d91f84e-cf09-4c68-86a7-1f0e1ed631a5"
    sdk_id = "panda-owned-sdk-agent-99"
    _seed_ide_transcript(projects_root, ide_id)

    resume_calls: list[str] = []

    async def fake_resume(agent_id: str, options: dict):
        resume_calls.append(agent_id)
        agent = MagicMock()
        agent.send = AsyncMock(return_value=MagicMock(run_id="run-1", id="run-1", messages=lambda: _empty_async()))
        return agent

    client = MagicMock()
    client.resume_agent = AsyncMock(side_effect=fake_resume)

    registry = {
        ide_id: {
            "agent_id": ide_id,
            "sdk_agent_id": sdk_id,
            "title": "IDE chat",
            "workspace": "pandamonium",
            "status": "idle",
            "source": "ide",
            "forked": True,
            "updated_at": 1,
        }
    }
    (mod.REGISTRY_FILE).write_text(json.dumps(registry), encoding="utf-8")

    async def fake_consume(*_args, **_kwargs):
        return None

    monkeypatch.setattr(mod, "_consume_run", fake_consume)
    monkeypatch.setattr(mod, "_require_auth", lambda *_a, **_k: None)
    monkeypatch.setattr(mod, "_ensure_client", AsyncMock(return_value=client))

    await mod.send_agent(ide_id, {"prompt": "Continue from fork"}, authorization="Bearer test")

    assert resume_calls == [sdk_id]
    for called_id in resume_calls:
        assert not guard.is_ide_transcript_agent_id(called_id, projects_root)


@pytest.mark.asyncio
async def test_fork_endpoint_runs_compaction_and_skips_ide_resume(service, monkeypatch):
    mod, projects_root = service
    ide_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    _seed_ide_transcript(projects_root, ide_id)
    sdk_id = "new-sdk-agent-42"

    resume_calls: list[str] = []
    client = MagicMock()
    client.resume_agent = AsyncMock(side_effect=lambda agent_id, _options: resume_calls.append(agent_id))
    created_agent = MagicMock()
    created_agent.agent_id = sdk_id

    handoff_json = json.dumps(
        {
            "goal": "Finish isolation",
            "files": ["cursor_bridge_service.py"],
            "next_steps": ["Add tests"],
            "summary": "Fork compaction wired",
        }
    )

    async def fake_compaction(_agent, _messages):
        return mod.parse_handoff_response(handoff_json)

    async def fake_create(options):
        return created_agent

    client.create_agent = AsyncMock(side_effect=fake_create)

    monkeypatch.setattr(mod, "_ensure_client", AsyncMock(return_value=client))
    monkeypatch.setattr(mod, "_run_fork_compaction", fake_compaction)
    monkeypatch.setattr(mod, "_require_auth", lambda *_a, **_k: None)
    monkeypatch.setattr(mod, "assert_agent_options", lambda options: options)
    monkeypatch.setattr(mod, "build_agent_options", lambda **kwargs: kwargs)
    monkeypatch.setattr(mod, "ensure_sdk_agent_store", lambda *_a, **_k: None)

    messages = [{"role": "user", "blocks": [{"type": "text", "text": f"line-{index}"}]} for index in range(20)]
    payload = await mod.fork_agent_endpoint(
        ide_id,
        {
            "workspace": "pandamonium",
            "cwd": str(mod.WORKSPACES["pandamonium"]),
            "title": "IDE chat",
            "messages": messages,
        },
        authorization="Bearer test",
    )

    assert payload["forked"] is True
    assert client.resume_agent.await_count == 0
    assert resume_calls == []
    row = json.loads(mod.REGISTRY_FILE.read_text(encoding="utf-8"))[ide_id]
    assert row["sdk_agent_id"] == sdk_id
    assert row["handoff"]["goal"] == "Finish isolation"
    assert len(row["pending_context"]) == 16


@pytest.mark.asyncio
async def test_resume_on_ide_id_returns_409(service):
    mod, projects_root = service
    ide_id = "6d91f84e-cf09-4c68-86a7-1f0e1ed631a5"
    _seed_ide_transcript(projects_root, ide_id)
    mod._require_auth = lambda *_a, **_k: None  # type: ignore[method-assign]

    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        await mod.resume_agent_endpoint(
            ide_id,
            {"workspace": "pandamonium", "cwd": str(mod.WORKSPACES["pandamonium"])},
            authorization="Bearer test",
        )
    assert exc.value.status_code == 409
    assert exc.value.detail == "ide_fork_required"


async def _empty_async():
    if False:  # pragma: no cover
        yield None
