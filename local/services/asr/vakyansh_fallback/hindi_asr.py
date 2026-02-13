"""Vakyansh Wav2Vec2 fallback ASR for Hindi.

Uses the ai4bharat/indicwav2vec-hindi model via Hugging Face Transformers
when the primary Pingala V1 Universal ASR is unavailable.
"""

import os
from typing import Optional

import numpy as np

DEFAULT_MODEL = "ai4bharat/indicwav2vec-hindi"
DEFAULT_DEVICE = os.getenv("ASR_DEVICE", "cpu")

_model = None
_processor = None
_device = None


def load_model(
    model_name: Optional[str] = None,
    device: Optional[str] = None,
) -> bool:
    """Load the Wav2Vec2 model and processor.

    Args:
        model_name: HuggingFace model ID. Defaults to indicwav2vec-hindi.
        device: "cpu" or "cuda". Defaults to ASR_DEVICE env var.

    Returns:
        True if loaded successfully, False otherwise.
    """
    global _model, _processor, _device

    model_id = model_name or DEFAULT_MODEL
    _device = device or DEFAULT_DEVICE

    try:
        from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

        _processor = Wav2Vec2Processor.from_pretrained(model_id)
        _model = Wav2Vec2ForCTC.from_pretrained(model_id)
        _model.to(_device)
        _model.eval()
        return True
    except Exception:
        _model = None
        _processor = None
        return False


def is_loaded() -> bool:
    """Return whether the model is ready for inference."""
    return _model is not None and _processor is not None


def unload_model() -> None:
    """Release the model and processor from memory."""
    global _model, _processor
    _model = None
    _processor = None


def transcribe(audio: np.ndarray, sample_rate: int = 16000) -> str:
    """Transcribe audio to Hindi text.

    Args:
        audio: Float32 numpy array of audio samples.
        sample_rate: Sample rate of the audio (default 16000 Hz).

    Returns:
        Transcribed text string.
    """
    if not is_loaded():
        raise RuntimeError(
            "Vakyansh ASR not loaded — call load_model() first"
        )

    import torch

    inputs = _processor(
        audio,
        sampling_rate=sample_rate,
        return_tensors="pt",
        padding=True,
    )
    input_values = inputs.input_values.to(_device)

    with torch.no_grad():
        logits = _model(input_values).logits

    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = _processor.batch_decode(predicted_ids)[0]
    return transcription.strip()
