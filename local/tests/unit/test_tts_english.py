"""Unit tests for English TTS (Qwen3-TTS).

Uses mocks since model weights may not be available.
"""

import os
import sys
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from services.tts.english import qwen3_tts


class TestQwen3TTS:
    """Test English TTS module."""

    def setup_method(self):
        qwen3_tts.unload_model()

    def test_not_loaded_initially(self):
        qwen3_tts._model = None
        assert not qwen3_tts.is_loaded()

    def test_synthesize_requires_model(self):
        qwen3_tts._model = None
        with pytest.raises(RuntimeError, match="not loaded"):
            qwen3_tts.synthesize("Hello world")

    def test_synthesize_with_mock_model(self):
        """Test synthesis with mocked Qwen3-TTS model produces audio array."""
        fake_audio = np.random.randn(24000).astype(np.float32)

        mock_model = MagicMock()
        mock_model.generate.return_value = ([fake_audio], 24000)

        qwen3_tts._model = mock_model

        audio = qwen3_tts.synthesize("Hello, welcome to your interview.")

        assert isinstance(audio, np.ndarray)
        assert audio.dtype == np.float32
        assert len(audio) == 24000
        mock_model.generate.assert_called_once()

    def test_streaming_yields_chunks(self):
        """Test streaming synthesis yields audio chunks."""
        fake_audio = np.random.randn(16000).astype(np.float32)

        mock_model = MagicMock()
        mock_model.generate.return_value = ([fake_audio], 24000)

        qwen3_tts._model = mock_model

        chunks = list(qwen3_tts.synthesize_streaming("Test text", chunk_size=4800))

        # 16000 / 4800 = 3.33 -> 4 chunks (last one partial)
        assert len(chunks) == 4
        for chunk in chunks:
            assert isinstance(chunk, np.ndarray)

    def test_unload_model(self):
        qwen3_tts._model = MagicMock()
        qwen3_tts.unload_model()
        assert not qwen3_tts.is_loaded()

    def test_is_loaded_after_mock_load(self):
        qwen3_tts._model = MagicMock()
        assert qwen3_tts.is_loaded()
