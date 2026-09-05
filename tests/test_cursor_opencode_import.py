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
        self.assertEqual(len(self.mod.MCP_SERVERS), 10)

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
            self.assertEqual(settings["agent_constitution_version"], "2")
            self.assertIn("Hermes", settings["agent_constitution"])
            self.assertIn("Context7", settings["agent_constitution"])
            self.assertIn("hermes_orchestrator", presets)

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
            self.assertEqual(count, 10)
            conn = sqlite3.connect(db)
            rows = conn.execute("SELECT name FROM mcp_servers").fetchall()
            conn.close()
            self.assertEqual(len(rows), 10)


if __name__ == "__main__":
    unittest.main()
