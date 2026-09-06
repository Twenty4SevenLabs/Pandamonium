#!/usr/bin/env python3
"""SSH cookbook helpers for Pandamonium → vm-hermes access."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]


class SshCookbookTests(unittest.TestCase):
    def test_write_agent_ssh_config_uses_cookbook_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp) / "data"
            ssh_mount = Path(tmp) / "ssh_mount"
            ssh_mount.mkdir()
            (ssh_mount / "id_ed25519").write_text("fake-key\n", encoding="utf-8")

            with mock.patch("src.ssh_cookbook.DATA_DIR", str(data_dir)), mock.patch(
                "src.ssh_cookbook.SSH_DIR", ssh_mount
            ), mock.patch("src.ssh_cookbook.SSH_IDENTITY", ssh_mount / "id_ed25519"), mock.patch(
                "src.ssh_cookbook.SSH_KNOWN_HOSTS", ssh_mount / "known_hosts"
            ):
                from src.ssh_cookbook import write_agent_ssh_config

                path = write_agent_ssh_config()
                text = path.read_text(encoding="utf-8")
                self.assertIn("Host vm-hermes 192.168.1.192", text)
                self.assertIn("User openclaw1", text)
                self.assertIn(str(ssh_mount / "id_ed25519"), text)
                self.assertIn("UserKnownHostsFile", text)
                self.assertIn("RequestTTY no", text)
                wrapper = (data_dir / "bin" / "ssh").read_text(encoding="utf-8")
                self.assertIn("-T", wrapper)
                self.assertIn("RequestTTY=no", wrapper)
                self.assertIn("-F", wrapper)
                self.assertIn("ssh", wrapper)

    def test_hermes_ssh_argv_is_non_interactive(self):
        with tempfile.TemporaryDirectory() as tmp:
            ssh_mount = Path(tmp) / "ssh_mount"
            ssh_mount.mkdir()
            config = ssh_mount / "config"
            config.write_text("# test\n", encoding="utf-8")

            with mock.patch("src.ssh_cookbook.SSH_DIR", ssh_mount):
                from src.ssh_cookbook import hermes_ssh_argv, wrap_hermes_remote_command

                argv = hermes_ssh_argv("hermes kanban boards list")
                self.assertEqual(argv[0], "/usr/bin/ssh")
                self.assertIn("-T", argv)
                self.assertIn("RequestTTY=no", argv)
                self.assertEqual(argv[argv.index("-F") + 1], str(config))
                self.assertEqual(argv[-2:], ["vm-hermes", wrap_hermes_remote_command("hermes kanban boards list")])
                self.assertIn("hermes kanban boards list", argv[-1])
                self.assertIn("HERMES_QUIET=1", argv[-1])
                self.assertIn("HERMES_KANBAN_BOARD=", argv[-1])
                self.assertIn("bash -lc", argv[-1])

    def test_refresh_known_hosts_appends_scan_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            ssh_mount = Path(tmp)
            known_hosts = ssh_mount / "known_hosts"
            known_hosts.write_text("# empty\n", encoding="utf-8")
            fake_scan = b"|1|abc|def ssh-ed25519 AAAATEST\n"

            with mock.patch("src.ssh_cookbook.SSH_DIR", ssh_mount), mock.patch(
                "src.ssh_cookbook.SSH_KNOWN_HOSTS", known_hosts
            ), mock.patch("src.ssh_cookbook._run_keyscan", return_value=fake_scan):
                from src.ssh_cookbook import refresh_known_hosts

                refresh_known_hosts(targets=("192.168.1.192",))
                body = known_hosts.read_bytes()
                self.assertIn(b"AAAATEST", body)


if __name__ == "__main__":
    unittest.main()
