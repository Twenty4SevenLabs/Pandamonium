# services/stt/stt_service.py
"""Multi-provider Speech-to-Text service — dispatches to local Whisper, OpenAI-compatible API, Fish ASR, or browser."""

import io
import logging
import os
import httpx
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

from services.tts.tts_service import FISH_API_KEY_MIN_LEN, _normalize_fish_api_key

logger = logging.getLogger(__name__)

FISH_ASR_URL = "https://api.fish.audio/v1/asr"


def _fish_asr_error_message(response) -> str:
    detail = ""
    try:
        body = response.json()
        if isinstance(body, dict):
            detail = str(body.get("message") or body.get("detail") or body.get("error") or "")
    except Exception:
        detail = (getattr(response, "text", None) or "")[:240]
    status = getattr(response, "status_code", None) or 500
    if status == 401:
        return "Fish rejected the API key while listening. Paste the full key from fish.audio/app/api-keys."
    if detail:
        return f"Fish Audio ASR failed ({status}): {detail}"
    return f"Fish Audio ASR failed ({status})"


def _normalize_transcript(text: Optional[str]) -> Optional[str]:
    if text is None:
        return None
    text = text.strip()
    return text if any(char.isalnum() for char in text) else ""


class STTService:
    """Multi-provider STT service.

    Reads provider config from data/settings.json on each call.
    Providers:
      "disabled"        — no STT
      "browser"         — client-side Web Speech API (no server transcription)
      "local"           — faster-whisper on CPU/GPU
      "fish"            — Fish Audio ASR (same API key as Fish TTS)
      "endpoint:<id>"   — OpenAI-compatible /audio/transcriptions via ModelEndpoint
    """

    def __init__(self):
        self._whisper_model = None  # lazy-init
        self._fish_asr_unpaid = False

    # ── Settings ──

    def _load_settings(self) -> dict:
        from src.settings import load_settings
        saved = load_settings()
        return {
            "stt_enabled": saved.get("stt_enabled", False),
            "stt_provider": saved.get("stt_provider", "disabled"),
            "stt_model": saved.get("stt_model", "base"),
            "stt_language": saved.get("stt_language", ""),
            "tts_provider": saved.get("tts_provider", "disabled"),
            "fish_api_key": saved.get("fish_api_key", ""),
        }

    def _fish_api_key(self, settings: dict | None = None) -> str:
        saved = settings if settings is not None else self._load_settings()
        key = _normalize_fish_api_key(str(saved.get("fish_api_key") or ""))
        if len(key) >= FISH_API_KEY_MIN_LEN:
            return key
        return _normalize_fish_api_key(os.getenv("FISH_AUDIO_API_KEY") or "")

    def _resolved_provider(self, settings: dict | None = None) -> str:
        saved = settings if settings is not None else self._load_settings()
        provider = str(saved.get("stt_provider") or "disabled")
        enabled = saved.get("stt_enabled") is not False
        if provider == "browser":
            return "browser"
        if enabled and provider not in ("disabled", "browser"):
            return provider
        if self._fish_api_key(saved) and (
            saved.get("tts_provider") == "fish" or provider == "fish"
        ):
            return "fish"
        if not enabled:
            return "disabled"
        return provider

    @property
    def available(self) -> bool:
        settings = self._load_settings()
        provider = self._resolved_provider(settings)
        if provider == "disabled":
            return False
        if provider == "browser":
            return True  # handled client-side
        if provider == "local":
            return self._get_whisper() is not None
        if provider == "fish":
            return bool(self._fish_api_key(settings))
        if isinstance(provider, str) and provider.startswith("endpoint:"):
            return True  # assume reachable
        return False

    # ── Local Whisper ──

    def _get_whisper(self):
        if self._whisper_model is None:
            try:
                from faster_whisper import WhisperModel
            except ImportError:
                logger.warning("faster-whisper not installed. Install with: pip install faster-whisper")
                return None
            try:
                settings = self._load_settings()
                model_size = settings.get("stt_model", "base")
                # faster-whisper runs on CTranslate2, not torch. torch is only
                # used (optionally) to detect a CUDA device for acceleration —
                # if it's missing or unusable we just run on CPU. Keeping this
                # probe separate (and tolerant of any failure, e.g. a broken
                # CUDA/torch install that raises OSError on import) means a
                # torch-less or torch-broken machine still does CPU
                # transcription instead of failing with a misleading
                # "faster-whisper not installed" error.
                try:
                    import torch
                    use_cuda = torch.cuda.is_available()
                except Exception:
                    use_cuda = False
                device = "cuda" if use_cuda else "cpu"
                compute_type = "float16" if device == "cuda" else "int8"
                self._whisper_model = WhisperModel(model_size, device=device, compute_type=compute_type)
                logger.info(f"faster-whisper model '{model_size}' loaded on {device}")
            except Exception as e:
                logger.error(f"Failed to load whisper model: {e}")
                return None
        return self._whisper_model

    def preload(self) -> None:
        """Load Whisper at startup so the first voice turn is not a cold download."""
        self._get_whisper()

    def _transcribe_local(self, audio_bytes: bytes, language: str = "") -> Optional[str]:
        model = self._get_whisper()
        if not model:
            return None
        tmp_path = None
        try:
            # Write to temp file (faster-whisper needs a file path or file-like)
            suffix = ".wav" if audio_bytes[:4] == b"RIFF" else ".webm"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name

            kwargs = {
                "beam_size": 1,
                "vad_filter": True,
                "condition_on_previous_text": False,
                "vad_parameters": {
                    "threshold": 0.35,
                    "min_speech_duration_ms": 250,
                    "min_silence_duration_ms": 400,
                    "speech_pad_ms": 200,
                },
            }
            if language:
                kwargs["language"] = language

            segments, info = model.transcribe(tmp_path, **kwargs)
            text = " ".join(seg.text.strip() for seg in segments)
            duration_after_vad = float(getattr(info, "duration_after_vad", 0) or 0)
            if not text.strip():
                if duration_after_vad < 0.25:
                    logger.info(
                        "Local STT skip no-VAD retry (silence) bytes=%s vad=%.2f lang=%s",
                        len(audio_bytes),
                        duration_after_vad,
                        getattr(info, "language", ""),
                    )
                    return ""
                kwargs["vad_filter"] = False
                kwargs.pop("vad_parameters", None)
                segments, info = model.transcribe(tmp_path, **kwargs)
                text = " ".join(seg.text.strip() for seg in segments)
                logger.info("Local STT retry without VAD: %s chars", len(text))

            logger.info(f"Local STT: {len(text)} chars, lang={info.language}, prob={info.language_probability:.2f}")
            return text
        except Exception as e:
            logger.error(f"Local STT transcription failed: {e}", exc_info=True)
            return None
        finally:
            if tmp_path:
                Path(tmp_path).unlink(missing_ok=True)

    # ── API endpoint ──

    def _transcribe_api(self, audio_bytes: bytes, endpoint_id: str, model: str, language: str = "") -> Optional[str]:
        from src.database import SessionLocal, ModelEndpoint

        db = SessionLocal()
        try:
            ep = db.query(ModelEndpoint).filter(ModelEndpoint.id == endpoint_id).first()
            if not ep:
                logger.error(f"STT endpoint {endpoint_id} not found")
                return None
            base_url = ep.base_url.rstrip("/")
            api_key = ep.api_key
        finally:
            db.close()

        url = base_url + "/audio/transcriptions"
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        files = {"file": ("audio.webm", io.BytesIO(audio_bytes), "audio/webm")}
        data = {"model": model or "whisper-1"}
        if language:
            data["language"] = language

        try:
            r = httpx.post(url, headers=headers, files=files, data=data, timeout=60)
            r.raise_for_status()
            result = r.json()
            text = result.get("text", "")
            logger.info(f"API STT: {len(text)} chars from {base_url}")
            return text
        except Exception as e:
            logger.error(f"API STT transcription failed: {e}")
            return None

    def _transcribe_fish(self, audio_bytes: bytes, language: str = "") -> Optional[str]:
        api_key = self._fish_api_key()
        if not api_key:
            raise RuntimeError("No Fish Audio API key. Paste the key in Settings → Voice.")
        if self._fish_asr_unpaid:
            local = self._transcribe_local(audio_bytes, language)
            if local:
                return local
            logger.warning("Fish ASR unpaid; local Whisper returned no text")
            return ""
        headers = {"Authorization": f"Bearer {api_key}"}
        is_wav = audio_bytes[:4] == b"RIFF"
        filename = "speech.wav" if is_wav else "speech.webm"
        mime = "audio/wav" if is_wav else "audio/webm"
        files = {"audio": (filename, io.BytesIO(audio_bytes), mime)}
        data = {"ignore_timestamps": "true"}
        if language:
            data["language"] = language
        try:
            timeout = float(os.getenv("PANDAMONIUM_FISH_ASR_TIMEOUT", "60"))
            response = httpx.post(
                FISH_ASR_URL,
                headers=headers,
                files=files,
                data=data,
                timeout=timeout,
            )
            if response.status_code == 402:
                self._fish_asr_unpaid = True
                logger.warning("Fish ASR returned 402 (no API credit); trying local Whisper")
                local = self._transcribe_local(audio_bytes, language)
                if local:
                    return local
                logger.warning("Fish ASR unpaid; local Whisper returned no text")
                return ""
            if response.status_code >= 400:
                raise RuntimeError(_fish_asr_error_message(response))
            try:
                payload = response.json()
            except Exception:
                payload = {}
            text = payload.get("text", "") if isinstance(payload, dict) else ""
            logger.info("Fish Audio ASR: %s chars", len(text or ""))
            return text
        except RuntimeError:
            raise
        except Exception as exc:
            logger.error("Fish Audio ASR failed: %s", exc)
            raise RuntimeError(f"Fish Audio ASR failed: {exc}") from exc

    # ── Public interface ──

    def transcribe(self, audio_bytes: bytes) -> Optional[str]:
        settings = self._load_settings()
        provider = self._resolved_provider(settings)
        model = settings["stt_model"]
        language = settings.get("stt_language", "")

        if provider in ("disabled", "browser"):
            return None

        if provider == "local":
            transcript = self._transcribe_local(audio_bytes, language)
        elif provider == "fish":
            transcript = self._transcribe_fish(audio_bytes, language)
        elif isinstance(provider, str) and provider.startswith("endpoint:"):
            endpoint_id = provider.split(":", 1)[1]
            transcript = self._transcribe_api(audio_bytes, endpoint_id, model, language)
        else:
            logger.error(f"Unknown STT provider: {provider}")
            return None
        return _normalize_transcript(transcript)

    def get_stats(self) -> Dict[str, Any]:
        settings = self._load_settings()
        provider = self._resolved_provider(settings)
        stats = {
            "available": self.available,
            "provider": provider,
            "model": settings["stt_model"],
            "language": settings.get("stt_language", ""),
        }

        if provider == "local":
            whisper = self._get_whisper()
            stats["model_loaded"] = whisper is not None
        elif provider == "browser":
            stats["model"] = "Browser (Web Speech API)"
        elif provider == "fish":
            stats["model"] = "Fish Audio ASR"
        elif isinstance(provider, str) and provider.startswith("endpoint:"):
            stats["endpoint_id"] = provider.split(":", 1)[1]

        return stats


# Module-level singleton
_stt_service = None

def get_stt_service() -> STTService:
    global _stt_service
    if _stt_service is None:
        _stt_service = STTService()
    return _stt_service
