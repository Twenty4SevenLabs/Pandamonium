"""Cursor bridge settings, token management, and process watchdog."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import secrets
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import httpx

from src.constants import DATA_DIR
from src.cursor_bridge_nodes import resolve_execution_node, sidecar_url_for_node
from src.secret_storage import decrypt, encrypt

logger = logging.getLogger(__name__)

BRIDGE_DIR = Path(DATA_DIR) / "cursor-bridge"
SETTINGS_FILE = BRIDGE_DIR / "settings.json"
TOKEN_FILE = BRIDGE_DIR / "token"
DEFAULT_URL = os.getenv("ODYSSEUS_CURSOR_BRIDGE_URL", "http://127.0.0.1:8050").rstrip("/")
PC_IDE_URL = (
    os.getenv("PANDAMONIUM_PC_CURSOR_BRIDGE_URL")
    or os.getenv("ODYSSEUS_PC_CURSOR_BRIDGE_URL")
    or ""
).rstrip("/")
PC_IDE_URLS_RAW = (
    os.getenv("PANDAMONIUM_PC_CURSOR_BRIDGE_URLS")
    or os.getenv("ODYSSEUS_PC_CURSOR_BRIDGE_URLS")
    or ""
)


def pc_ide_urls() -> list[str]:
    """Return all configured IDE mirror bridge base URLs (deduped, order preserved)."""
    urls: list[str] = []
    seen: set[str] = set()
    if PC_IDE_URLS_RAW.strip():
        for part in PC_IDE_URLS_RAW.split(","):
            url = part.strip().rstrip("/")
            if url and url not in seen:
                seen.add(url)
                urls.append(url)
    if PC_IDE_URL and PC_IDE_URL not in seen:
        urls.insert(0, PC_IDE_URL)
    return urls
PC_IDE_TOKEN_FILE = Path(
    os.getenv("PANDAMONIUM_PC_CURSOR_BRIDGE_TOKEN_FILE")
    or os.getenv("ODYSSEUS_PC_CURSOR_BRIDGE_TOKEN_FILE")
    or str(BRIDGE_DIR / "pc-ide-token")
)
BRIDGE_SCRIPT = Path(__file__).resolve().parents[1] / "services" / "cursor-bridge" / "cursor_bridge_service.py"
BRIDGE_PROCESS: subprocess.Popen[str] | None = None


def _port_holder_pid(port: int) -> int | None:
    try:
        output = subprocess.check_output(
            ["ss", "-ltnp", f"sport = :{port}"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    match = re.search(r"pid=(\d+)", output)
    return int(match.group(1)) if match else None


def _stop_pid(pid: int) -> None:
    try:
        os.kill(pid, 15)
    except OSError:
        return
    deadline = time.time() + 5
    while time.time() < deadline:
        try:
            os.kill(pid, 0)
        except OSError:
            return
        time.sleep(0.1)
    try:
        os.kill(pid, 9)
    except OSError:
        pass


def _load_settings() -> dict[str, Any]:
    try:
        payload = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _save_settings(payload: dict[str, Any]) -> None:
    BRIDGE_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
    SETTINGS_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    try:
        SETTINGS_FILE.chmod(0o600)
    except OSError:
        pass


def configured_api_key() -> str:
    payload = _load_settings()
    encrypted = str(payload.get("api_key_encrypted") or "")
    return decrypt(encrypted).strip()


def is_configured() -> bool:
    return bool(configured_api_key())


def bridge_token() -> str:
    if TOKEN_FILE.exists():
        token = TOKEN_FILE.read_text(encoding="utf-8").strip()
        if token:
            return token
    token = secrets.token_urlsafe(32)
    BRIDGE_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
    TOKEN_FILE.write_text(token + "\n", encoding="utf-8")
    try:
        TOKEN_FILE.chmod(0o600)
    except OSError:
        pass
    return token


def save_api_key(api_key: str) -> None:
    payload = _load_settings()
    payload["api_key_encrypted"] = encrypt(api_key.strip())
    payload["configured"] = True
    payload["updated_at"] = int(time.time())
    _save_settings(payload)


def clear_api_key() -> None:
    payload = _load_settings()
    payload.pop("api_key_encrypted", None)
    payload["configured"] = False
    payload["updated_at"] = int(time.time())
    _save_settings(payload)


def dismissed_agent_ids() -> set[str]:
    payload = _load_settings()
    raw = payload.get("dismissed_agent_ids")
    if not isinstance(raw, list):
        return set()
    return {str(row).strip() for row in raw if str(row).strip()}


def dismiss_agent(agent_id: str) -> None:
    agent_id = str(agent_id or "").strip()
    if not agent_id:
        return
    payload = _load_settings()
    dismissed = dismissed_agent_ids()
    dismissed.add(agent_id)
    payload["dismissed_agent_ids"] = sorted(dismissed)
    payload["updated_at"] = int(time.time())
    _save_settings(payload)


def _env_api_key_candidates() -> list[str]:
    names = (
        "ODYSSEUS_CURSOR_API_KEY",
        "PANDAMONIUM_CURSOR_API_KEY",
        "CURSOR_API_KEY",
    )
    values: list[str] = []
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            values.append(value)
    return values


def _looks_like_placeholder(value: str) -> bool:
    lowered = value.lower()
    markers = (
        "your_key_here",
        "replace_me",
        "replace_with",
        "changeme",
        "change_me",
        "placeholder",
        "xxx",
    )
    return any(marker in lowered for marker in markers)


def is_plausible_cursor_api_key(value: str) -> bool:
    token = str(value or "").strip()
    if len(token) < 20 or len(token) > 4096:
        return False
    if any(ord(char) < 32 for char in token):
        return False
    if _looks_like_placeholder(token):
        return False
    return token.startswith(("cursor_", "crsr_"))


def bootstrap_api_key_from_env() -> bool:
    """Seed encrypted settings from env when the UI has not connected yet."""
    if is_configured():
        return False
    for value in _env_api_key_candidates():
        if not is_plausible_cursor_api_key(value):
            continue
        save_api_key(value)
        logger.info("Cursor bridge API key loaded from environment")
        return True
    return False


def _default_cursor_workspaces_json() -> str:
    for env_name in ("PANDAMONIUM_CURSOR_WORKSPACES_JSON", "ODYSSEUS_CURSOR_WORKSPACES_JSON"):
        raw = os.getenv(env_name, "").strip()
        if raw:
            return raw
    candidates = (
        Path("/mnt/dev-env/projects/pandamonium"),
        Path(__file__).resolve().parents[1],
    )
    for path in candidates:
        if path.is_dir():
            return json.dumps({"pandamonium": str(path.resolve())})
    return json.dumps({"pandamonium": str(candidates[-1].resolve())})


def bridge_env() -> dict[str, str]:
    env = os.environ.copy()
    api_key = configured_api_key()
    if api_key:
        env["CURSOR_API_KEY"] = api_key
    env["ODYSSEUS_CURSOR_BRIDGE_TOKEN_FILE"] = str(TOKEN_FILE)
    env["ODYSSEUS_CURSOR_BRIDGE_STATE_DIR"] = str(BRIDGE_DIR)
    env.setdefault("ODYSSEUS_CURSOR_BRIDGE_HOST", "127.0.0.1")
    env.setdefault("ODYSSEUS_CURSOR_BRIDGE_PORT", "8050")
    bridge_home = (
        os.getenv("PANDAMONIUM_CURSOR_BRIDGE_HOME")
        or os.getenv("ODYSSEUS_CURSOR_BRIDGE_HOME")
        or ""
    ).strip()
    if bridge_home:
        env["PANDAMONIUM_CURSOR_BRIDGE_HOME"] = bridge_home
        env["HOME"] = bridge_home
    env.setdefault("PANDAMONIUM_CURSOR_SETTING_SOURCES", "project,user,plugins")
    workspaces_json = _default_cursor_workspaces_json()
    env["ODYSSEUS_CURSOR_WORKSPACES_JSON"] = workspaces_json
    env["PANDAMONIUM_CURSOR_WORKSPACES_JSON"] = workspaces_json
    return env


def _bridge_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {bridge_token()}", "Accept": "application/json"}


async def bridge_request(
    method: str,
    path: str,
    *,
    json_body: dict[str, Any] | None = None,
    timeout: float = 20,
    stream: bool = False,
    node: str | None = None,
) -> httpx.Response:
    base_url = sidecar_url_for_node(node) if node else DEFAULT_URL
    url = f"{base_url}{path}"
    async with httpx.AsyncClient(timeout=timeout) as client:
        if stream:
            return await client.build_request(method, url, headers=_bridge_headers(), json=json_body)
        response = await client.request(method, url, headers=_bridge_headers(), json=json_body)
    return response


async def bridge_request_for_agent(
    method: str,
    path: str,
    agent_meta: dict[str, Any],
    *,
    json_body: dict[str, Any] | None = None,
    timeout: float = 20,
    stream: bool = False,
) -> httpx.Response:
    node = resolve_execution_node(agent_meta)
    return await bridge_request(
        method,
        path,
        json_body=json_body,
        timeout=timeout,
        stream=stream,
        node=node,
    )


def _pc_ide_headers() -> dict[str, str]:
    try:
        token = PC_IDE_TOKEN_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        token = ""
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}", "Accept": "application/json"}


async def _fetch_ide_agents_from_url(
    client: httpx.AsyncClient,
    base_url: str,
    headers: dict[str, str],
) -> list[dict[str, Any]]:
    response = await client.get(f"{base_url}/v1/ide/agents", headers=headers)
    response.raise_for_status()
    payload = response.json()
    items = payload.get("items") if isinstance(payload, dict) else []
    rows: list[dict[str, Any]] = []
    for row in items:
        if not isinstance(row, dict):
            continue
        enriched = dict(row)
        enriched.setdefault("mirror_url", base_url)
        rows.append(enriched)
    return rows


async def list_ide_mirror_agents() -> list[dict[str, Any]]:
    urls = pc_ide_urls()
    if not urls:
        return []
    headers = _pc_ide_headers()
    if not headers:
        return []
    merged: dict[str, dict[str, Any]] = {}
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            for base_url in urls:
                try:
                    rows = await _fetch_ide_agents_from_url(client, base_url, headers)
                except Exception as exc:
                    logger.debug("IDE mirror unavailable at %s: %s", base_url, exc)
                    continue
                for row in rows:
                    agent_id = str(row.get("agent_id") or "")
                    if not agent_id:
                        continue
                    prev = merged.get(agent_id)
                    if prev is None or float(row.get("updated_at") or 0) >= float(prev.get("updated_at") or 0):
                        merged[agent_id] = row
    except Exception as exc:
        logger.debug("IDE mirror list failed: %s", exc)
    items = list(merged.values())
    items.sort(key=lambda row: float(row.get("updated_at") or 0), reverse=True)
    return items


async def ide_mirror_health() -> dict[str, Any]:
    urls = pc_ide_urls()
    if not urls:
        return {"configured": False, "connected": False, "hosts": []}
    headers = _pc_ide_headers()
    if not headers:
        return {"configured": True, "connected": False, "error": "pc_ide_token_missing", "hosts": []}
    hosts: list[dict[str, Any]] = []
    any_connected = False
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            for base_url in urls:
                host_status: dict[str, Any] = {"url": base_url, "connected": False}
                try:
                    response = await client.get(f"{base_url}/health", headers=headers)
                    response.raise_for_status()
                    payload = response.json()
                    if isinstance(payload, dict):
                        host_status.update(payload)
                    host_status["connected"] = bool(host_status.get("ok"))
                    any_connected = any_connected or host_status["connected"]
                except Exception as exc:
                    host_status["error"] = str(exc)[:120]
                hosts.append(host_status)
    except Exception as exc:
        return {
            "configured": True,
            "connected": False,
            "error": str(exc)[:120],
            "hosts": hosts,
        }
    return {
        "configured": True,
        "connected": any_connected,
        "hosts": hosts,
        "url_count": len(urls),
    }


async def fetch_ide_agent_session(agent_id: str) -> dict[str, Any] | None:
    urls = pc_ide_urls()
    if not urls:
        return None
    headers = _pc_ide_headers()
    if not headers:
        return None
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            for base_url in urls:
                try:
                    response = await client.get(
                        f"{base_url}/v1/ide/agents/{agent_id}/session",
                        headers=headers,
                    )
                except Exception as exc:
                    logger.debug("IDE session fetch failed for %s at %s: %s", agent_id, base_url, exc)
                    continue
                if response.status_code == 404:
                    continue
                response.raise_for_status()
                payload = response.json()
                if isinstance(payload, dict):
                    payload.setdefault("mirror_url", base_url)
                    return payload
    except Exception as exc:
        logger.debug("IDE session fetch failed for %s: %s", agent_id, exc)
    return None


async def bridge_health() -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{DEFAULT_URL}/health")
        response.raise_for_status()
        payload = response.json()
        payload["configured"] = is_configured()
        return payload
    except Exception as exc:
        return {"ok": False, "configured": is_configured(), "error": str(exc)[:120]}


async def bridge_status() -> dict[str, Any]:
    if not is_configured():
        return {"configured": False, "connected": False, "status": "disconnected"}
    try:
        response = await bridge_request("GET", "/status")
        response.raise_for_status()
        payload = response.json()
        payload["configured"] = True
        payload["status"] = "connected" if payload.get("connected") else "reconnect_needed"
        ide = await ide_mirror_health()
        payload["ide_mirror"] = ide
        return payload
    except Exception as exc:
        return {
            "configured": True,
            "connected": False,
            "status": "reconnect_needed",
            "error": str(exc)[:120],
        }


def stop_bridge_process() -> None:
    global BRIDGE_PROCESS
    proc = BRIDGE_PROCESS
    BRIDGE_PROCESS = None
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def ensure_bridge_process() -> None:
    global BRIDGE_PROCESS
    if not is_configured():
        return
    if BRIDGE_PROCESS and BRIDGE_PROCESS.poll() is None:
        return
    port = int(os.getenv("ODYSSEUS_CURSOR_BRIDGE_PORT", "8050"))
    holder = _port_holder_pid(port)
    if holder and (BRIDGE_PROCESS is None or BRIDGE_PROCESS.poll() is not None or BRIDGE_PROCESS.pid != holder):
        _stop_pid(holder)
        time.sleep(0.3)
    python = sys.executable
    env = bridge_env()
    BRIDGE_PROCESS = subprocess.Popen(
        [python, str(BRIDGE_SCRIPT)],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    logger.info("Started Cursor bridge process pid=%s", BRIDGE_PROCESS.pid)


async def ensure_bridge_online() -> dict[str, Any]:
    ensure_bridge_process()
    for delay in (0.2, 0.5, 1.0, 2.0):
        health = await bridge_health()
        if health.get("ok"):
            return health
        await asyncio.sleep(delay)
    return await bridge_health()
