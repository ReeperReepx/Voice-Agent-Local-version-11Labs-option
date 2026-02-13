"""pyttsx3 fallback TTS.

Provides the same interface as the primary TTS modules but uses the
Windows SAPI5 engine via pyttsx3. Works fully offline.

NOTE: pyttsx3 uses Windows COM (SAPI5) which is thread-affine.
We create a fresh engine per synthesize() call so it works correctly
when called from any thread (e.g. asyncio run_in_executor).
"""

import tempfile
import os
import logging
from typing import Optional, Generator

import numpy as np

NATIVE_SAMPLE_RATE = 22050

_loaded = False
_logger = logging.getLogger(__name__)


def is_available() -> bool:
    """Check if pyttsx3 is importable."""
    try:
        import pyttsx3
        return True
    except ImportError:
        return False


def load_model(model_name: Optional[str] = None, device: Optional[str] = None) -> None:
    """Mark backend as ready (engine is created per-call for COM safety)."""
    global _loaded

    if _loaded:
        return

    if not is_available():
        raise RuntimeError("pyttsx3 is not installed")

    _loaded = True
    _logger.info("pyttsx3 (SAPI5) TTS backend ready")


def is_loaded() -> bool:
    return _loaded


def unload_model() -> None:
    global _loaded
    _loaded = False


def _make_engine():
    """Create a fresh pyttsx3 engine on the current thread."""
    import pyttsx3
    engine = pyttsx3.init()
    engine.setProperty("rate", 150)
    return engine


def synthesize(text: str, sample_rate: int = 22050) -> np.ndarray:
    """Synthesize speech using pyttsx3 (Windows SAPI5).

    Creates a fresh COM engine each call to avoid cross-thread deadlocks.

    Returns:
        NumPy float32 array of audio samples.
    """
    if not _loaded:
        raise RuntimeError("pyttsx3 backend not loaded — call load_model() first")

    import wave

    engine = _make_engine()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        engine.save_to_file(text, tmp_path)
        engine.runAndWait()
        engine.stop()

        with wave.open(tmp_path, "rb") as wf:
            frames = wf.readframes(wf.getnframes())
            width = wf.getsampwidth()

        if width == 2:
            audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
        elif width == 1:
            audio = np.frombuffer(frames, dtype=np.uint8).astype(np.float32) / 128.0 - 1.0
        else:
            audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0

        _logger.info("pyttsx3 synthesized %d samples for: %.40s...", len(audio), text)
        return audio
    finally:
        try:
            del engine
        except Exception:
            pass
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def synthesize_streaming(text: str, chunk_size: int = 4800) -> Generator[np.ndarray, None, None]:
    """Synthesize speech and yield audio chunks for streaming."""
    audio = synthesize(text)
    for i in range(0, len(audio), chunk_size):
        yield audio[i:i + chunk_size]
