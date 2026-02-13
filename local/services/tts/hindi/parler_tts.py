"""Parler-TTS Hindi text-to-speech.

Uses parler-tts/parler-tts-mini-v1 for Hindi speech synthesis.
Install: pip install git+https://github.com/huggingface/parler-tts.git
"""

import os
from typing import Optional, Generator

import numpy as np

NATIVE_SAMPLE_RATE = 44100

TTS_HINDI_MODEL = os.getenv("TTS_HINDI_MODEL", "parler-tts/parler-tts-mini-v1")
TTS_DEVICE = os.getenv("TTS_DEVICE", "cuda")
TTS_VOICE_DESCRIPTION = os.getenv(
    "TTS_VOICE_DESCRIPTION",
    "A calm, clear female speaker with a moderate speed and natural tone. "
    "The recording is of high quality with the speaker's voice sounding professional.",
)

_model = None
_tokenizer = None


def load_model(model_name: Optional[str] = None, device: Optional[str] = None):
    """Load Parler-TTS model and tokenizer."""
    global _model, _tokenizer

    if _model is not None:
        return _model, _tokenizer

    name = model_name or TTS_HINDI_MODEL
    dev = device or TTS_DEVICE

    try:
        import torch
        from parler_tts import ParlerTTSForConditionalGeneration
        from transformers import AutoTokenizer

        _tokenizer = AutoTokenizer.from_pretrained(name)
        _model = ParlerTTSForConditionalGeneration.from_pretrained(name).to(dev)
        return _model, _tokenizer
    except ImportError:
        raise RuntimeError(
            "parler-tts is required. Install with: "
            "pip install git+https://github.com/huggingface/parler-tts.git"
        )
    except Exception as e:
        raise RuntimeError(f"Failed to load Parler-TTS: {e}")


def synthesize(text: str, sample_rate: int = 24000) -> np.ndarray:
    """Synthesize Hindi speech from text.

    Args:
        text: Hindi text (Devanagari or romanized)
        sample_rate: Ignored (Parler-TTS uses its own config sample rate)

    Returns:
        numpy array of audio samples (float32)
    """
    if _model is None:
        raise RuntimeError("Hindi TTS model not loaded. Call load_model() first.")

    import torch

    input_ids = _tokenizer(TTS_VOICE_DESCRIPTION, return_tensors="pt").input_ids.to(
        _model.device
    )
    prompt_input_ids = _tokenizer(text, return_tensors="pt").input_ids.to(
        _model.device
    )

    with torch.no_grad():
        generation = _model.generate(
            input_ids=input_ids,
            prompt_input_ids=prompt_input_ids,
        )

    audio = generation.cpu().numpy().squeeze().astype(np.float32)
    return audio


def synthesize_streaming(text: str, chunk_size: int = 4800) -> Generator[np.ndarray, None, None]:
    """Synthesize Hindi speech and yield audio chunks for streaming.

    Args:
        text: Hindi text to synthesize
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
    global _model, _tokenizer
    _model = None
    _tokenizer = None
