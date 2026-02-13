"""ASR model loader — faster-whisper (CTranslate2).

Uses faster-whisper for memory-efficient multilingual ASR.
Only ~2-3GB VRAM vs ~7GB for the transformers backend,
leaving room for TTS on the same GPU.
"""

import os
from typing import Optional

ASR_MODEL_PATH = os.getenv("ASR_MODEL_PATH", "medium")
ASR_DEVICE = os.getenv("ASR_DEVICE", "cuda")
ASR_COMPUTE_TYPE = os.getenv("ASR_COMPUTE_TYPE", "float16")

_transcriber = None


def load_model(
    model_path: Optional[str] = None,
    device: Optional[str] = None,
    compute_type: Optional[str] = None,
):
    """Load the faster-whisper ASR model.

    Returns the WhisperModel instance.
    """
    global _transcriber

    if _transcriber is not None:
        return _transcriber

    path = model_path or ASR_MODEL_PATH
    dev = device or ASR_DEVICE
    ct = compute_type or ASR_COMPUTE_TYPE

    try:
        from faster_whisper import WhisperModel

        _transcriber = WhisperModel(
            path,
            device=dev,
            compute_type=ct,
        )
        return _transcriber
    except ImportError:
        raise RuntimeError(
            "faster-whisper is required. Install with: pip install faster-whisper"
        )
    except Exception as e:
        raise RuntimeError(f"Failed to load faster-whisper model '{path}': {e}")


def get_transcriber():
    """Get the loaded transcriber (load if not already loaded)."""
    global _transcriber
    if _transcriber is None:
        load_model()
    return _transcriber


def unload_model():
    """Unload the model to free memory."""
    global _transcriber
    _transcriber = None


def is_loaded() -> bool:
    """Check if the model is currently loaded."""
    return _transcriber is not None
