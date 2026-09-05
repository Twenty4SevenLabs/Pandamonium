# Voice listen cutoff and barge-in

Session `7e4f9647` (2026-09-05 ~07:59–08:01 UTC). Time pronunciation was already fixed. This session’s remaining failures are listen-turn policy and AEC.

## Evidence

- Whisper clips are 7.5–9.9s. Transcripts end mid-sentence (`I'm trying to talk at the same level just to see if you're`). `MAX_TURN_MS = 8000` is a hard stop while the user is still speaking.
- `VOICE_SILENCE_MS = 450` ends a turn on a brief RMS dip.
- During TTS (`barge=True`) analyser RMS stays `0.0001–0.0004` while the user talks over the agent. `applyConstraints({ echoCancellation: false })` after `getUserMedia` does not disable Chrome AEC. MDN: `applyConstraints` replaces the constraint set, but Chrome still cancels local playback (`echoCancellation: true` / `"all"`) unless the track is opened with AEC off.
- Topology: headset playback + `Default - External Microphone (Realtek(R) Audio)`. AEC over-suppresses the desk mic during TTS.
- Successful interrupts then `trimListenChunksToTail(2000)` and re-enable AEC, so the next prompt is a 2–4s fragment (`which I'm visiting Tokyo.`).
- Agent `timeout=300` is the LLM HTTP timeout (5 minutes), not the mic. The mic was dying at **8 seconds**. Safety ceiling for a listen turn is 5 minutes so Whisper does not get unbounded audio.

## Behavior

1. `getUserMedia` requests `echoCancellation: false`. Do not toggle AEC on a live track.
2. End a listen turn on **1.6s of silence**, not 450ms. Hard cap **5 minutes**, and if they are still talking at the cap wait for that silence hangover when possible.
3. On barge-in, keep ~8s of pre-interrupt audio, not 2s.
4. Headset leak still must not barge: `bargeEnergyDecision` leak-vs-speech tests stay.

Chat copy is unchanged. Spoken clocks still expand in `speech_text()`.
