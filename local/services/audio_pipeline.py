"""Audio utilities for the WebSocket voice pipeline.

Handles format conversion, resampling, TTS synthesis, and chunking.
"""

import logging

import numpy as np

logger = logging.getLogger(__name__)


def pcm16_to_float32(pcm_bytes: bytes) -> np.ndarray:
    """Convert raw PCM16 bytes to float32 numpy array.

    Args:
        pcm_bytes: Raw 16-bit signed integer PCM audio bytes.

    Returns:
        numpy float32 array normalised to [-1.0, 1.0].
    """
    return np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0


def float32_to_pcm16(audio: np.ndarray) -> bytes:
    """Convert float32 numpy array to raw PCM16 bytes.

    Args:
        audio: numpy float32 array in [-1.0, 1.0].

    Returns:
        Raw bytes of 16-bit signed integer PCM.
    """
    clipped = np.clip(audio, -1.0, 1.0)
    return (clipped * 32767).astype(np.int16).tobytes()


def resample_audio(audio: np.ndarray, orig_sr: int, target_sr: int = 24000) -> np.ndarray:
    """Resample audio using numpy linear interpolation.

    Args:
        audio: Input float32 audio array.
        orig_sr: Original sample rate.
        target_sr: Target sample rate (default 24kHz).

    Returns:
        Resampled float32 audio array.
    """
    if orig_sr == target_sr:
        return audio

    duration = len(audio) / orig_sr
    target_len = int(duration * target_sr)
    if target_len == 0:
        return np.array([], dtype=np.float32)

    indices = np.linspace(0, len(audio) - 1, target_len)
    return np.interp(indices, np.arange(len(audio)), audio).astype(np.float32)


def synthesize_and_normalize(text: str, language: str, target_sr: int = 24000) -> bytes:
    """Synthesize speech with TTS, resample to target_sr, return PCM16 bytes.

    Args:
        text: Text to synthesize.
        language: "en" or "hi" — selects the TTS engine.
        target_sr: Output sample rate (default 24kHz for browser playback).

    Returns:
        PCM16 bytes at target_sr.
    """
    from services.tts import get_tts_for_language

    tts_module = get_tts_for_language(language)

    # Ensure the TTS model is loaded
    if not tts_module.is_loaded():
        logger.info("Loading TTS model for language=%s", language)
        tts_module.load_model()

    # Get native sample rate from the TTS module
    native_sr = getattr(tts_module, "NATIVE_SAMPLE_RATE", target_sr)

    audio = tts_module.synthesize(text)

    # Resample if needed
    if native_sr != target_sr:
        audio = resample_audio(audio, native_sr, target_sr)

    return float32_to_pcm16(audio)


def chunk_pcm_bytes(pcm: bytes, chunk_size: int = 4800) -> list[bytes]:
    """Split PCM16 bytes into fixed-size chunks for streaming.

    Each sample is 2 bytes (int16), so chunk_size is in *samples*.
    Default 4800 samples = 200ms at 24kHz.

    Args:
        pcm: Raw PCM16 bytes.
        chunk_size: Number of samples per chunk.

    Returns:
        List of byte chunks.
    """
    byte_chunk = chunk_size * 2  # 2 bytes per int16 sample
    return [pcm[i:i + byte_chunk] for i in range(0, len(pcm), byte_chunk)]
