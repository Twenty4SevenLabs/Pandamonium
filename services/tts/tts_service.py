# src/tts_service.py
"""Multi-provider TTS service — Kokoro, OpenAI-compatible endpoints, Fish Audio, or browser."""

import io
import wave
import logging
import hashlib
import os
import re
import httpx
from pathlib import Path
from typing import Optional, Dict, Any

from src.constants import TTS_CACHE_DIR

logger = logging.getLogger(__name__)

FISH_TTS_URL = "https://api.fish.audio/v1/tts"
FISH_MODELS_URL = "https://api.fish.audio/model"
FISH_DEFAULT_MODEL = "s2.1-pro-free"
FISH_API_KEY_MIN_LEN = 24
_FISH_LEGACY_VOICE_RE = re.compile(r"^(?:[ab][fm]_|.*_chatterbox$)", re.IGNORECASE)


class TTSError(Exception):
    """Provider synthesis failed with a user-facing message."""

    def __init__(self, message: str, status: int = 500):
        super().__init__(message)
        self.message = message
        self.status = int(status or 500)


def _normalize_fish_api_key(raw: str) -> str:
    key = (raw or "").strip()
    if key.lower().startswith("bearer "):
        key = key[7:].strip()
    if len(key) >= 2 and key[0] == key[-1] and key[0] in {'"', "'"}:
        key = key[1:-1].strip()
    return key


def _fish_usable_voice(requested: str, default: str) -> str:
    req = (requested or "").strip()
    fallback = (default or "").strip()
    if not req or _FISH_LEGACY_VOICE_RE.match(req):
        return fallback
    return req


def _fish_error_message(response: Any) -> str:
    detail = ""
    try:
        body = response.json()
        if isinstance(body, dict):
            detail = str(body.get("message") or body.get("detail") or body.get("error") or "")
    except Exception:
        detail = (getattr(response, "text", None) or "")[:240]
    status = getattr(response, "status_code", None) or 500
    if status == 401:
        return (
            "Fish rejected the API key (Invalid Token). "
            "The voice list is public and does not prove the key works. "
            "Paste the full key from fish.audio/app/api-keys, then Preview again."
        )
    if detail:
        return f"Fish Audio TTS failed ({status}): {detail}"
    return f"Fish Audio TTS failed ({status})"

KOKORO_VOICES = [
    {"id": "af_sarah", "label": "Sarah", "locale": "American English", "gender": "female"},
    {"id": "af_heart", "label": "Heart", "locale": "American English", "gender": "female"},
    {"id": "af_bella", "label": "Bella", "locale": "American English", "gender": "female"},
    {"id": "af_nicole", "label": "Nicole", "locale": "American English", "gender": "female"},
    {"id": "af_sky", "label": "Sky", "locale": "American English", "gender": "female"},
    {"id": "am_adam", "label": "Adam", "locale": "American English", "gender": "male"},
    {"id": "am_michael", "label": "Michael", "locale": "American English", "gender": "male"},
    {"id": "bf_emma", "label": "Emma", "locale": "British English", "gender": "female"},
    {"id": "bf_isabella", "label": "Isabella", "locale": "British English", "gender": "female"},
    {"id": "bm_george", "label": "George", "locale": "British English", "gender": "male"},
    {"id": "bm_lewis", "label": "Lewis", "locale": "British English", "gender": "male"},
]


def _safe_speed(value, default: float = 1.0) -> float:
    """Parse the stored tts_speed defensively. The settings layer tolerates
    corrupt/agent-written config, so a non-numeric or empty value (e.g. an agent
    setting "speech speed" = "fast", or a hand-edited settings.json) must not
    crash synthesis or the stats endpoint with a ValueError."""
    try:
        speed = float(value)
    except (TypeError, ValueError):
        return default
    return speed if speed > 0 else default


def _fish_headers(model: str, api_key: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "model": (model or FISH_DEFAULT_MODEL).strip() or FISH_DEFAULT_MODEL,
    }


def _fish_tts_body(text: str, voice: str, speed: float) -> Dict[str, Any]:
    body: Dict[str, Any] = {
        "text": text,
        "format": "wav",
        "sample_rate": 44100,
        "prosody": {"speed": speed, "volume": 0, "normalize_loudness": True},
    }
    if (voice or "").strip():
        body["reference_id"] = voice.strip()
    return body


def _parse_fish_voice_items(items: Any) -> list[dict[str, str]]:
    catalog: list[dict[str, str]] = []
    if not isinstance(items, list):
        return catalog
    for item in items:
        if not isinstance(item, dict):
            continue
        vid = str(item.get("_id") or item.get("id") or "").strip()
        if not vid:
            continue
        label = str(item.get("title") or item.get("name") or vid).strip() or vid
        catalog.append({"id": vid, "label": label})
    return catalog


class TTSService:
    """Multi-provider TTS service.

    Reads provider config from data/settings.json on each call.
    Providers:
      "disabled"        — no TTS
      "browser"         — client-side Web Speech API (no server synthesis)
      "local"           — Kokoro-82M on GPU
      "fish"            — Fish Audio S2.1 Pro (cloud TTS)
      "endpoint:<id>"   — OpenAI-compatible /audio/speech via ModelEndpoint
    """

    def __init__(self, cache_dir: str = TTS_CACHE_DIR):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._kokoro = None  # lazy-init

    # ── Settings ──

    def _load_settings(self) -> dict:
        from src.settings import load_settings
        saved = load_settings()
        return {
            "tts_enabled": saved.get("tts_enabled", True),
            "tts_provider": saved.get("tts_provider", "disabled"),
            "tts_model": saved.get("tts_model", "tts-1"),
            "tts_voice": saved.get("tts_voice", "alloy"),
            "tts_agent_voices": saved.get("tts_agent_voices", {}),
            "tts_speed": saved.get("tts_speed", "1"),
            "fish_api_key": saved.get("fish_api_key", ""),
        }

    @property
    def available(self) -> bool:
        settings = self._load_settings()
        if settings.get("tts_enabled") is False:
            return False
        provider = settings["tts_provider"]
        if provider == "disabled":
            return False
        if provider == "browser":
            return True  # handled client-side
        if provider == "local":
            kokoro = self._get_kokoro()
            return kokoro is not None and kokoro.available
        if provider == "fish":
            return bool(self._fish_api_key(settings))
        if isinstance(provider, str) and provider.startswith("endpoint:"):
            return True  # assume reachable; errors surface at synthesis time
        return False

    # ── Cache ──

    def _cache_key(self, text: str, provider: str, model: str, voice: str, speed: float = 1.0) -> str:
        raw = f"{provider}|{model}|{voice}|{speed}|{text}"
        if provider == "fish":
            raw = f"{raw}|wav"
        return hashlib.sha256(raw.encode()).hexdigest()

    def _get_cached(self, key: str) -> Optional[bytes]:
        for ext in (".mp3", ".wav"):
            path = self.cache_dir / f"{key}{ext}"
            if path.exists():
                return path.read_bytes()
        return None

    def _put_cache(self, key: str, data: bytes):
        ext = ".mp3" if (len(data) >= 3 and (data[:3] == b'ID3' or (data[0] == 0xff and (data[1] & 0xe0) == 0xe0))) else ".wav"
        (self.cache_dir / f"{key}{ext}").write_bytes(data)

    def clear_cache(self):
        count = 0
        for f in self.cache_dir.glob("*.*"):
            f.unlink()
            count += 1
        logger.info(f"Cleared {count} cached TTS files")

    # ── Kokoro (local) ──

    def _get_kokoro(self):
        if self._kokoro is None:
            self._kokoro = _KokoroPipeline()
        return self._kokoro

    # ── API endpoint ──

    def _synthesize_api(self, text: str, endpoint_id: str, model: str, voice: str, speed: float = 1.0) -> Optional[bytes]:
        from src.database import SessionLocal, ModelEndpoint

        db = SessionLocal()
        try:
            ep = db.query(ModelEndpoint).filter(ModelEndpoint.id == endpoint_id).first()
            if not ep:
                logger.error(f"TTS endpoint {endpoint_id} not found")
                return None
            base_url = ep.base_url.rstrip("/")
            api_key = ep.api_key
        finally:
            db.close()

        url = base_url + "/audio/speech"
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        payload = {
            "model": model,
            "input": text,
            "voice": voice,
            "response_format": "wav",
            "speed": speed,
        }

        try:
            timeout = float(os.getenv("ODYSSEUS_TTS_ENDPOINT_TIMEOUT", "180"))
            r = httpx.post(url, json=payload, headers=headers, timeout=timeout)
            r.raise_for_status()
            logger.info(f"API TTS: {len(r.content)} bytes from {base_url}")
            return r.content
        except Exception as e:
            logger.error(f"API TTS synthesis failed: {e}")
            return None

    def _fish_api_key(self, settings: dict | None = None) -> str:
        saved = settings if settings is not None else self._load_settings()
        key = _normalize_fish_api_key(str(saved.get("fish_api_key") or ""))
        if key:
            return key
        return _normalize_fish_api_key(os.getenv("FISH_AUDIO_API_KEY") or "")

    def _synthesize_fish(
        self,
        text: str,
        model: str,
        voice: str,
        speed: float,
        settings: dict | None = None,
    ) -> Optional[bytes]:
        api_key = self._fish_api_key(settings)
        if not api_key:
            raise TTSError(
                "No Fish Audio API key. Click the API key field and paste the full key from fish.audio/app/api-keys.",
                status=401,
            )
        if len(api_key) < FISH_API_KEY_MIN_LEN:
            raise TTSError(
                "That Fish API key is too short. Paste the full key from fish.audio/app/api-keys — "
                "the public voice list does not mean the key is valid.",
                status=401,
            )
        headers = _fish_headers(model, api_key)
        payload = _fish_tts_body(text, voice, speed)
        try:
            timeout = float(os.getenv("PANDAMONIUM_FISH_TTS_TIMEOUT", "180"))
            r = httpx.post(FISH_TTS_URL, json=payload, headers=headers, timeout=timeout)
            if r.status_code >= 400:
                raise TTSError(_fish_error_message(r), status=r.status_code)
            logger.info("Fish Audio TTS: %s bytes", len(r.content))
            return r.content
        except TTSError:
            raise
        except Exception as e:
            logger.error("Fish Audio TTS synthesis failed: %s", e)
            raise TTSError(f"Fish Audio TTS failed: {e}", status=502) from e

    def _list_fish_voices(self) -> list[dict[str, str]]:
        api_key = self._fish_api_key()
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        merged: list[dict[str, str]] = []
        seen: set[str] = set()
        queries = []
        if api_key:
            queries.append({"self": True, "page_size": 50, "page_number": 1})
        queries.append({"page_size": 50, "page_number": 1, "sort_by": "score"})
        for params in queries:
            try:
                response = httpx.get(FISH_MODELS_URL, headers=headers, params=params, timeout=15)
                response.raise_for_status()
                payload = response.json()
                items = payload.get("items") if isinstance(payload, dict) else []
            except Exception as exc:
                logger.warning("Fish Audio voice list failed: %s", str(exc)[:160])
                continue
            for voice in _parse_fish_voice_items(items):
                if voice["id"] in seen:
                    continue
                seen.add(voice["id"])
                merged.append(voice)
        return merged

    # ── Public interface ──

    def synthesize(
        self,
        text: str,
        use_cache: bool = True,
        model: str | None = None,
        voice: str | None = None,
        speed: float | str | None = None,
    ) -> Optional[bytes]:
        settings = self._load_settings()
        if settings.get("tts_enabled") is False:
            return None
        provider = settings["tts_provider"]
        model = model or settings["tts_model"]
        voice = voice or settings["tts_voice"]
        if provider == "fish":
            voice = _fish_usable_voice(voice, settings.get("tts_voice") or "")
        speed = _safe_speed(speed if speed is not None else settings.get("tts_speed", "1"))

        if provider in ("disabled", "browser"):
            return None

        if len(text) > 5000:
            text = text[:5000]

        if use_cache:
            key = self._cache_key(text, provider, model, voice, speed)
            cached = self._get_cached(key)
            if cached:
                logger.info(f"TTS cache hit ({len(text)} chars)")
                return cached

        audio_data = None

        if provider == "local":
            kokoro = self._get_kokoro()
            if kokoro and kokoro.available:
                audio_data = kokoro.synthesize_raw(text, voice)
            else:
                logger.warning("Kokoro TTS not available")
                return None
        elif provider == "fish":
            audio_data = self._synthesize_fish(text, model, voice, speed, settings)
        elif isinstance(provider, str) and provider.startswith("endpoint:"):
            endpoint_id = provider.split(":", 1)[1]
            audio_data = self._synthesize_api(text, endpoint_id, model, voice, speed)
        else:
            logger.error(f"Unknown TTS provider: {provider}")
            return None

        if audio_data and use_cache:
            key = self._cache_key(text, provider, model, voice, speed)
            self._put_cache(key, audio_data)

        return audio_data

    def synthesize_to_base64(
        self,
        text: str,
        model: str | None = None,
        voice: str | None = None,
        speed: float | str | None = None,
        use_cache: bool = True,
    ) -> Optional[str]:
        import base64
        audio = self.synthesize(text, use_cache=use_cache, model=model, voice=voice, speed=speed)
        if audio:
            return base64.b64encode(audio).decode("utf-8")
        return None

    def list_voices(self) -> list[dict[str, str]]:
        settings = self._load_settings()
        provider = str(settings.get("tts_provider") or "")
        if provider == "fish":
            catalog = self._list_fish_voices()
            if catalog:
                return catalog
            return []
        if provider.startswith("endpoint:"):
            endpoint_id = provider.split(":", 1)[1]
            from src.database import SessionLocal, ModelEndpoint

            db = SessionLocal()
            try:
                endpoint = db.query(ModelEndpoint).filter(ModelEndpoint.id == endpoint_id).first()
                base_url = str(getattr(endpoint, "base_url", "") or "").rstrip("/")
                api_key = str(getattr(endpoint, "api_key", "") or "")
            finally:
                db.close()
            if base_url:
                headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
                catalog = []
                last_exc = None
                for suffix in ("/voices", "/audio/voices"):
                    try:
                        response = httpx.get(f"{base_url}{suffix}", headers=headers, timeout=5)
                        response.raise_for_status()
                        voices = response.json().get("voices") or []
                        catalog = [
                            {
                                "id": str(voice.get("id") or "").strip(),
                                "label": str(voice.get("label") or voice.get("id") or "").strip(),
                            }
                            for voice in voices
                            if isinstance(voice, dict)
                            and voice.get("id")
                            and voice.get("available", True) is not False
                        ]
                        if catalog:
                            return catalog
                    except Exception as exc:
                        last_exc = exc
                        continue
                if last_exc is not None:
                    logger.warning(
                        "Could not list voices from TTS endpoint %s: %s",
                        endpoint_id,
                        str(last_exc)[:160],
                    )
        return list(KOKORO_VOICES)

    def set_voice(self, voice: str):
        """Legacy no-op — voice is now managed via admin settings."""

    def get_stats(self) -> Dict[str, Any]:
        settings = self._load_settings()
        provider = settings["tts_provider"]
        tts_enabled = settings.get("tts_enabled", True)

        cache_files = list(self.cache_dir.glob("*.wav")) + list(self.cache_dir.glob("*.mp3"))
        cache_size = sum(f.stat().st_size for f in cache_files)

        is_available = self.available and tts_enabled
        stats = {
            "available": is_available,
            "ready": is_available,
            "provider": provider,
            "model": settings["tts_model"],
            "voice": settings["tts_voice"],
            "speed": _safe_speed(settings.get("tts_speed", "1")),
            "cache_entries": len(cache_files),
            "cache_size_mb": round(cache_size / (1024 * 1024), 2),
        }

        if provider == "local":
            kokoro = self._get_kokoro()
            stats["model"] = "Kokoro-82M (GPU)" if (kokoro and kokoro.available) else "Kokoro (not loaded)"
        elif provider == "browser":
            stats["model"] = "Browser (Web Speech API)"
        elif provider == "fish":
            stats["model"] = settings.get("tts_model") or FISH_DEFAULT_MODEL
            stats["key_configured"] = bool(self._fish_api_key(settings))
        elif isinstance(provider, str) and provider.startswith("endpoint:"):
            stats["endpoint_id"] = provider.split(":", 1)[1]

        return stats


class _KokoroPipeline:
    """Encapsulates the Kokoro-82M local GPU pipeline."""

    def __init__(self):
        self.pipeline = None
        self.available = False
        self.device = None
        self._init()

    def _init(self):
        try:
            import torch
            from kokoro import KPipeline

            if not torch.cuda.is_available():
                logger.warning("CUDA not available for Kokoro TTS")
                return

            self.device = torch.device("cuda:0")
            with torch.cuda.device(0):
                self.pipeline = KPipeline(lang_code="a")
                if hasattr(self.pipeline, "model"):
                    self.pipeline.model = self.pipeline.model.to(self.device)
            self.available = True
            logger.info("Kokoro-82M TTS pipeline loaded")
        except ImportError as e:
            logger.warning(f"Kokoro TTS not available: {e}")
            logger.warning("Install with: pip install kokoro soundfile")
        except Exception as e:
            logger.error(f"Kokoro init failed: {e}", exc_info=True)

    def synthesize_raw(self, text: str, voice: str = "af_heart") -> Optional[bytes]:
        if not self.available:
            return None
        try:
            import torch
            import numpy as np

            with torch.cuda.device(self.device):
                chunks = []
                for _, _, audio in self.pipeline(text, voice=voice):
                    chunks.append(audio)

            if not chunks:
                return None

            full = np.concatenate(chunks)
            buf = io.BytesIO()
            with wave.open(buf, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(24000)
                wf.writeframes((full * 32767).astype(np.int16).tobytes())
            return buf.getvalue()
        except Exception as e:
            logger.error(f"Kokoro synthesis failed: {e}", exc_info=True)
            return None


# Module-level singleton
_tts_service = None

def get_tts_service() -> TTSService:
    global _tts_service
    if _tts_service is None:
        _tts_service = TTSService()
    return _tts_service
