"""Tests for Unsloth Studio client helpers."""
import httpx

from src.unsloth_client import (
    _extract_downloaded_local_ids,
    is_unsloth_endpoint,
    list_studio_model_ids,
    normalize_openai_base,
    parse_unsloth_model_id,
    studio_api_root,
)


def test_studio_api_root_strips_v1():
    assert studio_api_root("http://192.168.1.181:8888/v1") == "http://192.168.1.181:8888"


def test_parse_unsloth_model_id_splits_quant():
    repo, quant = parse_unsloth_model_id("unsloth/gemma-4-26B-A4B-it-GGUF:UD-Q4_K_XL")
    assert repo == "unsloth/gemma-4-26B-A4B-it-GGUF"
    assert quant == "UD-Q4_K_XL"


def test_parse_unsloth_model_id_without_quant():
    repo, quant = parse_unsloth_model_id("unsloth/Qwen3-1.7B-GGUF")
    assert repo == "unsloth/Qwen3-1.7B-GGUF"
    assert quant is None


def test_is_unsloth_endpoint_matches_env(monkeypatch):
    monkeypatch.setenv("UNSLOTH_BASE_URL", "http://192.168.1.181:8888/v1")
    assert is_unsloth_endpoint("http://192.168.1.181:8888/v1")
    assert is_unsloth_endpoint("http://192.168.1.181:8888/v1/")
    assert not is_unsloth_endpoint("http://localhost:11434/v1")


def test_is_unsloth_endpoint_matches_default_port(monkeypatch):
    monkeypatch.delenv("UNSLOTH_BASE_URL", raising=False)
    assert is_unsloth_endpoint("http://m1.tail61d527.ts.net:8888/v1")
    assert is_unsloth_endpoint("http://m1.tail61d527.ts.net:8889/v1")
    assert is_unsloth_endpoint("https://m1.tail61d527.ts.net/v1")
    assert not is_unsloth_endpoint("http://example.com:1234/v1")


def test_is_unsloth_endpoint_matches_chat_completions_url(monkeypatch):
    """Chat sessions store the OpenAI chat URL, not the /v1 base.

    stream_llm() is called with sess.endpoint_url which ends in
    /v1/chat/completions. If we miss that, ensure_model_loaded never runs
    and Unsloth keeps serving whichever GGUF is already in memory.
    """
    monkeypatch.setenv("UNSLOTH_BASE_URL", "https://m1.tail61d527.ts.net/v1")
    assert is_unsloth_endpoint("https://m1.tail61d527.ts.net/v1/chat/completions")
    assert is_unsloth_endpoint("https://m1.tail61d527.ts.net/v1/chat/completions/")
    monkeypatch.delenv("UNSLOTH_BASE_URL", raising=False)
    assert is_unsloth_endpoint("https://m1.tail61d527.ts.net/v1/chat/completions")
    assert is_unsloth_endpoint("http://m1.tail61d527.ts.net:8889/v1/chat/completions")


def test_normalize_openai_base():
    assert normalize_openai_base("http://host:8888/v1/") == "http://host:8888/v1"
    assert (
        normalize_openai_base("https://m1.tail61d527.ts.net/v1/chat/completions")
        == "https://m1.tail61d527.ts.net/v1"
    )


def test_studio_api_root_strips_chat_completions():
    assert studio_api_root("https://m1.tail61d527.ts.net/v1/chat/completions") == "https://m1.tail61d527.ts.net"


def test_extract_downloaded_local_ids_skips_partial():
    payload = {
        "models": [
            {"id": "unsloth/Qwen3.5-9B-GGUF", "partial": False},
            {"id": "luxuansang/Qwen3.8-9B-heretic-uncensored-NVFP4-GGUF", "partial": True},
            {"id": "unsloth/FLUX.2-klein-4B", "partial": False, "active_cache": False},
        ]
    }
    assert _extract_downloaded_local_ids(payload) == ["unsloth/Qwen3.5-9B-GGUF"]


def test_list_studio_model_ids_merges_local_catalog(monkeypatch):
    calls = []

    def fake_get_json(url, api_key, *, timeout, params=None):
        calls.append(url)
        if url.endswith("/v1/models"):
            return {
                "data": [
                    {"id": "unsloth/Qwen3.5-9B-GGUF"},
                ]
            }
        if url.endswith("/api/models/local"):
            return {
                "models": [
                    {"id": "unsloth/Qwen3.5-9B-GGUF", "partial": False},
                    {"id": "unsloth/Qwen3-14B-GGUF", "partial": False},
                    {"id": "unsloth/FLUX.2-klein-4B-GGUF", "partial": False},
                ]
            }
        if url.endswith("/api/models/gguf-variants"):
            repo = (params or {}).get("repo_id") or ""
            return {"variants": [{"quant": "UD-Q4_K_XL", "downloaded": True}], "default_variant": "UD-Q4_K_XL"} if repo else {}
        raise AssertionError(f"unexpected url {url}")

    monkeypatch.setattr("src.unsloth_client._get_json", fake_get_json)
    ids = list_studio_model_ids("https://m1.example/v1", "test-key")
    assert "unsloth/Qwen3.5-9B-GGUF:UD-Q4_K_XL" in ids
    assert "unsloth/Qwen3-14B-GGUF:UD-Q4_K_XL" in ids
    assert "unsloth/Qwen3.5-9B-GGUF" in ids


def test_rewrite_unsloth_url_uses_lan_wake_proxy(monkeypatch):
    from src.unsloth_client import rewrite_unsloth_url

    monkeypatch.delenv("UNSLOTH_LAN_PROXY", raising=False)
    assert (
        rewrite_unsloth_url("http://192.168.1.181:8888/v1/chat/completions")
        == "http://192.168.1.2:8888/v1/chat/completions"
    )
    assert rewrite_unsloth_url("https://m1.tail61d527.ts.net/v1") == "http://192.168.1.2:8888/v1"
    assert rewrite_unsloth_url("http://192.168.1.2:8888/v1") == "http://192.168.1.2:8888/v1"


def test_ensure_model_loaded_wakes_idle_gpu_then_retries(monkeypatch):
    from src.unsloth_client import ensure_model_loaded

    calls = {"status": 0, "wake": 0}

    def fake_status(base, key):
        calls["status"] += 1
        if calls["status"] == 1:
            raise httpx.ConnectError("[Errno 113] No route to host")
        return {"active_model": "unsloth/Qwen3.5-9B-GGUF", "loading": []}

    def fake_wake():
        calls["wake"] += 1
        return True

    monkeypatch.setattr("src.unsloth_client.get_inference_status", fake_status)
    monkeypatch.setattr("src.unsloth_client._wake_unsloth_backend", fake_wake)
    monkeypatch.setattr("src.unsloth_client.is_unsloth_endpoint", lambda _u: True)
    monkeypatch.setattr("src.unsloth_client.rewrite_unsloth_url", lambda u: u)

    ok = ensure_model_loaded("http://192.168.1.2:8888/v1", "unsloth/Qwen3.5-9B-GGUF", "key")
    assert ok is True
    assert calls["wake"] == 1
    assert calls["status"] == 2


def test_ensure_model_loaded_waits_for_active(monkeypatch):
    calls = {"load": 0, "status": 0}

    def fake_status(base, key):
        calls["status"] += 1
        if calls["status"] < 3:
            return {"active_model": "unsloth/Qwen3-14B-GGUF", "loading": []}
        return {"active_model": "unsloth/Qwen3.5-9B-GGUF", "loading": []}

    def fake_load(base, model_id, key, **kwargs):
        calls["load"] += 1
        return {}

    monkeypatch.setattr("src.unsloth_client.get_inference_status", fake_status)
    monkeypatch.setattr("src.unsloth_client.load_model", fake_load)
    monkeypatch.setattr("src.unsloth_client.time.sleep", lambda _s: None)
    monkeypatch.setattr("src.unsloth_client.is_unsloth_endpoint", lambda _u: True)

    ok = __import__("src.unsloth_client", fromlist=["ensure_model_loaded"]).ensure_model_loaded(
        "https://m1.example/v1",
        "unsloth/Qwen3.5-9B-GGUF",
        "key",
    )
    assert ok is True
    assert calls["load"] == 1
    assert calls["status"] >= 3
