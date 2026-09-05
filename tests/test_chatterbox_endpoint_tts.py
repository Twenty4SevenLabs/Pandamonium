"""Panda talks to the Linux M1 Chatterbox OpenAI TTS server."""
import httpx

from services.tts.tts_service import TTSService


class _Eq:
    def __eq__(self, other):
        return True


class _ModelEndpoint:
    id = _Eq()


class _Ep:
    id = "m1-chatterbox"
    base_url = "http://192.168.1.181:8030/v1"
    api_key = ""


class _FakeDB:
    def query(self, _model):
        return self

    def filter(self, *_args, **_kwargs):
        return self

    def first(self):
        return _Ep()

    def close(self):
        return None


def test_list_voices_falls_back_to_audio_voices(tmp_path, monkeypatch):
    service = TTSService(cache_dir=str(tmp_path))
    monkeypatch.setattr(
        service,
        "_load_settings",
        lambda: {
            "tts_enabled": True,
            "tts_provider": "endpoint:m1-chatterbox",
            "tts_model": "chatterbox-tts",
            "tts_voice": "jarvis_chatterbox",
            "tts_speed": "1",
        },
    )

    monkeypatch.setattr("src.database.SessionLocal", _FakeDB)
    monkeypatch.setattr("src.database.ModelEndpoint", _ModelEndpoint)

    urls = []

    class FakeResp:
        def __init__(self, status, payload=None):
            self.status_code = status
            self._payload = payload or {}

        def raise_for_status(self):
            if self.status_code >= 400:
                raise httpx.HTTPStatusError("nope", request=None, response=self)

        def json(self):
            return self._payload

    def fake_get(url, headers=None, timeout=None):
        urls.append(url)
        if url.endswith("/voices") and not url.endswith("/audio/voices"):
            return FakeResp(404)
        if url.endswith("/audio/voices"):
            return FakeResp(
                200,
                {
                    "voices": [
                        {"id": "jarvis_chatterbox", "label": "Jarvis"},
                        {"id": "gordon_chatterbox", "label": "Gordon"},
                        {"id": "friday_chatterbox", "label": "Friday"},
                    ]
                },
            )
        return FakeResp(404)

    monkeypatch.setattr(httpx, "get", fake_get)
    voices = service.list_voices()
    assert [v["id"] for v in voices] == [
        "jarvis_chatterbox",
        "gordon_chatterbox",
        "friday_chatterbox",
    ]
    assert any(u.endswith("/audio/voices") for u in urls)


def test_endpoint_speech_accepts_wav_even_when_mp3_requested(tmp_path, monkeypatch):
    service = TTSService(cache_dir=str(tmp_path))
    monkeypatch.setattr(
        service,
        "_load_settings",
        lambda: {
            "tts_enabled": True,
            "tts_provider": "endpoint:m1-chatterbox",
            "tts_model": "chatterbox-tts",
            "tts_voice": "jarvis_chatterbox",
            "tts_speed": "1",
        },
    )

    monkeypatch.setattr("src.database.SessionLocal", _FakeDB)
    monkeypatch.setattr("src.database.ModelEndpoint", _ModelEndpoint)

    wav = b"RIFF" + b"\x00" * 4 + b"WAVE" + b"\x00" * 40
    posted = {}

    class FakeResp:
        content = wav
        status_code = 200

        def raise_for_status(self):
            return None

    def fake_post(url, json=None, headers=None, timeout=None):
        posted["url"] = url
        posted["json"] = json
        return FakeResp()

    monkeypatch.setattr(httpx, "post", fake_post)
    audio = service.synthesize("Sir, systems online.", use_cache=False)
    assert audio[:4] == b"RIFF"
    assert posted["url"].endswith("/audio/speech")
    assert posted["json"]["voice"] == "jarvis_chatterbox"
    assert posted["json"]["response_format"] == "wav"
