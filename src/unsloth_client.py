"""Unsloth Studio integration for Pandamonium.

Unsloth exposes an OpenAI-compatible API at ``/v1`` but only lists *loaded*
models there. The Studio catalog (downloaded GGUF repos, local folders, and
hub defaults) lives under ``/api/models/*``. This module discovers those models
for the picker and calls ``POST /api/inference/load`` before chat when the
requested model is not already active.

Docker cannot use Tailscale MagicDNS. M1 traffic is rewritten to the pve-heavy
wake proxy. M2 / Mac / laptop hosts stay on their LAN or Tailscale IPs.
"""

from __future__ import annotations

import logging
import os
import re
import time
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse, urlunparse

import httpx

logger = logging.getLogger(__name__)

_GGUF_QUANT_RE = re.compile(r"^UD-[A-Z0-9_]+$|^[IQ][0-9]+_[A-Z0-9_]+$|^[A-Z0-9_]+$")

DEFAULT_UNSLOTH_PROXY = "http://192.168.1.2:8888"
DEFAULT_UNSLOTH_WAKE_URL = "http://192.168.1.2:8910/wake"
DEFAULT_M2_PROXY = "http://192.168.1.191:8888"
_UNSLOTH_PORTS = frozenset({8888, 8889, 18888, 18889, 18890})
_M1_HOSTS = frozenset({
    "192.168.1.181",
    "192.168.1.2",
    "100.100.247.127",
    "m1.tail61d527.ts.net",
    "m1",
})
_M2_HOSTS = frozenset({
    "192.168.1.191",
    "192.168.1.90",
    "100.123.238.35",
    "m2.tail61d527.ts.net",
    "m2",
    "agents.tail61d527.ts.net",
    "agents",
})
_A1_HOSTS = frozenset({
    "100.80.146.51",
    "a1.tailfa464b.ts.net",
    "a1",
})
_IMAC_HOSTS = frozenset({
    "100.85.221.36",
    "lunas-imac.tailfa464b.ts.net",
})
_MINI_HOSTS = frozenset({
    "100.87.228.16",
    "toms-mac-mini.tailfa464b.ts.net",
})
_LAPTOP_HOSTS = frozenset({
    "192.168.1.98",
    "100.112.1.19",
    "247laptop.tail61d527.ts.net",
    "247laptop",
})


class UnslothUnreachableError(RuntimeError):
    """M1 Unsloth Studio is offline (idle-stopped) or the wake proxy failed."""


def normalize_openai_base(base_url: str) -> str:
    """Normalize an OpenAI-compatible URL down to the ``/v1`` base.

    Chat sessions store ``.../v1/chat/completions``. Studio probes use
    ``.../v1``. Both must collapse to the same origin+/v1 so Unsloth load
    and model listing hit the right host.
    """
    base = (base_url or "").strip().rstrip("/")
    lowered = base.lower()
    for suffix in ("/chat/completions", "/completions", "/models"):
        if lowered.endswith(suffix):
            base = base[: -len(suffix)].rstrip("/")
            lowered = base.lower()
            break
    return base


def studio_api_root(openai_base: str) -> str:
    """``http://host:8888/v1`` or ``.../v1/chat/completions`` → ``http://host:8888``."""
    base = normalize_openai_base(openai_base)
    if base.lower().endswith("/v1"):
        return base[:-3].rstrip("/") or base
    return base


def configured_unsloth_base() -> str:
    return normalize_openai_base(os.getenv("UNSLOTH_BASE_URL", ""))


def _rewrite_target(host: str) -> Optional[str]:
    """LAN/proxy origin for a MagicDNS or idle-stop hostname. None = leave URL."""
    host = (host or "").lower().rstrip(".")
    if host in _M1_HOSTS and host not in {"192.168.1.2"}:
        return (os.getenv("UNSLOTH_LAN_PROXY") or DEFAULT_UNSLOTH_PROXY).rstrip("/")
    if host in {
        "m2.tail61d527.ts.net",
        "m2",
        "100.123.238.35",
        "agents.tail61d527.ts.net",
        "agents",
        "192.168.1.90",
    }:
        return (os.getenv("UNSLOTH_M2_BASE_URL") or DEFAULT_M2_PROXY).rstrip("/").removesuffix("/v1")
    if host in {"247laptop.tail61d527.ts.net", "247laptop"}:
        return (os.getenv("UNSLOTH_LAPTOP_BASE_URL") or "http://192.168.1.98:8888").rstrip("/").removesuffix("/v1")
    return None


def rewrite_unsloth_url(url: str) -> str:
    """Rewrite MagicDNS / idle-stop Unsloth URLs to Docker-reachable LAN origins."""
    raw = (url or "").strip()
    if not raw:
        return raw
    parsed = urlparse(raw if "://" in raw else f"http://{raw}")
    target = _rewrite_target(parsed.hostname or "")
    if not target:
        return raw
    proxy_parsed = urlparse(target if "://" in target else f"http://{target}")
    return urlunparse((
        proxy_parsed.scheme or "http",
        proxy_parsed.netloc,
        parsed.path or "",
        parsed.params,
        parsed.query,
        parsed.fragment,
    ))


def _is_connect_failure(exc: BaseException) -> bool:
    if isinstance(
        exc,
        (
            httpx.ConnectError,
            httpx.ConnectTimeout,
            httpx.ReadError,
            httpx.WriteError,
            httpx.RemoteProtocolError,
        ),
    ):
        return True
    if isinstance(exc, httpx.HTTPStatusError) and exc.response is not None:
        return exc.response.status_code in (502, 503, 504)
    msg = str(exc).lower()
    return any(
        needle in msg
        for needle in (
            "no route to host",
            "connection refused",
            "connection reset",
            "connecterror",
            "network is unreachable",
            "name or service not known",
            "peer closed",
            "all connection attempts failed",
        )
    )


def _wake_unsloth_backend() -> bool:
    url = (
        os.getenv("PANDAMONIUM_UNSLOTH_WAKE_URL")
        or os.getenv("ODYSSEUS_UNSLOTH_WAKE_URL")
        or DEFAULT_UNSLOTH_WAKE_URL
    ).strip()
    if not url:
        return False
    timeout = float(
        os.getenv("PANDAMONIUM_UNSLOTH_WAKE_TIMEOUT")
        or os.getenv("ODYSSEUS_UNSLOTH_WAKE_TIMEOUT", "210")
    )
    try:
        response = httpx.get(url, timeout=timeout)
        response.raise_for_status()
        logger.info("Unsloth backend wake ok: %s", url)
        return True
    except Exception as exc:  # noqa: BLE001 — wake is best-effort before retry
        logger.warning("Unsloth backend wake failed (%s): %s", url, exc)
        return False


def _host_api_key_env(host: str) -> List[str]:
    host = (host or "").lower().rstrip(".")
    if host in _M1_HOSTS:
        return ["UNSLOTH_M1_API_KEY", "UNSLOTH_API_KEY"]
    if host in _M2_HOSTS:
        return ["UNSLOTH_M2_API_KEY", "UNSLOTH_API_KEY"]
    if host in _A1_HOSTS:
        return ["UNSLOTH_A1_API_KEY", "UNSLOTH_MBP_API_KEY", "UNSLOTH_API_KEY"]
    if host in _IMAC_HOSTS:
        return ["UNSLOTH_IMAC_API_KEY", "UNSLOTH_API_KEY"]
    if host in _MINI_HOSTS:
        return ["UNSLOTH_MINI_API_KEY", "UNSLOTH_API_KEY"]
    if host in _LAPTOP_HOSTS:
        return ["UNSLOTH_LAPTOP_API_KEY", "UNSLOTH_API_KEY"]
    return ["UNSLOTH_API_KEY"]


def resolve_unsloth_api_key(
    endpoint_api_key: Optional[str] = None,
    openai_base: Optional[str] = None,
) -> str:
    if (endpoint_api_key or "").strip():
        return endpoint_api_key.strip()
    host = ""
    if openai_base:
        parsed = urlparse(
            normalize_openai_base(openai_base)
            if "://" in (openai_base or "")
            else f"http://{openai_base}"
        )
        host = (parsed.hostname or "").lower()
    for env_name in _host_api_key_env(host):
        value = (os.getenv(env_name) or "").strip()
        if value:
            return value
    return ""


def _configured_unsloth_bases() -> List[str]:
    urls = [os.getenv("UNSLOTH_BASE_URL", "")]
    urls.extend(os.getenv("UNSLOTH_EXTRA_BASE_URLS", "").split(","))
    for env_name in (
        "UNSLOTH_M1_BASE_URL",
        "UNSLOTH_M2_BASE_URL",
        "UNSLOTH_A1_BASE_URL",
        "UNSLOTH_IMAC_BASE_URL",
        "UNSLOTH_MINI_BASE_URL",
        "UNSLOTH_LAPTOP_BASE_URL",
    ):
        urls.append(os.getenv(env_name, ""))
    out = []
    for raw in urls:
        norm = normalize_openai_base(raw).lower()
        if not norm or norm in out:
            continue
        try:
            port = urlparse(norm).port
        except Exception:
            port = None
        if port == 1234:
            continue
        out.append(norm)
    return out


def _unsloth_label_for_host(host: str) -> str:
    host = (host or "").lower().rstrip(".")
    if host in _M1_HOSTS:
        return "Unsloth Studio (M1)"
    if host in _M2_HOSTS:
        return "Unsloth Studio (M2)"
    if host in _A1_HOSTS:
        return "Unsloth Studio (A1)"
    if host in _IMAC_HOSTS:
        return "Unsloth Studio (iMac)"
    if host in _MINI_HOSTS:
        return "Unsloth Studio (Mac mini)"
    if host in _LAPTOP_HOSTS:
        return "Unsloth Studio (247Laptop)"
    return f"Unsloth Studio ({host or 'node'})"


def unsloth_endpoint_id(base_url: str) -> str:
    parsed = urlparse(normalize_openai_base(base_url))
    host = (parsed.hostname or "host").replace(".", "-")
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    return f"unsloth-{host}-{port}"[:64]


def unsloth_studio_targets() -> List[Dict[str, str]]:
    """Docker-reachable Unsloth Studio /v1 URLs to register as Added Models."""
    seen: List[str] = []
    targets: List[Dict[str, str]] = []

    def _add(raw: str) -> None:
        rewritten = rewrite_unsloth_url(raw.strip())
        norm = normalize_openai_base(rewritten)
        if not norm:
            return
        parsed = urlparse(norm if "://" in norm else f"http://{norm}")
        port = parsed.port
        if port == 1234:
            return
        if port is not None and port not in _UNSLOTH_PORTS:
            return
        key = norm.lower()
        if key in seen:
            return
        seen.append(key)
        host = (parsed.hostname or "").lower()
        targets.append(
            {
                "id": unsloth_endpoint_id(norm),
                "name": _unsloth_label_for_host(host),
                "base_url": norm,
            }
        )

    for base in _configured_unsloth_bases():
        _add(base)
    known = (
        _M1_HOSTS | _M2_HOSTS | _A1_HOSTS | _IMAC_HOSTS | _MINI_HOSTS | _LAPTOP_HOSTS
    )
    for host in os.getenv("LLM_HOSTS", "").split(","):
        host = host.strip()
        if host and host.lower() in known:
            _add(f"http://{host}:8888/v1")
    return targets


def is_unsloth_endpoint(base_url: str) -> bool:
    """True when ``base_url`` targets Unsloth Studio's OpenAI-compatible API."""
    norm = normalize_openai_base(base_url).lower()
    if not norm:
        return False
    if norm in _configured_unsloth_bases() or any(
        norm.rstrip("/") == cfg or norm.startswith(cfg.rstrip("/") + "/")
        for cfg in _configured_unsloth_bases()
    ):
        return True
    try:
        parsed = urlparse(norm if "://" in norm else f"http://{norm}")
        path = (parsed.path or "").rstrip("/")
        host = (parsed.hostname or "").lower().rstrip(".")
        if path.endswith("/v1") and (
            parsed.port in _UNSLOTH_PORTS
            or host in _M1_HOSTS
            or host in _M2_HOSTS
            or host in _A1_HOSTS
            or host in _IMAC_HOSTS
            or host in _MINI_HOSTS
            or host in _LAPTOP_HOSTS
            or host.endswith(".tail61d527.ts.net")
        ):
            return True
    except Exception:
        pass
    return False


def _auth_headers(api_key: str) -> Dict[str, str]:
    if not api_key:
        return {}
    return {"Authorization": f"Bearer {api_key}"}


def _get_json(
    url: str,
    api_key: str,
    *,
    timeout: float,
    params: Optional[Dict[str, Any]] = None,
) -> Any:
    with httpx.Client(timeout=timeout) as client:
        resp = client.get(url, headers=_auth_headers(api_key), params=params)
        resp.raise_for_status()
        return resp.json()


def _post_json(
    url: str,
    api_key: str,
    payload: Dict[str, Any],
    *,
    timeout: float,
) -> Any:
    headers = {"Content-Type": "application/json", **_auth_headers(api_key)}
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()


def parse_unsloth_model_id(model_id: str) -> Tuple[str, Optional[str]]:
    """Split ``repo:QUANT`` into load API fields.

    Only the last ``:`` segment is treated as a GGUF quant when it looks like
    one (``UD-Q4_K_XL``, ``Q4_K_M``, etc.).
    """
    model_id = (model_id or "").strip()
    if ":" not in model_id:
        return model_id, None
    repo, tail = model_id.rsplit(":", 1)
    if repo and tail and _GGUF_QUANT_RE.match(tail.upper()):
        return repo, tail
    return model_id, None


def _extract_ids(payload: Any, *keys: str) -> List[str]:
    out: List[str] = []
    if not isinstance(payload, dict):
        return out
    for key in keys:
        items = payload.get(key)
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, str) and item:
                out.append(item)
            elif isinstance(item, dict):
                mid = item.get("id") or item.get("repo_id")
                if isinstance(mid, str) and mid:
                    out.append(mid)
    return out


def _is_downloaded_record(item: Any) -> bool:
    """True when a Studio model record represents a complete local download."""
    if not isinstance(item, dict):
        return True
    if item.get("partial") is True:
        return False
    if item.get("active_cache") is False:
        return False
    return True


def _looks_like_filesystem_path(model_id: str) -> bool:
    n = (model_id or "").strip().replace("\\", "/")
    if not n:
        return False
    if n.startswith("/"):
        return True
    if len(n) >= 3 and n[1] == ":" and n[2] == "/":
        return True
    return n.startswith("//")


def _local_fs_path(item: Dict[str, Any]) -> Optional[str]:
    if not isinstance(item, dict):
        return None
    for key in ("path", "id"):
        val = item.get(key)
        if isinstance(val, str) and _looks_like_filesystem_path(val):
            return val.strip()
    return None


def _picker_id_from_local_record(item: Any) -> Optional[str]:
    """Hub-style or display id for the model picker — never a raw folder path."""
    if isinstance(item, str) and item.strip():
        raw = item.strip()
        if _looks_like_filesystem_path(raw):
            return raw.rsplit("/", 1)[-1] or raw
        return raw
    if not isinstance(item, dict):
        return None
    mid = item.get("id") or item.get("model_id") or item.get("repo_id")
    hub = item.get("model_id") or item.get("repo_id")
    display = item.get("display_name")
    if isinstance(mid, str) and _looks_like_filesystem_path(mid):
        if isinstance(hub, str) and hub.strip() and not _looks_like_filesystem_path(hub):
            return hub.strip()
        if isinstance(display, str) and display.strip():
            return display.strip()
        return mid.replace("\\", "/").rsplit("/", 1)[-1] or mid
    if isinstance(mid, str) and mid.strip():
        return mid.strip()
    return None


def _extract_downloaded_local_ids(payload: Any) -> List[str]:
    """IDs from ``/api/models/local`` that are fully present on disk."""
    if not isinstance(payload, dict):
        return []
    items = payload.get("models")
    if not isinstance(items, list):
        return []
    out: List[str] = []
    for item in items:
        if not _is_downloaded_record(item):
            continue
        picker = _picker_id_from_local_record(item)
        if picker and picker not in out:
            out.append(picker)
    return out


def _extract_downloaded_cached_repo_ids(payload: Any, *, key: str) -> List[str]:
    """Repo IDs from cached-model listings, skipping partial downloads."""
    if not isinstance(payload, dict):
        return []
    items = payload.get(key)
    if not isinstance(items, list):
        return []
    out: List[str] = []
    for item in items:
        if isinstance(item, str) and item:
            out.append(item)
            continue
        if not isinstance(item, dict) or not _is_downloaded_record(item):
            continue
        repo_id = item.get("repo_id") or item.get("id")
        if isinstance(repo_id, str) and repo_id:
            out.append(repo_id)
    return out


def _expand_downloaded_gguf_variants(
    root: str,
    api_key: str,
    repo_ids: List[str],
    *,
    timeout: float,
    max_repos: int = 40,
) -> List[str]:
    expanded: List[str] = []
    for repo_id in repo_ids[:max_repos]:
        if not repo_id.upper().endswith("-GGUF"):
            expanded.append(repo_id)
            continue
        try:
            data = _get_json(
                f"{root}/api/models/gguf-variants",
                api_key,
                timeout=timeout,
                params={"repo_id": repo_id},
            )
        except Exception as exc:
            logger.debug("Unsloth gguf-variants failed for %s: %s", repo_id, exc)
            expanded.append(repo_id)
            continue
        variants = data.get("variants") if isinstance(data, dict) else None
        default_variant = data.get("default_variant") if isinstance(data, dict) else None
        downloaded: List[str] = []
        if isinstance(variants, list):
            for variant in variants:
                if not isinstance(variant, dict):
                    continue
                if not variant.get("downloaded", True):
                    continue
                quant = variant.get("quant") or variant.get("filename")
                if isinstance(quant, str) and quant:
                    downloaded.append(quant)
        if downloaded:
            for quant in downloaded:
                expanded.append(f"{repo_id}:{quant}")
        elif isinstance(default_variant, str) and default_variant:
            expanded.append(f"{repo_id}:{default_variant}")
        else:
            expanded.append(repo_id)
    return expanded


def list_studio_model_ids(
    openai_base: str,
    api_key: Optional[str] = None,
    *,
    timeout: Optional[float] = None,
) -> List[str]:
    """Return Studio model IDs that are downloaded and loadable via ``/v1``."""
    openai_base = rewrite_unsloth_url(openai_base)
    key = resolve_unsloth_api_key(api_key, openai_base)
    budget = float(timeout or os.getenv("UNSLOTH_DISCOVERY_TIMEOUT_SEC", "15"))

    loadable: List[str] = []
    try:
        data = _get_json(f"{normalize_openai_base(openai_base)}/models", key, timeout=budget)
        loadable = _extract_ids(data, "data")
    except Exception as exc:
        logger.debug("Unsloth /v1/models fetch failed: %s", exc)

    if loadable:
        loaded = list(loadable)
    else:
        loaded = []

    catalog: List[str] = []
    try:
        root = studio_api_root(openai_base)
        data = _get_json(f"{root}/api/models/local", key, timeout=budget)
        local_ids = _extract_downloaded_local_ids(data)
        if local_ids:
            catalog = _expand_downloaded_gguf_variants(
                root, key, local_ids, timeout=budget
            )
    except Exception as exc:
        logger.debug("Unsloth local catalog failed: %s", exc)

    merged: List[str] = []
    for mid in catalog + loaded:
        if not mid or mid in merged:
            continue
        if mid.startswith("/") or ":\\" in mid or mid.startswith("\\"):
            continue
        merged.append(mid)
    if merged:
        return merged

    # Fallback when /v1/models is temporarily unavailable: only fully downloaded
    # local folders that look like chat GGUF repos (skip raw diffusers trees).
    try:
        root = studio_api_root(openai_base)
        data = _get_json(f"{root}/api/models/local", key, timeout=budget)
        local_ids = _extract_downloaded_local_ids(data)
        return [
            mid for mid in local_ids
            if mid.lower().endswith("-gguf")
        ]
    except Exception as exc:
        logger.debug("Unsloth local model fallback failed: %s", exc)
        return []


def get_inference_status(openai_base: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    key = resolve_unsloth_api_key(api_key, openai_base)
    root = studio_api_root(rewrite_unsloth_url(openai_base))
    data = _get_json(f"{root}/api/inference/status", key, timeout=10.0)
    return data if isinstance(data, dict) else {}


def _normalize_model_ref(model_id: str) -> str:
    return (model_id or "").strip().replace("\\", "/").rstrip("/").lower()


def _model_repo_ref(model_id: str) -> str:
    """Repo/folder identity with GGUF quant stripped and paths normalized."""
    repo, _quant = parse_unsloth_model_id(_normalize_model_ref(model_id))
    return repo.replace("\\", "/").rstrip("/")


def _active_model_matches(status: Dict[str, Any], model_id: str) -> bool:
    """True when Studio's active_model is the same GGUF/MLX the picker requested.

    Unsloth status often reports an LM Studio folder
    (``/Users/…/lmstudio-community/Qwen3.8-27B-MLX-4bit``) while ``/v1/models``
    lists the short id ``Qwen3.8-27B-MLX-4bit``. Treat path suffixes and final
    path segments as the same model so we do not POST ``/api/inference/load``
    (which Studio then resolves as a missing Hugging Face ``unsloth/…`` repo).
    """
    active = (status.get("active_model") or "").strip()
    requested = (model_id or "").strip()
    if not active or not requested:
        return False
    if _normalize_model_ref(active) == _normalize_model_ref(requested):
        return True
    _, req_quant = parse_unsloth_model_id(requested)
    _, act_quant = parse_unsloth_model_id(active)
    if req_quant and act_quant and req_quant.lower() != act_quant.lower():
        return False
    act_repo = _model_repo_ref(active)
    req_repo = _model_repo_ref(requested)
    if not act_repo or not req_repo:
        return False
    if act_repo == req_repo:
        return True
    if act_repo.endswith("/" + req_repo) or req_repo.endswith("/" + act_repo):
        return True
    return act_repo.rsplit("/", 1)[-1] == req_repo.rsplit("/", 1)[-1]


def _wait_for_active_model(
    openai_base: str,
    model_id: str,
    api_key: Optional[str] = None,
    *,
    timeout: Optional[float] = None,
) -> bool:
    """Poll Studio until ``model_id`` is the active inference model."""
    budget = float(timeout or os.getenv("UNSLOTH_LOAD_TIMEOUT_SEC", "900"))
    deadline = time.monotonic() + budget
    first = time.monotonic()
    while time.monotonic() < deadline:
        status = get_inference_status(openai_base, api_key)
        if _active_model_matches(status, model_id):
            return True
        loading = status.get("loading") or []
        loading_requested = isinstance(loading, list) and any(
            isinstance(x, str) and _active_model_matches({"active_model": x}, model_id)
            for x in loading
        )
        if loading_requested:
            time.sleep(0.5)
            continue
        # Load POSTs can return before status flips. Keep polling briefly
        # while the previous GGUF is still listed as active.
        if (
            (status.get("active_model") or "").strip()
            and not loading_requested
            and (time.monotonic() - first) >= 10
        ):
            return False
        time.sleep(0.5)
    return _active_model_matches(get_inference_status(openai_base, api_key), model_id)


def _record_aliases(item: Dict[str, Any]) -> List[str]:
    out: List[str] = []
    for key in ("id", "path", "model_id", "repo_id", "display_name"):
        val = item.get(key)
        if isinstance(val, str) and val.strip() and val.strip() not in out:
            out.append(val.strip())
    return out


def _prefer_lmstudio_filesystem(item: Dict[str, Any], requested: str) -> bool:
    """True when POST /api/inference/load must use a local folder, not a hub id.

    Short /v1 ids and LM Studio records must not be sent as Hugging Face
    ``unsloth/<leaf>`` — that repo often does not exist (401/500).
    Hub GGUF ids (``unsloth/foo-GGUF:QUANT``) stay hub ids.
    """
    fs = _local_fs_path(item)
    if not fs:
        return False
    source = str(item.get("source") or "").lower()
    if source == "lmstudio":
        return True
    if "/.lmstudio/" in fs.replace("\\", "/").lower():
        return True
    req = (requested or "").strip().replace("\\", "/")
    return "/" not in req and ":" not in req


def _resolve_load_id_from_catalog(payload: Any, model_id: str) -> Optional[str]:
    """Return a local filesystem path when the catalog has a matching LM Studio folder."""
    requested = (model_id or "").strip()
    if not requested:
        return None
    if _looks_like_filesystem_path(requested):
        return requested
    req_repo, _req_quant = parse_unsloth_model_id(requested)
    items = payload.get("models") if isinstance(payload, dict) else None
    if not isinstance(items, list):
        return None
    for item in items:
        if not isinstance(item, dict) or not _is_downloaded_record(item):
            continue
        aliases = _record_aliases(item)
        if not aliases:
            continue
        matched = requested in aliases or req_repo in aliases
        if not matched:
            matched = any(
                _active_model_matches({"active_model": alias}, requested)
                for alias in aliases
            )
        if not matched:
            continue
        if _prefer_lmstudio_filesystem(item, requested):
            fs = _local_fs_path(item)
            if fs:
                return fs
    return None


def resolve_studio_load_id(
    openai_base: str,
    model_id: str,
    api_key: Optional[str] = None,
) -> str:
    """Map a picker / session id to the Studio load path when a local folder exists."""
    requested = (model_id or "").strip()
    if not requested or _looks_like_filesystem_path(requested):
        return requested
    try:
        key = resolve_unsloth_api_key(api_key, openai_base)
        root = studio_api_root(rewrite_unsloth_url(openai_base))
        budget = float(os.getenv("UNSLOTH_DISCOVERY_TIMEOUT_SEC", "15"))
        data = _get_json(f"{root}/api/models/local", key, timeout=budget)
    except Exception as exc:
        logger.debug("Unsloth local catalog for load resolve failed: %s", exc)
        return requested
    resolved = _resolve_load_id_from_catalog(data, requested)
    if resolved and resolved != requested:
        logger.info("Unsloth load id %s resolved to local path %s", requested, resolved)
        return resolved
    return requested


def load_model(
    openai_base: str,
    model_id: str,
    api_key: Optional[str] = None,
    *,
    timeout: Optional[float] = None,
) -> Dict[str, Any]:
    key = resolve_unsloth_api_key(api_key, openai_base)
    root = studio_api_root(rewrite_unsloth_url(openai_base))
    resolved = resolve_studio_load_id(openai_base, model_id, api_key)
    model_path, gguf_variant = parse_unsloth_model_id(resolved)
    payload: Dict[str, Any] = {"model_path": model_path}
    if gguf_variant:
        payload["gguf_variant"] = gguf_variant
    load_timeout = float(timeout or os.getenv("UNSLOTH_LOAD_TIMEOUT_SEC", "900"))
    data = _post_json(f"{root}/api/inference/load", key, payload, timeout=load_timeout)
    return data if isinstance(data, dict) else {}


def _ensure_model_loaded_inner(
    openai_base: str,
    model_id: str,
    api_key: Optional[str] = None,
) -> bool:
    status = get_inference_status(openai_base, api_key)
    if _active_model_matches(status, model_id):
        return True
    loading = status.get("loading") or []
    if isinstance(loading, list) and any(
        isinstance(x, str) and _active_model_matches({"active_model": x}, model_id)
        for x in loading
    ):
        logger.info("Unsloth is already loading %s", model_id)
        return _wait_for_active_model(openai_base, model_id, api_key)
    logger.info("Loading Unsloth model %s via Studio API", model_id)
    load_model(openai_base, model_id, api_key)
    if not _wait_for_active_model(openai_base, model_id, api_key):
        status = get_inference_status(openai_base, api_key)
        active = (status.get("active_model") or "").strip()
        logger.warning(
            "Unsloth load finished but active model is %r, wanted %r",
            active or "(none)",
            model_id,
        )
        return False
    return True


def ensure_model_loaded(
    openai_base: str,
    model_id: str,
    api_key: Optional[str] = None,
) -> bool:
    """Load ``model_id`` on Unsloth Studio when it is not already active."""
    openai_base = rewrite_unsloth_url(openai_base)
    if not is_unsloth_endpoint(openai_base):
        return True
    if not model_id:
        return False
    mid = model_id.lower()
    if any(marker in mid for marker in (
        "flux", "stable-diffusion", "sdxl", "sd3", "dall-e", "gpt-image", "hidream",
        "chatterbox", "kokoro",
    )):
        logger.warning("Refusing to load non-chat model %s on Unsloth chat runtime", model_id)
        return False
    try:
        return _ensure_model_loaded_inner(openai_base, model_id, api_key)
    except UnslothUnreachableError:
        raise
    except httpx.HTTPStatusError as exc:
        if _is_connect_failure(exc):
            return _ensure_model_loaded_after_wake(openai_base, model_id, api_key, exc)
        detail = ""
        try:
            body = exc.response.json()
            if isinstance(body, dict):
                detail = str(body.get("detail") or body.get("error") or body)
        except Exception:
            detail = exc.response.text[:200] if exc.response is not None else str(exc)
        logger.warning("Unsloth load failed for %s: %s", model_id, detail)
        return False
    except Exception as exc:
        if _is_connect_failure(exc):
            return _ensure_model_loaded_after_wake(openai_base, model_id, api_key, exc)
        logger.warning("Unsloth load failed for %s: %s", model_id, exc)
        return False


def _ensure_model_loaded_after_wake(
    openai_base: str,
    model_id: str,
    api_key: Optional[str],
    cause: BaseException,
) -> bool:
    logger.warning("Unsloth unreachable (%s); waking M1 GPU VM", cause)
    if not _wake_unsloth_backend():
        raise UnslothUnreachableError(
            "Unsloth Studio (M1) is offline and the GPU wake API did not respond."
        ) from cause
    try:
        return _ensure_model_loaded_inner(openai_base, model_id, api_key)
    except Exception as retry_exc:
        raise UnslothUnreachableError(
            f"Unsloth Studio (M1) did not become ready after wake: {retry_exc}"
        ) from retry_exc


def unsloth_host_from_env() -> Optional[str]:
    configured = configured_unsloth_base()
    if not configured:
        return None
    parsed = urlparse(configured if "://" in configured else f"http://{configured}")
    return parsed.hostname or None
