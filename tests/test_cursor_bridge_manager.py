from __future__ import annotations

import os
from unittest.mock import AsyncMock, patch

import pytest

from src import cursor_bridge_manager as mgr


def test_pc_ide_urls_merges_single_and_list():
    with patch.object(mgr, "PC_IDE_URL", "http://m3:8051"), patch.object(
        mgr,
        "PC_IDE_URLS_RAW",
        "http://m3:8051,http://192.168.1.2:8051,http://192.168.1.2:8051",
    ):
        assert mgr.pc_ide_urls() == [
            "http://m3:8051",
            "http://192.168.1.2:8051",
        ]


@pytest.mark.asyncio
async def test_list_ide_mirror_agents_merges_multiple_hosts():
    async def fake_fetch(client, base_url, headers):
        if base_url == "http://a:8051":
            return [{"agent_id": "shared", "title": "from-a", "updated_at": 1, "mirror_url": base_url}]
        return [
            {"agent_id": "shared", "title": "from-b", "updated_at": 5, "mirror_url": base_url},
            {"agent_id": "b-only", "title": "b", "updated_at": 3, "mirror_url": base_url},
        ]

    with patch.object(mgr, "pc_ide_urls", return_value=["http://a:8051", "http://b:8051"]), patch.object(
        mgr, "_pc_ide_headers", return_value={"Authorization": "Bearer t"}
    ), patch.object(mgr, "_fetch_ide_agents_from_url", side_effect=fake_fetch):
        items = await mgr.list_ide_mirror_agents()

    ids = [row["agent_id"] for row in items]
    assert ids == ["shared", "b-only"]
    shared = next(row for row in items if row["agent_id"] == "shared")
    assert shared["title"] == "from-b"
    assert shared["mirror_url"] == "http://b:8051"
