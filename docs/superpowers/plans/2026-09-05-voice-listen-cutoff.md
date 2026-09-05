# Voice listen cutoff and barge-in

1. Fail tests that still expect `MAX_TURN_MS = 8000`, `VOICE_SILENCE_MS = 450`, and `echoCancellation: true`.
2. Open the call mic with `echoCancellation: false`; stop toggling AEC via `applyConstraints`.
3. Silence hangover 1600ms; max listen 5 minutes.
4. Keep 8s of barge audio on interrupt.
5. Bump SW cache to `pandamonium-v391`, copy static files into the live container.
