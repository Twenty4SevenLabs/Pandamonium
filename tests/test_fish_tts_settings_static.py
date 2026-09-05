"""Static wiring for Fish Audio S2.1 Pro in the Voice settings card."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_voice_settings_has_fish_provider_and_key_placeholder():
    html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    assert 'option value="fish">Fish Audio (S2.1 Pro)</option>' in html
    assert 'placeholder="Fish Audio API key"' in html
    assert 'id="set-ttsApiKey"' in html
    assert "s2.1-pro-free" in html


def test_settings_js_enables_fish_stt_when_saving_fish_tts():
    js = (ROOT / "static" / "js" / "settings.js").read_text(encoding="utf-8")
    html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    assert "stt_provider: 'fish'" in js
    assert "stt_enabled: true" in js
    assert "listen" in html.lower() or "Fish ASR" in html or "same key to listen" in html


def test_settings_js_saves_fish_api_key_without_wiping_empty():
    js = (ROOT / "static" / "js" / "settings.js").read_text(encoding="utf-8")
    assert "function isFish()" in js
    assert "fish_api_key" in js
    assert "if (!key)" in js
    assert "key.length < 24" in js
    assert "s2.1-pro-free" in js
    assert "chatterbox" in js


def test_settings_js_lists_chatterbox_endpoint_as_tts():
    js = (ROOT / "static" / "js" / "settings.js").read_text(encoding="utf-8")
    assert "chatterbox-tts" in js
    assert "ttsKeywords" in js
    assert "'chatterbox'" in js or '"chatterbox"' in js
