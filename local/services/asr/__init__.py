"""ASR service: language-aware speech recognition.

Dispatches to Pingala V1 Universal (primary) or Vakyansh Wav2Vec2 (Hindi fallback).
"""

import logging

_logger = logging.getLogger(__name__)


def get_asr_for_language(language: str = "en"):
    """Get the appropriate ASR module for the given language.

    Args:
        language: "en" for English/universal (Pingala), "hi" for Hindi.

    Returns:
        The ASR module. For Hindi, tries Pingala first, falls back to Vakyansh.
    """
    if language == "hi":
        try:
            from .pingala import model_loader
            if model_loader.is_loaded() or model_loader.load_model():
                return model_loader
        except Exception as e:
            _logger.warning("Pingala ASR unavailable for Hindi: %s", e)

        try:
            from .vakyansh_fallback import hindi_asr
            return hindi_asr
        except Exception as e:
            _logger.warning("Vakyansh ASR fallback also unavailable: %s", e)
            raise RuntimeError("No Hindi ASR backend available") from e

    # English / universal — use Pingala
    from .pingala import model_loader
    return model_loader