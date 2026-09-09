#!/usr/bin/env python3
"""Build OpenCode provider blocks from live Unsloth fleet /v1/models scans."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from copy import deepcopy
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ENV_FILE = REPO / ".env"

# (provider_id, display_name, base_url, env var for API key)
FLEET_NODES: list[tuple[str, str, str, str]] = [
    ("unsloth-m1", "Unsloth M1 (LAN)", "http://192.168.1.2:8888/v1", "UNSLOTH_M1_API_KEY"),
    ("unsloth-m1-guest", "Unsloth M1 guest (181)", "http://192.168.1.181:8888/v1", "UNSLOTH_M1_API_KEY"),
    ("unsloth-m1-tailscale", "Unsloth M1 (Tailscale)", "http://100.100.247.127:8888/v1", "UNSLOTH_M1_API_KEY"),
    ("unsloth-m1-serve", "Unsloth M1 (Serve HTTPS)", "https://m1.tail61d527.ts.net/v1", "UNSLOTH_M1_API_KEY"),
    ("unsloth-m2", "Unsloth M2 (LAN)", "http://192.168.1.191:8888/v1", "UNSLOTH_M2_API_KEY"),
    ("unsloth-m2-tailscale", "Unsloth M2 (Tailscale)", "http://100.123.238.35:8888/v1", "UNSLOTH_M2_API_KEY"),
    ("unsloth-m2-serve", "Unsloth M2 (Serve HTTPS)", "https://m2.tail61d527.ts.net/v1", "UNSLOTH_M2_API_KEY"),
    ("unsloth-a1", "Unsloth A1 (James MBP)", "http://100.80.146.51:8888/v1", "UNSLOTH_A1_API_KEY"),
    ("unsloth-imac", "Unsloth iMac (Luna)", "http://100.85.221.36:8888/v1", "UNSLOTH_IMAC_API_KEY"),
    ("unsloth-mini", "Unsloth Mac mini (Tom)", "http://100.87.228.16:8888/v1", "UNSLOTH_MINI_API_KEY"),
    ("unsloth-laptop", "Unsloth 247Laptop (local)", "http://100.112.1.19:8888/v1", "UNSLOTH_LAPTOP_API_KEY"),
]

WINDOWS_PREFERRED = {
    "unsloth-m1-serve",
    "unsloth-m2-serve",
    "unsloth-m1-tailscale",
    "unsloth-m2-tailscale",
    "unsloth-a1",
    "unsloth-imac",
    "unsloth-mini",
    "unsloth-laptop",
    "unsloth-m1",
    "unsloth-m2",
    "unsloth-m1-guest",
}

FALLBACK_MODELS: dict[str, dict] = {
    "unsloth-m1": {
        "unsloth/Qwen3.5-9B-GGUF": {"name": "M1 · Qwen3.5 9B", "limit": {"context": 65536, "output": 8192}},
        "unsloth/Qwen3-14B-GGUF": {"name": "M1 · Qwen3 14B", "limit": {"context": 32768, "output": 8192}},
        "unsloth/FLUX.2-klein-4B-GGUF": {"name": "M1 · FLUX klein 4B", "limit": {"context": 32768, "output": 8192}},
    },
    "unsloth-m2": {
        "unsloth/Qwen2.5-Coder-7B-Instruct-GGUF": {
            "name": "M2 · Qwen2.5 Coder 7B",
            "limit": {"context": 32768, "output": 8192},
        },
        "unsloth/Qwen3.5-9B-GGUF": {"name": "M2 · Qwen3.5 9B", "limit": {"context": 32768, "output": 8192}},
    },
}


def load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def api_key(env_name: str) -> str:
    value = os.environ.get(env_name, "").strip()
    if value:
        return value
    if env_name != "UNSLOTH_API_KEY":
        return os.environ.get("UNSLOTH_API_KEY", "").strip()
    return ""


def fetch_models(base_url: str, key: str) -> dict | None:
    url = base_url.rstrip("/")
    if not url.endswith("/v1"):
        url += "/v1"
    req = urllib.request.Request(
        f"{url}/models",
        headers={"Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            payload = json.load(resp)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError):
        return None
    models: dict = {}
    for row in payload.get("data", []):
        model_id = row.get("id")
        if not model_id:
            continue
        ctx = row.get("context_length") or row.get("max_model_len") or 32768
        short = model_id.split("/")[-1]
        models[model_id] = {
            "name": short,
            "limit": {"context": min(int(ctx), 131072), "output": 8192},
        }
    return models or None


def clone_models(source_id: str, providers: dict) -> dict | None:
    if source_id in providers:
        return deepcopy(providers[source_id]["models"])
    base = source_id.removesuffix("-tailscale").removesuffix("-serve").removesuffix("-guest")
    if base in providers:
        return deepcopy(providers[base]["models"])
    if base in FALLBACK_MODELS:
        return deepcopy(FALLBACK_MODELS[base])
    return None


def build_providers() -> tuple[dict, list[str]]:
    providers: dict = {}
    log: list[str] = []
    for pid, name, base, env_name in FLEET_NODES:
        key = api_key(env_name)
        if not key:
            log.append(f"skip {pid}: missing {env_name}")
            continue
        models = fetch_models(base, key)
        if models:
            log.append(f"ok   {pid}: {len(models)} models (live)")
        else:
            models = clone_models(pid, providers)
            if models:
                log.append(f"fill {pid}: {len(models)} models (cloned/fallback)")
            else:
                log.append(f"fail {pid}: unreachable and no fallback")
                continue
        base_norm = base.rstrip("/")
        if not base_norm.endswith("/v1"):
            base_norm += "/v1"
        providers[pid] = {
            "npm": "@ai-sdk/openai-compatible",
            "name": name,
            "options": {
                "baseURL": base_norm,
                "apiKey": f"{{env:{env_name}}}",
            },
            "models": models,
        }
    return providers, log


def write_config(path: Path, providers: dict, *, default_model: str, enabled: list[str]) -> None:
    doc = {
        "$schema": "https://opencode.ai/config.json",
        "provider": providers,
        "model": default_model,
        "enabled_providers": enabled,
        "compaction": {"auto": True, "reserved": 3276},
    }
    path.write_text(json.dumps(doc, indent=2) + "\n")


def main() -> int:
    load_dotenv(ENV_FILE)
    providers, log = build_providers()
    if not providers:
        print("No Unsloth providers could be built.", file=sys.stderr)
        return 1

    enabled_linux = list(providers.keys())
    default = "unsloth-m2/unsloth/Qwen2.5-Coder-7B-Instruct-GGUF"
    if default.split("/", 1)[0] not in providers:
        first = next(iter(providers))
        first_model = next(iter(providers[first]["models"]))
        default = f"{first}/{first_model}"

    write_config(REPO / "opencode.json", providers, default_model=default, enabled=enabled_linux)

    windows_providers = {
        pid: providers[pid] for pid in WINDOWS_PREFERRED if pid in providers
    }
    if not windows_providers:
        windows_providers = providers
    win_enabled = list(windows_providers.keys())
    win_default = default
    if win_default.split("/", 1)[0] not in windows_providers:
        first = next(iter(windows_providers))
        first_model = next(iter(windows_providers[first]["models"]))
        win_default = f"{first}/{first_model}"
    write_config(
        REPO / "opencode.windows.json",
        windows_providers,
        default_model=win_default,
        enabled=win_enabled,
    )

    print(f"Wrote {REPO / 'opencode.json'} ({len(providers)} providers)")
    print(f"Wrote {REPO / 'opencode.windows.json'} ({len(windows_providers)} providers)")
    for line in log:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
