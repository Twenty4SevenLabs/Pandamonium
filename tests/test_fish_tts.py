"""Fish Audio S2.1 Pro TTS provider."""
import httpx

from services.tts.tts_service import (
    FISH_TTS_URL,
    TTSService,
    _fish_headers,
    _fish_tts_body,
    _parse_fish_voice_items,
)


def test_parse_fish_voice_items_uses_id_and_title():
    items = [
        {"_id": "abc123", "title": "Narrator"},
        {"id": "def456", "name": "Alt"},
        {"title": "no-id"},
        "skip-me",
    ]
    assert _parse_fish_voice_items(items) == [
        {"id": "abc123", "label": "Narrator"},
        {"id": "def456", "label": "Alt"},
    ]


def test_fish_tts_body_and_headers():
    body = _fish_tts_body("Hello world", "voice-1", 1.25)
    assert body["text"] == "Hello world"
    assert body["reference_id"] == "voice-1"
    assert body["format"] == "wav"
    assert body["sample_rate"] == 44100
    assert body["prosody"]["speed"] == 1.25
    headers = _fish_headers("s2.1-pro-free", "sk-test")
    assert headers["Authorization"] == "Bearer sk-test"
    assert headers["model"] == "s2.1-pro-free"
    assert headers["Content-Type"] == "application/json"


def test_fish_available_requires_key(tmp_path, monkeypatch):
    service = TTSService(cache_dir=str(tmp_path))
    monkeypatch.delenv("FISH_AUDIO_API_KEY", raising=False)
    monkeypatch.setattr(
        service,
        "_load_settings",
        lambda: {
            "tts_enabled": True,
            "tts_provider": "fish",
            "tts_model": "s2.1-pro-free",
            "tts_voice": "abc",
            "tts_speed": "1",
            "fish_api_key": "",
        },
    )
    assert service.available is False
    monkeypatch.setattr(
        service,
        "_load_settings",
        lambda: {
            "tts_enabled": True,
            "tts_provider": "fish",
            "tts_model": "s2.1-pro-free",
            "tts_voice": "abc",
            "tts_speed": "1",
            "fish_api_key": "sk-live-test-key-not-real-value",
        },
    )
    assert service.available is True


def test_synthesize_fish_posts_s21_pro_free(tmp_path, monkeypatch):
    service = TTSService(cache_dir=str(tmp_path))
    monkeypatch.setattr(
        service,
        "_load_settings",
        lambda: {
            "tts_enabled": True,
            "tts_provider": "fish",
            "tts_model": "s2.1-pro-free",
            "tts_voice": "voice-9",
            "tts_speed": "1.5",
            "fish_api_key": "sk-live-test-key-not-real-value",
        },
    )
    posted = {}

    class FakeResp:
        status_code = 200
        content = b"RIFF....WAVEfmt "
        def raise_for_status(self):
            return None

    def fake_post(url, json=None, headers=None, timeout=None):
        posted["url"] = url
        posted["json"] = json
        posted["headers"] = headers
        return FakeResp()

    monkeypatch.setattr(httpx, "post", fake_post)
    audio = service.synthesize("Hello from Fish", use_cache=False)
    assert audio == b"RIFF....WAVEfmt "
    assert posted["url"] == FISH_TTS_URL
    assert posted["headers"]["model"] == "s2.1-pro-free"
    assert posted["json"]["reference_id"] == "voice-9"
    assert posted["json"]["format"] == "wav"
    assert posted["json"]["sample_rate"] == 44100
    assert posted["json"]["prosody"]["speed"] == 1.5


def test_fish_http_error_message_from_json_body():
    from services.tts.tts_service import TTSError, _fish_error_message

    class Resp:
        status_code = 401
        def json(self):
            return {"status": 401, "message": "Invalid Token"}
        text = ""

    msg = _fish_error_message(Resp())
    assert "Invalid Token" in msg
    err = TTSError(msg, status=401)
    assert err.status == 401


def test_synthesize_fish_raises_tts_error_on_401(tmp_path, monkeypatch):
    from services.tts.tts_service import TTSError

    service = TTSService(cache_dir=str(tmp_path))
    monkeypatch.setattr(
        service,
        "_load_settings",
        lambda: {
            "tts_enabled": True,
            "tts_provider": "fish",
            "tts_model": "s2.1-pro-free",
            "tts_voice": "voice-9",
            "tts_speed": "1",
            "fish_api_key": "not-a-real-fish-token-value",
        },
    )

    class FakeResp:
        status_code = 401
        text = '{"status":401,"message":"Invalid Token"}'
        def json(self):
            return {"status": 401, "message": "Invalid Token"}

    monkeypatch.setattr(httpx, "post", lambda *a, **k: FakeResp())
    try:
        service.synthesize("Hello from Fish", use_cache=False)
        raise AssertionError("expected TTSError")
    except TTSError as err:
        assert err.status == 401
        assert "Invalid Token" in err.message


def test_fish_skips_chatterbox_agent_voice_ids():
    from services.tts.tts_service import _fish_usable_voice

    assert _fish_usable_voice("jarvis_chatterbox", "bf322df2096a46f18c579d0baa36f41d") == (
        "bf322df2096a46f18c579d0baa36f41d"
    )
    assert _fish_usable_voice("bf322df2096a46f18c579d0baa36f41d", "other") == (
        "bf322df2096a46f18c579d0baa36f41d"
    )


def test_normalize_fish_api_key_strips_bearer_and_quotes():
    from services.tts.tts_service import _normalize_fish_api_key

    assert _normalize_fish_api_key('Bearer abcdefghijklmnopqrstuv') == "abcdefghijklmnopqrstuv"
    assert _normalize_fish_api_key('"real-key-value-here-long"') == "real-key-value-here-long"


def test_list_fish_voices_merges_self_then_public(tmp_path, monkeypatch):
    service = TTSService(cache_dir=str(tmp_path))
    monkeypatch.setattr(
        service,
        "_load_settings",
        lambda: {
            "tts_enabled": True,
            "tts_provider": "fish",
            "tts_model": "s2.1-pro-free",
            "tts_voice": "",
            "tts_speed": "1",
            "fish_api_key": "sk-live-test-key-not-real-value",
        },
    )
    calls = []

    class FakeResp:
        content = b'{"items":[]}'
        def __init__(self, payload):
            self._payload = payload
        def raise_for_status(self):
            return None
        def json(self):
            return self._payload

    def fake_get(url, headers=None, params=None, timeout=None):
        calls.append(params)
        if params and params.get("self") is True:
            return FakeResp({"items": [{"_id": "mine", "title": "My clone"}]})
        return FakeResp({"items": [{"_id": "pub", "title": "Public voice"}, {"_id": "mine", "title": "dup"}]})

    monkeypatch.setattr(httpx, "get", fake_get)
    voices = service.list_voices()
    assert voices[0] == {"id": "mine", "label": "My clone"}
    assert {"id": "pub", "label": "Public voice"} in voices
    assert sum(1 for v in voices if v["id"] == "mine") == 1
