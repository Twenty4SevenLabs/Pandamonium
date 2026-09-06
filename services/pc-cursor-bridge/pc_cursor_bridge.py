#!/usr/bin/env python3
"""Read-only Windows/Linux companion that mirrors open Cursor IDE agent chats."""

from __future__ import annotations

import hmac
import json
import os
import re
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HOST = os.getenv("JARVIS_CURSOR_BRIDGE_HOST", "127.0.0.1")
PORT = int(os.getenv("JARVIS_CURSOR_BRIDGE_PORT", "8051"))
TOKEN_FILE = Path(os.getenv("JARVIS_CURSOR_BRIDGE_TOKEN_FILE", str(Path.home() / ".config/jarvis/cursor-bridge-token")))
PROJECTS_ROOT = Path(os.getenv("JARVIS_CURSOR_PROJECTS_ROOT", str(Path.home() / ".cursor" / "projects")))
TITLE_PATTERN = re.compile(r'"title"\s*:\s*"([^"]{1,200})"')


def _token() -> str:
    try:
        return TOKEN_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def _authorized(header: str | None) -> bool:
    expected = _token()
    supplied = (header or "").removeprefix("Bearer ").strip()
    return bool(expected and supplied and hmac.compare_digest(expected, supplied))


def _title_from_transcript(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            for _ in range(20):
                line = handle.readline()
                if not line:
                    break
                match = TITLE_PATTERN.search(line)
                if match:
                    return match.group(1).strip()[:120]
    except OSError:
        pass
    return path.stem.replace("-", " ")[:120] or "Cursor IDE agent"


def _scan_ide_agents(limit: int = 200) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    if not PROJECTS_ROOT.is_dir():
        return items
    for project_dir in sorted(PROJECTS_ROOT.iterdir(), key=lambda row: row.stat().st_mtime, reverse=True):
        transcript_dir = project_dir / "agent-transcripts"
        if not transcript_dir.is_dir():
            continue
        for transcript in sorted(transcript_dir.glob("*.jsonl"), key=lambda row: row.stat().st_mtime, reverse=True):
            try:
                stat = transcript.stat()
            except OSError:
                continue
            agent_id = transcript.stem
            items.append(
                {
                    "agent_id": agent_id,
                    "title": _title_from_transcript(transcript),
                    "workspace": project_dir.name,
                    "status": "idle",
                    "source": "ide",
                    "updated_at": int(stat.st_mtime),
                }
            )
            if len(items) >= limit:
                return items
    return items


def _json(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class Handler(BaseHTTPRequestHandler):
    server_version = "PandamoniumPcCursorBridge/1.0"

    def log_message(self, _fmt: str, *_args) -> None:
        return

    def do_GET(self) -> None:
        if not _authorized(self.headers.get("Authorization")):
            _json(self, 401, {"error": "unauthorized"})
            return
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            _json(
                self,
                200,
                {
                    "ok": True,
                    "protocol": "pandamonium.pc-cursor-bridge.v1",
                    "projects_root": str(PROJECTS_ROOT),
                    "uptime_seconds": int(time.time()),
                },
            )
            return
        if parsed.path == "/v1/ide/agents":
            query = parse_qs(parsed.query)
            limit = min(500, max(1, int((query.get("limit") or ["200"])[0])))
            _json(self, 200, {"items": _scan_ide_agents(limit=limit), "source": "ide"})
            return
        _json(self, 404, {"error": "not_found"})


def main() -> None:
    hosts = tuple(part.strip() for part in os.getenv("JARVIS_CURSOR_BRIDGE_HOSTS", HOST).split(",") if part.strip())
    if not hosts or any(host in {"0.0.0.0", "::"} for host in hosts):
        raise RuntimeError("bridge_hosts_must_be_explicit")
    server = ThreadingHTTPServer((hosts[0], PORT), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
