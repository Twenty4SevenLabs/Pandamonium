# TTS clock pronunciation

Chatterbox reads `2:51 AM` as "two point five one AM" because a colon is treated like a decimal. Chat copy can keep digital clocks. Spoken text must expand them before TTS.

## Behavior

`speech_text()` in `src/voice_pcm.py` rewrites clock patterns after Markdown cleanup:

- `2:51 AM` / `2.51 AM` / `2:51 a.m.` → `two fifty-one AM`
- `2:00 PM` → `two o'clock PM`
- `9:05` → `nine oh five`
- `14:30` → `two thirty PM`
- `00:15` → `twelve fifteen AM`

Do not rewrite UTC offsets (`UTC-05:00`), ISO `T` times, or URL ports (URLs are stripped first).
