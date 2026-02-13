"""TTS service: language-aware text-to-speech synthesis."""

import logging

_logger = logging.getLogger(__name__)


def get_tts_for_language(language: str):
    """Get the appropriate TTS module for the given language.

    Args:
        language: "en" for English (Qwen3-TTS), "hi" for Hindi (Parler-TTS)

    Returns:
        The TTS module with synthesize() and synthesize_streaming() functions.
    """
    # On GPUs with limited VRAM (<=8GB), running ASR + a neural TTS
    # simultaneously causes cuDNN conflicts or OOM.  Use pyttsx3 (Windows
    # SAPI5) which is instant and conflict-free.  To use the neural TTS
    # models instead, set TTS_BACKEND=neural in your .env.
    import os
    if os.getenv("TTS_BACKEND", "sapi5") == "neural":
        if language == "hi":
            try:
                from .hindi import parler_tts
                return parler_tts
            except Exception as e:
                _logger.warning("Parler-TTS unavailable, falling back to pyttsx3: %s", e)
        else:
            try:
                from .english import qwen3_tts
                return qwen3_tts
            except Exception as e:
                _logger.warning("Qwen3-TTS unavailable, falling back to pyttsx3: %s", e)

    from .fallback import espeak
    return espeak
