"""Unit tests for Hindi TTS (Parler-TTS).

Uses mocks since model weights may not be available.
"""

import os
import sys
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from services.tts.hindi import parler_tts


class TestParlerTTS:
    """Test Hindi TTS module."""

    def setup_method(self):
        parler_tts.unload_model()

    def test_not_loaded_initially(self):
        parler_tts._model = None
        assert not parler_tts.is_loaded()

    def test_synthesize_requires_model(self):
        parler_tts._model = None
        with pytest.raises(RuntimeError, match="not loaded"):
            parler_tts.synthesize("नमस्ते")

    def test_synthesize_with_mock_model(self):
        """Test Hindi synthesis with mocked Parler-TTS model."""
        fake_audio = np.random.randn(24000).astype(np.float32)

        mock_model = MagicMock()
        mock_model.device = "cpu"
        mock_generation = MagicMock()
        mock_generation.cpu.return_value.numpy.return_value.squeeze.return_value.astype.return_value = fake_audio
        mock_model.generate.return_value = mock_generation

        mock_tokenizer = MagicMock()
        mock_token_result = MagicMock()
        mock_token_result.input_ids.to.return_value = MagicMock()
        mock_tokenizer.return_value = mock_token_result

        parler_tts._model = mock_model
        parler_tts._tokenizer = mock_tokenizer

        mock_torch = MagicMock()
        mock_torch.no_grad.return_value.__enter__ = MagicMock(return_value=None)
        mock_torch.no_grad.return_value.__exit__ = MagicMock(return_value=False)

        with patch.dict("sys.modules", {"torch": mock_torch}):
            audio = parler_tts.synthesize("यह एक परीक्षा है")

        assert isinstance(audio, np.ndarray)
        assert audio.dtype == np.float32
        assert len(audio) == 24000

    def test_streaming_yields_chunks(self):
        """Test streaming Hindi synthesis."""
        fake_audio = np.random.randn(24000).astype(np.float32)

        mock_model = MagicMock()
        mock_model.device = "cpu"
        mock_generation = MagicMock()
        mock_generation.cpu.return_value.numpy.return_value.squeeze.return_value.astype.return_value = fake_audio
        mock_model.generate.return_value = mock_generation

        mock_tokenizer = MagicMock()
        mock_token_result = MagicMock()
        mock_token_result.input_ids.to.return_value = MagicMock()
        mock_tokenizer.return_value = mock_token_result

        parler_tts._model = mock_model
        parler_tts._tokenizer = mock_tokenizer

        mock_torch = MagicMock()
        mock_torch.no_grad.return_value.__enter__ = MagicMock(return_value=None)
        mock_torch.no_grad.return_value.__exit__ = MagicMock(return_value=False)

        with patch.dict("sys.modules", {"torch": mock_torch}):
            chunks = list(parler_tts.synthesize_streaming("Namaste", chunk_size=4800))

        assert len(chunks) == 5
        for chunk in chunks:
            assert isinstance(chunk, np.ndarray)

    def test_unload_model(self):
        parler_tts._model = MagicMock()
        parler_tts._tokenizer = MagicMock()
        parler_tts.unload_model()
        assert not parler_tts.is_loaded()
