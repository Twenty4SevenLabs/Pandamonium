"""Organic sphere must ship the texture the mesh loader waits on."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LENNA = ROOT / "static" / "vendor" / "organic-sphere" / "assets" / "lenna.png"


def test_organic_sphere_texture_exists():
    assert LENNA.is_file(), "Voice Orb 3D mesh never mounts without assets/lenna.png"
    magic = LENNA.read_bytes()[:8]
    assert magic == b"\x89PNG\r\n\x1a\n"


def test_jarvis_voice_taps_analyser_into_destination():
    source = (ROOT / "static" / "js" / "jarvisVoice.js").read_text(encoding="utf-8")
    assert "function connectMeter(" in source
    assert "silent: ctx.destination" not in source
    assert "createMediaStreamDestination" not in source
    assert "silent.gain.value = 0" in source
    assert "analyser.connect(silent)" in source
    assert "track.clone()" not in source
    assert "startCaptureProbe" not in source
    assert "CHUNK_VOICE_BYTES = 1000" in source
    assert "function applyRecorderChunk(" in source
    assert "function pauseCaptureForSpeech(" in source
    assert "SPHERE_IDLE_LEVELS" in source
    assert "async function interruptAndListen(" in source
    assert "getUserMedia({ audio: true })" not in source
    assert "echoCancellation: false" in source
    assert "echoCancellation: true" not in source
    assert "orb.style.transform" in source
    assert "__jarvisSphereBridge" in source
    assert "bridge.ready" in source
    assert "postMessage({" in source and ", '*')" in source
    assert "browserText" in source
    assert "await ctx.resume()" in source
    assert "encodeWavPcm16" in source
    assert "startPcmCapture" in source
    assert "capturePeakRms" in source
    assert "VOICE_SILENCE_MS = 1600" in source
    assert "SPHERE_IDLE_VOLUME = 0" in source
    assert "BARGE_IN_BYTES" not in source
    assert "BARGE_RMS_THRESHOLD" in source
    assert "BARGE_RMS_RATIO" in source
    assert "function bargeEnergyDecision(" in source
    assert "armCaptureMeter(" in source
    assert "MAX_TURN_MS = 5 * 60 * 1000" in source
    assert "ready: talking" in source
    assert "audioWorklet.addModule" in source
    assert "t*=.45" not in source  # that lives in the sphere bundle
    assert "MIN_TRANSCRIPT_CHARS" in source
    assert "MIN_RECORDING_BYTES" in source


def test_organic_sphere_honors_parent_ready_flag():
    bundle = (
        ROOT / "static" / "vendor" / "organic-sphere" / "bundle.a58026fa81805d03e449.jarvis-fullscreen-v5.js"
    ).read_text(encoding="utf-8")
    assert 'if("jarvis-audio-levels"===e.type)' in bundle
    assert "this.ready=!0,this.state=e.state" not in bundle
    assert "this.ready=!1,this.volume=0" in bundle
    assert "null==e.ready" in bundle
    assert "t*=.45" in bundle
    assert "this.variations.volume.getDefault=()=>0" in bundle
    assert "this.variations.highLevel.getDefault=()=>0" in bundle
    assert "this.variations.mediumLevel.getDefault=()=>1" in bundle
    assert "uDisplacementStrength:{value:0}" in bundle
    assert "uDistortionStrength:{value:0}" in bundle
    assert "getDefault=()=>3.587" not in bundle
    assert "return.35*Math.max(t,e,n)" in bundle
