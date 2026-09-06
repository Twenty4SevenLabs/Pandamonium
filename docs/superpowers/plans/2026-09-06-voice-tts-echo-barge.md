# Voice Orb TTS echo barge-in

1. Raise barge floor to `0.045`, voiced window to `550ms`, grace to `900ms` so a `0.031` Chatterbox headset leak does not interrupt.
2. Keep barge baseline/grace across TTS chunks (`resetArm: false`).
3. Drop Whisper transcripts that match `lastSpokenPlain`.
4. Bump SW cache to `pandamonium-v392` and copy static files into `pandamonium-pandamonium-1`.
5. Do not change Chatterbox `:8030` or Unsloth endpoints.
