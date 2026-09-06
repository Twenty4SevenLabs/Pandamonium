#!/usr/bin/env python3
"""Tests for Cursor/OpenCode → Pandamonium import script."""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path("/mnt/dev-env/projects/pandamonium")
SCRIPT = REPO / "scripts" / "import_cursor_opencode_bundle.py"


def load_module():
    spec = importlib.util.spec_from_file_location("import_cursor_opencode_bundle", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


class CursorOpenCodeImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SCRIPT.is_file():
            raise unittest.SkipTest(f"missing import script: {SCRIPT}")
        cls.mod = load_module()

    def test_categorize_skill(self):
        self.assertEqual(self.mod.categorize_skill("hermes-orchestrator"), "hermes")
        self.assertEqual(self.mod.categorize_skill("brainstorming"), "superpowers")
        self.assertEqual(self.mod.categorize_skill("coding-trinity"), "trinity")
        self.assertEqual(self.mod.categorize_skill("cursor-canvas"), "cursor")
        self.assertEqual(self.mod.categorize_skill("prisma-cli-dev"), "prisma")

    def test_mcp_config_count(self):
        self.assertEqual(len(self.mod.MCP_SERVERS), 12)

    def test_remote_mcp_servers_use_streamable_http(self):
        by_name = {spec["name"]: spec for spec in self.mod.MCP_SERVERS}
        for name in ("context7", "prisma-remote", "neon", "figma"):
            spec = by_name[name]
            self.assertEqual(spec["transport"], "http", name)
            self.assertTrue(str(spec.get("url") or "").startswith("https://"), name)

    def test_gitlab_uses_stdio_against_self_hosted_instance(self):
        gitlab = {spec["name"]: spec for spec in self.mod.MCP_SERVERS}["gitlab"]
        self.assertEqual(gitlab["transport"], "stdio")
        self.assertEqual(gitlab["command"], "npx")
        self.assertIn("gitlab-mcp", " ".join(gitlab["args"]))
        env = gitlab["env"]
        self.assertIn("GITLAB_API_URL", env)
        self.assertIn("GITLAB_PERSONAL_ACCESS_TOKEN", env)
        self.assertIn("${GITLAB_TOKEN}", env["GITLAB_PERSONAL_ACCESS_TOKEN"])

    def test_hermes_ssh_targets_lan_ip_noninteractively(self):
        hermes = {spec["name"]: spec for spec in self.mod.MCP_SERVERS}["hermes"]
        joined = " ".join(hermes["args"])
        self.assertIn("192.168.1.192", joined)
        self.assertNotIn("vm-hermes", joined)
        self.assertIn("BatchMode=yes", joined)
        self.assertIn("-T", joined)
        self.assertIn("RequestTTY=no", joined)

    def test_hermes_mcp_uses_cookbook_key_and_kanban_tools_server(self):
        hermes = {spec["name"]: spec for spec in self.mod.MCP_SERVERS}["hermes"]
        args = hermes["args"]
        self.assertEqual(hermes["command"], "ssh")
        self.assertIn("-i", args)
        self.assertIn("/app/.ssh/id_ed25519", args)
        self.assertIn("IdentitiesOnly=yes", args)
        remote = args[-1]
        self.assertIn("hermes_tools_mcp_server", remote)
        self.assertNotIn("hermes mcp serve", remote)

    def test_hermes_messaging_mcp_uses_serve_bridge(self):
        messaging = {spec["name"]: spec for spec in self.mod.MCP_SERVERS}["hermes-messaging"]
        args = messaging["args"]
        self.assertEqual(messaging["command"], "ssh")
        self.assertIn("/app/.ssh/id_ed25519", args)
        remote = args[-1]
        self.assertIn("hermes mcp serve", remote)
        self.assertNotIn("hermes_tools_mcp_server", remote)

    def test_stdio_secret_placeholders_are_env_refs(self):
        by_name = {spec["name"]: spec for spec in self.mod.MCP_SERVERS}
        self.assertEqual(
            by_name["github"]["env"]["GITHUB_PERSONAL_ACCESS_TOKEN"],
            "${GITHUB_TOKEN}",
        )
        self.assertEqual(by_name["aikido"]["env"]["AIKIDO_API_KEY"], "${AIKIDO_API_KEY}")
        self.assertEqual(
            by_name["context7"]["env"]["CONTEXT7_API_KEY"],
            "${CONTEXT7_API_KEY}",
        )

    def test_duckduckgo_mcp_uses_npx_without_api_key(self):
        ddg = {spec["name"]: spec for spec in self.mod.MCP_SERVERS}["duckduckgo"]
        self.assertEqual(ddg["transport"], "stdio")
        self.assertEqual(ddg["command"], "npx")
        self.assertEqual(ddg["args"], ["-y", "@oevortex/ddg_search@latest"])
        self.assertEqual(ddg.get("url"), None)
        self.assertFalse(ddg.get("env"))

    def test_dry_run_import(self):
        source = Path.home() / ".config" / "opencode"
        if not (source / "skills").is_dir():
            self.skipTest("opencode bundle not present")
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "data"
            data.mkdir()
            (data / "settings.json").write_text("{}", encoding="utf-8")
            (data / "presets.json").write_text("{}", encoding="utf-8")
            (data / "app.db").write_bytes(b"")
            counts = self.mod.import_skills(source, data, dry_run=True)
            total = sum(counts.values())
            self.assertGreaterEqual(total, 130)
            self.assertIn("hermes", counts)
            self.assertIn("superpowers", counts)
            self.assertIn("trinity", counts)

    def test_identity_update(self):
        source = Path.home() / ".config" / "opencode"
        if not (source / "AGENTS.md").is_file():
            self.skipTest("AGENTS.md missing")
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "data"
            data.mkdir()
            (data / "settings.json").write_text('{"agent_constitution":"old"}', encoding="utf-8")
            (data / "presets.json").write_text("{}", encoding="utf-8")
            self.mod.update_identity(source, data, dry_run=False)
            settings = json.loads((data / "settings.json").read_text(encoding="utf-8"))
            presets = json.loads((data / "presets.json").read_text(encoding="utf-8"))
            self.assertEqual(settings["agent_constitution_version"], "3")
            self.assertIn("Hermes", settings["agent_constitution"])
            self.assertIn("Context7", settings["agent_constitution"])
            self.assertIn("read and write", settings["agent_constitution"].lower())
            self.assertNotIn("do not implement project code unless", settings["agent_constitution"].lower())
            self.assertIn("hermes_orchestrator", presets)

    def test_condensed_constitution_is_cluster_operator(self):
        text = self.mod.CONDENSED_CONSTITUTION
        self.assertLessEqual(len(text), 16_000)
        self.assertIn("Pandamonium", text)
        self.assertIn("Context7", text)
        self.assertIn("Hermes Kanban", text)
        self.assertIn("taste-skills-router", text)
        self.assertIn("read and write", text.lower())
        self.assertIn("admin", text.lower())
        self.assertNotIn("do not implement project code unless", text.lower())

    def test_mcp_sqlite_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "data"
            data.mkdir()
            db = data / "app.db"
            conn = sqlite3.connect(db)
            conn.execute(
                """
                CREATE TABLE mcp_servers (
                    id VARCHAR PRIMARY KEY,
                    name VARCHAR NOT NULL,
                    transport VARCHAR NOT NULL,
                    command VARCHAR,
                    args TEXT,
                    env TEXT,
                    url VARCHAR,
                    is_enabled BOOLEAN,
                    oauth_config TEXT,
                    disabled_tools TEXT,
                    oauth_tokens TEXT,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL
                )
                """
            )
            conn.commit()
            conn.close()
            count = self.mod.import_mcp(data, dry_run=False)
            self.assertEqual(count, 12)
            conn = sqlite3.connect(db)
            rows = conn.execute("SELECT name FROM mcp_servers").fetchall()
            conn.close()
            self.assertEqual(len(rows), 12)
            names = {row[0] for row in rows}
            self.assertIn("duckduckgo", names)
            self.assertIn("hermes-messaging", names)


if __name__ == "__main__":
    unittest.main()
