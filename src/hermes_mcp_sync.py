"""Keep persisted Hermes MCP rows aligned with src.hermes_mcp_config."""

from __future__ import annotations

import json
import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from src.constants import DATA_DIR
from src.hermes_mcp_config import HERMES_MCP_SERVER_SPECS

logger = logging.getLogger(__name__)


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def sync_hermes_mcp_servers(data_dir: Path | None = None) -> int:
    """Upsert hermes + hermes-messaging rows in mcp_servers. Returns rows touched."""
    db_path = (data_dir or Path(DATA_DIR)) / "app.db"
    if not db_path.is_file():
        logger.debug("Hermes MCP sync skipped — no database at %s", db_path)
        return 0

    now = _utc_now()
    updated = 0
    conn = sqlite3.connect(db_path)
    try:
        for spec in HERMES_MCP_SERVER_SPECS:
            name = spec["name"]
            args_json = json.dumps(spec.get("args") or [])
            env_json = json.dumps(spec.get("env") or {})
            row = conn.execute("SELECT id, args, command FROM mcp_servers WHERE name = ?", (name,)).fetchone()
            if row is None:
                conn.execute(
                    """
                    INSERT INTO mcp_servers (
                        id, name, transport, command, args, env, url, is_enabled,
                        oauth_config, disabled_tools, oauth_tokens, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, NULL, NULL, NULL, ?, ?)
                    """,
                    (
                        str(uuid.uuid4()),
                        name,
                        spec["transport"],
                        spec.get("command"),
                        args_json,
                        env_json,
                        spec.get("url"),
                        now,
                        now,
                    ),
                )
                updated += 1
                continue

            server_id, old_args, old_command = row
            if old_args != args_json or old_command != spec.get("command"):
                conn.execute(
                    """
                    UPDATE mcp_servers SET
                        transport = ?, command = ?, args = ?, env = ?, url = ?,
                        is_enabled = 1, updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        spec["transport"],
                        spec.get("command"),
                        args_json,
                        env_json,
                        spec.get("url"),
                        now,
                        server_id,
                    ),
                )
                updated += 1
        if updated:
            conn.commit()
            logger.info("Synced %s Hermes MCP server row(s)", updated)
        return updated
    finally:
        conn.close()
