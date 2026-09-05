"""Fish Audio ASR for Voice Orb listening."""
import httpx

from services.stt.stt_service import FISH_ASR_URL, STTService


def _fish_settings(**overrides):
    settings = {
        "stt_enabled": False,
        "stt_provider": "disabled",
        "stt_model": "base",
        "stt_language": "en",
        "tts_provider": "fish",
        "fish_api_key": "sk-live-test-key-not-real-value-xxxxxx",
    }
    settings.update(overrides)
    return settings


def test_browser_stt_is_not_overridden_by_fish_tts(monkeypatch):
    service = STTService()
    monkeypatch.delenv("FISH_AUDIO_API_KEY", raising=False)
    monkeypatch.setattr(
        service,
        "_load_settings",
        lambda: _fish_settings(stt_enabled=True, stt_provider="browser"),
    )
    assert service._resolved_provider() == "browser"
    assert service.transcribe(b"fake-webm-bytes") is None


def test_stt_available_when_tts_is_fish_even_if_stt_toggle_is_off(monkeypatch):
    service = STTService()
    monkeypatch.delenv("FISH_AUDIO_API_KEY", raising=False)
    monkeypatch.setattr(service, "_load_settings", lambda: _fish_settings())
    assert service.available is True
    stats = service.get_stats()
    assert stats["available"] is True
    assert stats["provider"] == "fish"


def test_stt_disabled_without_fish_key_stays_unavailable(monkeypatch):
    service = STTService()
    monkeypatch.delenv("FISH_AUDIO_API_KEY", raising=False)
    monkeypatch.setattr(
        service,
        "_load_settings",
        lambda: _fish_settings(fish_api_key="", tts_provider="fish"),
    )
    assert service.available is False


def test_transcribe_fish_posts_multipart_asr(monkeypatch):
    service = STTService()
    monkeypatch.setattr(service, "_load_settings", lambda: _fish_settings())
    posted = {}

    class FakeResp:
        status_code = 200
        def raise_for_status(self):
            return None
        def json(self):
            return {"text": "Hello from the orb.", "duration": 1.2}

    def fake_post(url, headers=None, files=None, data=None, timeout=None):
        posted["url"] = url
        posted["headers"] = headers
        posted["files"] = files
        posted["data"] = data
        return FakeResp()

    monkeypatch.setattr(httpx, "post", fake_post)
    text = service.transcribe(b"fake-webm-bytes")
    assert text == "Hello from the orb."
    assert posted["url"] == FISH_ASR_URL
    assert posted["headers"]["Authorization"].startswith("Bearer ")
    assert posted["files"]["audio"][0] == "speech.webm"
    assert posted["data"]["language"] == "en"
    assert posted["data"]["ignore_timestamps"] == "true"


def test_transcribe_fish_sends_wav_when_riff(monkeypatch):
    service = STTService()
    monkeypatch.setattr(service, "_load_settings", lambda: _fish_settings())
    posted = {}

    class FakeResp:
        status_code = 200
        def json(self):
            return {"text": "Wave hello.", "duration": 0.4}

    def fake_post(url, headers=None, files=None, data=None, timeout=None):
        posted["files"] = files
        return FakeResp()

    monkeypatch.setattr(httpx, "post", fake_post)
    assert service.transcribe(b"RIFF" + b"\x00" * 20) == "Wave hello."
    assert posted["files"]["audio"][0] == "speech.wav"


def test_transcribe_fish_402_falls_back_to_local(monkeypatch):
    service = STTService()
    monkeypatch.setattr(service, "_load_settings", lambda: _fish_settings())
    monkeypatch.setattr(service, "_transcribe_local", lambda audio, language="": "local transcript")

    class FakeResp:
        status_code = 402
        def json(self):
            return {"status": 402, "message": "Insufficient API credit."}

    monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: FakeResp())
    assert service.transcribe(b"RIFF" + b"\x00" * 20) == "local transcript"


def test_transcribe_fish_skips_asr_after_402(monkeypatch):
    service = STTService()
    monkeypatch.setattr(service, "_load_settings", lambda: _fish_settings())
    monkeypatch.setattr(service, "_transcribe_local", lambda audio, language="": "local transcript")
    posts = []

    class FakeResp:
        status_code = 402
        def json(self):
            return {"status": 402, "message": "Insufficient API credit."}

    def fake_post(*args, **kwargs):
        posts.append(kwargs)
        return FakeResp()

    monkeypatch.setattr(httpx, "post", fake_post)
    assert service.transcribe(b"RIFF" + b"\x00" * 20) == "local transcript"
    assert service.transcribe(b"RIFF" + b"\x00" * 20) == "local transcript"
    assert len(posts) == 1


def test_transcribe_fish_402_empty_local_returns_empty(monkeypatch):
    service = STTService()
    monkeypatch.setattr(service, "_load_settings", lambda: _fish_settings())
    monkeypatch.setattr(service, "_transcribe_local", lambda audio, language="": "")

    class FakeResp:
        status_code = 402
        def json(self):
            return {"status": 402, "message": "Insufficient API credit."}

    monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: FakeResp())
    assert service.transcribe(b"RIFF" + b"\x00" * 20) == ""
    assert service.transcribe(b"RIFF" + b"\x00" * 20) == ""


def test_transcribe_local_skips_novad_retry_on_tiny_silence(monkeypatch):
    service = STTService()
    calls = []

    class Info:
        language = "en"
        language_probability = 0.3
        duration = 10.0
        duration_after_vad = 0.0

    class FakeModel:
        def transcribe(self, path, **kwargs):
            calls.append(kwargs)
            return iter([]), Info()

    monkeypatch.setattr(service, "_get_whisper", lambda: FakeModel())
    assert service._transcribe_local(b"RIFF" + b"\x00" * 20, "en") == ""
    assert [item.get("vad_filter") for item in calls] == [True]
    assert calls[0]["vad_parameters"]["speech_pad_ms"] == 200
    assert calls[0]["vad_parameters"]["threshold"] == 0.35


def test_transcribe_local_skips_novad_retry_on_large_silence(monkeypatch):
    service = STTService()
    calls = []

    class Info:
        language = "en"
        language_probability = 0.25
        duration = 9.96
        duration_after_vad = 0.0

    class FakeModel:
        def transcribe(self, path, **kwargs):
            calls.append(kwargs.get("vad_filter"))
            return iter([]), Info()

    monkeypatch.setattr(service, "_get_whisper", lambda: FakeModel())
    assert service._transcribe_local(b"RIFF" + b"\x00" * 16000, "en") == ""
    assert calls == [True]


def test_transcribe_local_retries_without_vad_when_empty(monkeypatch):
    service = STTService()
    calls = []

    class Seg:
        text = " hello "

    class Info:
        language = "en"
        language_probability = 0.9
        duration = 10.0
        duration_after_vad = 2.4

    class FakeModel:
        def transcribe(self, path, **kwargs):
            calls.append(kwargs.get("vad_filter"))
            if kwargs.get("vad_filter"):
                return iter([]), Info()
            return iter([Seg()]), Info()

    monkeypatch.setattr(service, "_get_whisper", lambda: FakeModel())
    assert service._transcribe_local(b"RIFF" + b"\x00" * 9000, "en") == "hello"
    assert calls == [True, False]
