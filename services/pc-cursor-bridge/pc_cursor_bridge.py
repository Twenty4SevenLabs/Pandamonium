#!/usr/bin/env python3
"""Read-only Windows/Linux companion that mirrors Cursor IDE agent chats."""

from __future__ import annotations

import hmac
import json
import os
import secrets
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from transcript_io import discover_transcripts, index_transcripts, load_session, title_from_transcript  # noqa: E402

HOST = os.getenv("JARVIS_CURSOR_BRIDGE_HOST", "127.0.0.1")
PORT = int(os.getenv("JARVIS_CURSOR_BRIDGE_PORT", "8051"))
TOKEN_FILE = Path(
    os.getenv(
        "JARVIS_CURSOR_BRIDGE_TOKEN_FILE",
        str(Path.home() / ".config" / "jarvis" / "cursor-bridge-token"),
    )
)
PROJECTS_ROOT = Path(os.getenv("JARVIS_CURSOR_PROJECTS_ROOT", str(Path.home() / ".cursor" / "projects")))
STARTED_AT = time.time()
PROTOCOL = "pandamonium.pc-cursor-bridge.v1"


def ensure_token() -> str:
    token = _token()
    if token:
        return token
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    token = secrets.token_urlsafe(32)
    TOKEN_FILE.write_text(token + "\n", encoding="utf-8")
    try:
        TOKEN_FILE.chmod(0o600)
    except OSError:
        pass
    return token


def _token() -> str:
    try:
        return TOKEN_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def _authorized(header: str | None) -> bool:
    expected = _token()
    supplied = (header or "").removeprefix("Bearer ").strip()
    return bool(expected and supplied and hmac.compare_digest(expected, supplied))


def _scan_ide_agents(limit: int = 200) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    for row in discover_transcripts(PROJECTS_ROOT, limit=limit):
        messages = []
        try:
            from transcript_io import parse_transcript

            messages = parse_transcript(row.path, max_messages=3)
        except Exception:
            messages = []
        items.append(
            {
                "agent_id": row.agent_id,
                "title": title_from_transcript(row.path, messages),
                "workspace": row.workspace,
                "status": "idle",
                "source": "ide",
                "updated_at": row.updated_at,
                "read_only": True,
                "is_subagent": row.is_subagent,
                "message_count": len(messages),
            }
        )
    return items


def _json(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    body = json.dumps(payload, ensure_ascii=True).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class Handler(BaseHTTPRequestHandler):
    server_version = "PandamoniumPcCursorBridge/1.1"

    def log_message(self, _fmt: str, *_args) -> None:
        return

    def do_GET(self) -> None:
        if not _authorized(self.headers.get("Authorization")):
            _json(self, 401, {"error": "unauthorized"})
            return
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        query = parse_qs(parsed.query)

        if path == "/health":
            _json(
                self,
                200,
                {
                    "ok": True,
                    "protocol": PROTOCOL,
                    "projects_root": str(PROJECTS_ROOT),
                    "projects_root_exists": PROJECTS_ROOT.is_dir(),
                    "uptime_seconds": int(time.time() - STARTED_AT),
                },
            )
            return

        if path == "/v1/ide/agents":
            limit = min(500, max(1, int((query.get("limit") or ["200"])[0])))
            _json(self, 200, {"items": _scan_ide_agents(limit=limit), "source": "ide"})
            return

        if path.startswith("/v1/ide/agents/"):
            remainder = path.removeprefix("/v1/ide/agents/").strip("/")
            parts = [part for part in remainder.split("/") if part]
            if not parts:
                _json(self, 404, {"error": "agent_not_found"})
                return
            agent_id = parts[0]
            want_session = len(parts) >= 2 and parts[1] == "session"
            refs = index_transcripts(PROJECTS_ROOT, limit=500)
            ref = refs.get(agent_id)
            if not ref:
                _json(self, 404, {"error": "agent_not_found"})
                return
            if want_session:
                max_messages = min(1000, max(1, int((query.get("limit") or ["500"])[0])))
                session = load_session(
                    ref.path,
                    agent_id=ref.agent_id,
                    workspace=ref.workspace,
                    updated_at=ref.updated_at,
                    is_subagent=ref.is_subagent,
                )
                session["messages"] = session["messages"][:max_messages]
                session["message_count"] = len(session["messages"])
                _json(self, 200, session)
                return
            session = load_session(
                ref.path,
                agent_id=ref.agent_id,
                workspace=ref.workspace,
                updated_at=ref.updated_at,
                is_subagent=ref.is_subagent,
            )
            session.pop("messages", None)
            _json(self, 200, session)
            return

        _json(self, 404, {"error": "not_found"})


def main() -> None:
    ensure_token()
    allow_lan = os.getenv("JARVIS_CURSOR_BRIDGE_ALLOW_LAN", "").strip().lower() in {"1", "true", "yes", "on"}
    hosts = tuple(part.strip() for part in os.getenv("JARVIS_CURSOR_BRIDGE_HOSTS", HOST).split(",") if part.strip())
    if not hosts or (any(host in {"0.0.0.0", "::"} for host in hosts) and not allow_lan):
        raise RuntimeError("bridge_hosts_must_be_explicit")
    host = hosts[0]
    print(f"Pandamonium PC Cursor bridge listening on http://{host}:{PORT}", flush=True)
    print(f"Projects root: {PROJECTS_ROOT}", flush=True)
    print(f"Token file: {TOKEN_FILE}", flush=True)
    server = ThreadingHTTPServer((host, PORT), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
