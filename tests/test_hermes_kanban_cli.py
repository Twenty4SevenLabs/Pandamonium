#!/usr/bin/env python3
"""Hermes Kanban CLI builder and normalizer tests."""

from __future__ import annotations

import unittest

from src.hermes_kanban_cli import (
    build_kanban_cli_command,
    cli_usage_hint,
    normalize_hermes_cli_command,
)


class HermesKanbanCliTests(unittest.TestCase):
    def test_normalize_create_title_flag(self):
        raw = 'hermes kanban create --title "Smoke" --body "hi" --assignee default'
        fixed = normalize_hermes_cli_command(raw)
        self.assertIn('hermes kanban create "Smoke"', fixed)
        self.assertNotIn("--title", fixed)

    def test_build_create_uses_positional_title(self):
        cmd = build_kanban_cli_command(
            "create",
            {
                "title": "Test card",
                "body": "Body text",
                "assignee": "default",
                "created_by": "pandamonium",
            },
        )
        self.assertIn("HERMES_KANBAN_BOARD=", cmd)
        self.assertIn('hermes kanban create', cmd)
        self.assertIn("'Test card'", cmd)
        self.assertIn("--body", cmd)
        self.assertIn("--assignee", cmd)
        self.assertNotIn("--title", cmd)

    def test_build_archive_multiple_ids(self):
        cmd = build_kanban_cli_command(
            "archive",
            {"task_ids": ["t_abc", "t_def"], "board": "pandamonium"},
        )
        self.assertIn("hermes kanban archive", cmd)
        self.assertIn("t_abc", cmd)
        self.assertIn("t_def", cmd)

    def test_cli_usage_hint_for_bad_create(self):
        hint = cli_usage_hint('hermes kanban create --title "x"', 2)
        self.assertIn("positional title", hint)


if __name__ == "__main__":
    unittest.main()
