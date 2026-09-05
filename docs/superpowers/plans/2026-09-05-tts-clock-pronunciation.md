# TTS clock pronunciation

Expand digital clocks in `speech_text()` before Chatterbox so `2:51 AM` is spoken as "two fifty-one AM", not "two point five one".

## Steps

1. Add `expand_spoken_clocks` in `src/voice_pcm.py`; call it from `speech_text()`.
2. Cover colon, dotted, 24-hour, o'clock, oh-minutes, and UTC-offset non-matches in `tests/test_voice_pcm_stream.py`.
3. Ship `voice_pcm.py` into the live container and restart only `pandamonium-pandamonium-1`.
