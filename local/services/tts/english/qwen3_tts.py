"""Qwen3-TTS English text-to-speech.

Uses Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign for natural English speech.
Install: pip install qwen-tts
"""

import os
from typing import Optional, Generator

import numpy as np

NATIVE_SAMPLE_RATE = 24000

TTS_ENGLISH_MODEL = os.getenv(
    "TTS_ENGLISH_MODEL", "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign"
)
TTS_DEVICE = os.getenv("TTS_DEVICE", "cuda:0")
TTS_VOICE_INSTRUCT = os.getenv(
    "TTS_VOICE_INSTRUCT",
    "A calm, professional male speaker with a clear and measured tone, "
    "suitable for an interview setting.",
)

_model = None


def load_model(model_name: Optional[str] = None, device: Optional[str] = None):
    """Load Qwen3-TTS VoiceDesign model."""
    global _model

    if _model is not None:
        return _model

    name = model_name or TTS_ENGLISH_MODEL
    dev = device or TTS_DEVICE

    try:
        import torch
        from qwen_tts import Qwen3TTSModel

        dtype = torch.bfloat16 if "cuda" in dev else torch.float32
        _model = Qwen3TTSModel.from_pretrained(
            name,
            device_map=dev,
            dtype=dtype,
        )
        return _model
    except ImportError:
        raise RuntimeError("qwen-tts is required. Install with: pip install qwen-tts")
    except Exception as e:
        raise RuntimeError(f"Failed to load Qwen3-TTS: {e}")


def synthesize(text: str, sample_rate: int = 24000) -> np.ndarray:
    """Synthesize English speech from text.

    Args:
        text: English text to synthesize
        sample_rate: Ignored (Qwen3-TTS controls its own sample rate)

    Returns:
        numpy array of audio samples (float32)
    """
    if _model is None:
        raise RuntimeError("TTS model not loaded. Call load_model() first.")

    wavs, sr = _model.generate_voice_design(
        text=text,
        instruct=TTS_VOICE_INSTRUCT,
        language="English",
    )

    audio = np.array(wavs[0], dtype=np.float32)
    return audio


def synthesize_streaming(text: str, chunk_size: int = 4800) -> Generator[np.ndarray, None, None]:
    """Synthesize speech and yield audio chunks for streaming.

    Args:
        text: English text to synthesize
        chunk_size: Number of samples per chunk

    Yields:
        numpy arrays of audio chunks
    """
    audio = synthesize(text)
    for i in range(0, len(audio), chunk_size):
        yield audio[i:i + chunk_size]


def is_loaded() -> bool:
    return _model is not None


def unload_model():
    global _model
    _model = None
