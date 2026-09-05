"""Tests for Unsloth Studio client helpers."""
import httpx

from src.unsloth_client import (
    _active_model_matches,
    _extract_downloaded_local_ids,
    _resolve_load_id_from_catalog,
    is_unsloth_endpoint,
    list_studio_model_ids,
    load_model,
    normalize_openai_base,
    parse_unsloth_model_id,
    studio_api_root,
)

_LMSTUDIO_QWEN = {
    "id": "/Users/ollama/.lmstudio/models/lmstudio-community/Qwen3.8-27B-MLX-4bit",
    "display_name": "Qwen3.8-27B-MLX-4bit",
    "path": "/Users/ollama/.lmstudio/models/lmstudio-community/Qwen3.8-27B-MLX-4bit",
    "source": "lmstudio",
    "model_id": "lmstudio-community/Qwen3.8-27B-MLX-4bit",
    "active_cache": None,
    "partial": False,
}


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
    assert _extract_downloaded_local_ids({"models": [_LMSTUDIO_QWEN]}) == [
        "lmstudio-community/Qwen3.8-27B-MLX-4bit"
    ]


def test_ensure_model_loaded_refuses_flux(monkeypatch):
    from src.unsloth_client import ensure_model_loaded

    called = []
    monkeypatch.setattr("src.unsloth_client.is_unsloth_endpoint", lambda _url: True)
    monkeypatch.setattr(
        "src.unsloth_client._ensure_model_loaded_inner",
        lambda *_a, **_k: called.append("loaded") or True,
    )
    assert ensure_model_loaded("http://192.168.1.2:8888/v1", "unsloth/FLUX.2-klein-4B") is False
    assert called == []


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


def test_ensure_model_loaded_refuses_chatterbox(monkeypatch):
    monkeypatch.setattr("src.unsloth_client.is_unsloth_endpoint", lambda _u: True)
    monkeypatch.setattr("src.unsloth_client.rewrite_unsloth_url", lambda u: u)
    monkeypatch.setattr(
        "src.unsloth_client.load_model",
        lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("must not load TTS")),
    )
    from src.unsloth_client import ensure_model_loaded
    assert ensure_model_loaded("http://192.168.1.2:8888/v1", "ResembleAI/chatterbox", "key") is False


def test_active_model_matches_lmstudio_folder_to_short_id():
    """A1 Unsloth reports the LM Studio folder; the picker sends the /v1 id.

    Exact-string compare treated these as different models and POSTed
    /api/inference/load, which Hugging Face 401'd as unsloth/Qwen3.8-27B-MLX-4bit.
    """
    status = {
        "active_model": "/Users/ollama/.lmstudio/models/lmstudio-community/Qwen3.8-27B-MLX-4bit",
        "loading": [],
    }
    assert _active_model_matches(status, "Qwen3.8-27B-MLX-4bit")
    assert _active_model_matches(status, "lmstudio-community/Qwen3.8-27B-MLX-4bit")
    assert not _active_model_matches(status, "unsloth/Qwen3.5-9B-GGUF")


def test_active_model_matches_keeps_gguf_quant_distinct():
    status = {"active_model": "unsloth/Qwen3.5-9B-GGUF:UD-Q4_K_XL", "loading": []}
    assert _active_model_matches(status, "unsloth/Qwen3.5-9B-GGUF:UD-Q4_K_XL")
    assert _active_model_matches(status, "Qwen3.5-9B-GGUF:UD-Q4_K_XL")
    assert not _active_model_matches(status, "unsloth/Qwen3.5-9B-GGUF:Q4_K_M")


def test_resolve_load_id_from_catalog_maps_short_id_to_lmstudio_folder():
    """Idle A1 has no active_model; chat still stores the /v1 short id.

    POST /api/inference/load with model_path=Qwen3.8-27B-MLX-4bit is resolved
    as Hugging Face unsloth/Qwen3.8-27B-MLX-4bit (401/500). Use the local
    LM Studio folder instead.
    """
    payload = {"models": [_LMSTUDIO_QWEN]}
    assert (
        _resolve_load_id_from_catalog(payload, "Qwen3.8-27B-MLX-4bit")
        == _LMSTUDIO_QWEN["path"]
    )
    assert (
        _resolve_load_id_from_catalog(payload, "lmstudio-community/Qwen3.8-27B-MLX-4bit")
        == _LMSTUDIO_QWEN["path"]
    )


def test_resolve_load_id_from_catalog_leaves_hub_gguf_ids_alone():
    payload = {
        "models": [
            {
                "id": "unsloth/Qwen3.5-9B-GGUF",
                "display_name": "Qwen3.5-9B-GGUF",
                "path": None,
                "source": "hf_cache",
                "model_id": "unsloth/Qwen3.5-9B-GGUF",
                "partial": False,
            },
            {
                "id": "/Users/ollama/.cache/huggingface/hub/models--unsloth--Qwen3.5-9B-GGUF/snapshots/abc",
                "display_name": "Qwen3.5-9B-GGUF",
                "path": "/Users/ollama/.cache/huggingface/hub/models--unsloth--Qwen3.5-9B-GGUF/snapshots/abc",
                "source": "custom",
                "model_id": "unsloth/Qwen3.5-9B-GGUF",
                "partial": False,
            },
        ]
    }
    assert (
        _resolve_load_id_from_catalog(payload, "unsloth/Qwen3.5-9B-GGUF:UD-Q4_K_XL")
        is None
    )


def test_load_model_posts_lmstudio_folder_for_short_id(monkeypatch):
    posted = {}

    def fake_get_json(url, api_key, *, timeout, params=None):
        if url.endswith("/api/models/local"):
            return {"models": [_LMSTUDIO_QWEN]}
        raise AssertionError(f"unexpected url {url}")

    def fake_post_json(url, api_key, payload, timeout):
        posted["url"] = url
        posted["payload"] = payload
        return {}

    monkeypatch.setattr("src.unsloth_client._get_json", fake_get_json)
    monkeypatch.setattr("src.unsloth_client._post_json", fake_post_json)

    load_model("http://100.80.146.51:8888/v1", "Qwen3.8-27B-MLX-4bit", "key")
    assert posted["url"].endswith("/api/inference/load")
    assert posted["payload"]["model_path"] == _LMSTUDIO_QWEN["path"]
    assert "gguf_variant" not in posted["payload"]


def test_list_studio_model_ids_includes_lmstudio_mlx_folder(monkeypatch):
    def fake_get_json(url, api_key, *, timeout, params=None):
        if url.endswith("/v1/models"):
            return {"data": []}
        if url.endswith("/api/models/local"):
            return {"models": [_LMSTUDIO_QWEN]}
        if url.endswith("/api/models/gguf-variants"):
            return {}
        raise AssertionError(f"unexpected url {url}")

    monkeypatch.setattr("src.unsloth_client._get_json", fake_get_json)
    ids = list_studio_model_ids("http://100.80.146.51:8888/v1", "key")
    assert "lmstudio-community/Qwen3.8-27B-MLX-4bit" in ids
    assert not any(i.startswith("/Users/") for i in ids)


def test_ensure_model_loaded_skips_reload_when_lmstudio_path_already_active(monkeypatch):
    from src.unsloth_client import ensure_model_loaded

    calls = {"load": 0}

    def fake_status(base, key):
        return {
            "active_model": "/Users/ollama/.lmstudio/models/lmstudio-community/Qwen3.8-27B-MLX-4bit",
            "loading": [],
        }

    def fake_load(*_a, **_k):
        calls["load"] += 1
        return {}

    monkeypatch.setattr("src.unsloth_client.get_inference_status", fake_status)
    monkeypatch.setattr("src.unsloth_client.load_model", fake_load)
    monkeypatch.setattr("src.unsloth_client.is_unsloth_endpoint", lambda _u: True)
    monkeypatch.setattr("src.unsloth_client.rewrite_unsloth_url", lambda u: u)

    ok = ensure_model_loaded(
        "http://100.80.146.51:8888/v1",
        "Qwen3.8-27B-MLX-4bit",
        "key",
    )
    assert ok is True
    assert calls["load"] == 0


def test_unsloth_studio_targets_skips_lmstudio_port(monkeypatch):
    from src.unsloth_client import unsloth_studio_targets

    monkeypatch.setenv("UNSLOTH_BASE_URL", "http://192.168.1.2:8888/v1")
    monkeypatch.setenv("UNSLOTH_M2_BASE_URL", "http://192.168.1.191:8888/v1")
    monkeypatch.setenv("UNSLOTH_A1_BASE_URL", "http://100.80.146.51:8888/v1")
    monkeypatch.setenv(
        "UNSLOTH_EXTRA_BASE_URLS",
        "http://192.168.1.191:8888/v1,http://100.80.146.51:1234/v1",
    )
    monkeypatch.setenv("LLM_HOSTS", "192.168.1.2,100.85.221.36,100.87.228.16")
    bases = [t["base_url"] for t in unsloth_studio_targets()]
    assert "http://192.168.1.2:8888/v1" in bases
    assert "http://192.168.1.191:8888/v1" in bases
    assert "http://100.80.146.51:8888/v1" in bases
    assert "http://100.85.221.36:8888/v1" in bases
    assert "http://100.87.228.16:8888/v1" in bases
    assert not any(":1234" in b for b in bases)
    names = {t["base_url"]: t["name"] for t in unsloth_studio_targets()}
    assert "M1" in names["http://192.168.1.2:8888/v1"]
    assert "M2" in names["http://192.168.1.191:8888/v1"]


def test_stream_llm_yields_sse_error_when_unsloth_load_fails(monkeypatch):
    """Load failure must be an SSE error event, not an uncaught RuntimeError.

    FastAPI StreamingResponse turns a raised generator exception into HTTP 500
    ("Error 500" in the chat UI). Yielding event:error keeps the stream 200.
    """
    import asyncio
    import json

    from src import llm_core

    monkeypatch.setattr(
        "src.unsloth_client.ensure_model_loaded",
        lambda *_a, **_k: False,
    )
    monkeypatch.setattr("src.unsloth_client.is_unsloth_endpoint", lambda _u: True)
    monkeypatch.setattr("src.unsloth_client.rewrite_unsloth_url", lambda u: u)
    monkeypatch.setattr("src.unsloth_client.resolve_unsloth_api_key", lambda *_a, **_k: "key")

    inner_called = {"n": 0}

    async def fake_inner(*_a, **_k):
        inner_called["n"] += 1
        if False:
            yield "nope"

    monkeypatch.setattr(llm_core, "_stream_llm_inner", fake_inner)

    async def collect():
        out = []
        async for chunk in llm_core.stream_llm(
            "http://100.80.146.51:8888/v1",
            "Qwen3.8-27B-MLX-4bit",
            [{"role": "user", "content": "hi"}],
        ):
            out.append(chunk)
        return out

    chunks = asyncio.run(collect())
    assert inner_called["n"] == 0
    assert any(c.startswith("event: error") for c in chunks)
    payload = None
    for c in chunks:
        if c.startswith("event: error"):
            data_line = [ln for ln in c.split("\n") if ln.startswith("data: ")][0]
            payload = json.loads(data_line[6:])
    assert payload is not None
    assert payload["status"] == 502
    assert "Qwen3.8-27B-MLX-4bit" in (payload.get("text") or payload.get("error") or "")
