"""Tests for Vakyansh Wav2Vec2 Hindi ASR fallback."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pytest
from unittest.mock import patch, MagicMock
from services.asr.vakyansh_fallback import hindi_asr


@pytest.fixture(autouse=True)
def reset_state():
    """Reset module state between tests."""
    hindi_asr._model = None
    hindi_asr._processor = None
    hindi_asr._device = None
    yield
    hindi_asr._model = None
    hindi_asr._processor = None
    hindi_asr._device = None


class TestLoadModel:
    """Tests for load_model."""

    @patch("services.asr.vakyansh_fallback.hindi_asr.Wav2Vec2ForCTC", create=True)
    @patch("services.asr.vakyansh_fallback.hindi_asr.Wav2Vec2Processor", create=True)
    def test_load_success(self, mock_proc_cls, mock_model_cls):
        mock_processor = MagicMock()
        mock_model = MagicMock()
        mock_proc_cls.from_pretrained.return_value = mock_processor
        mock_model_cls.from_pretrained.return_value = mock_model

        with patch.dict("sys.modules", {
            "transformers": MagicMock(
                Wav2Vec2ForCTC=mock_model_cls,
                Wav2Vec2Processor=mock_proc_cls,
            ),
        }):
            result = hindi_asr.load_model()

        assert result is True
        assert hindi_asr.is_loaded() is True

    def test_load_failure_returns_false(self):
        with patch.dict("sys.modules", {"transformers": None}):
            # This will cause ImportError inside load_model
            result = hindi_asr.load_model("nonexistent/model")
        assert result is False
        assert hindi_asr.is_loaded() is False

    def test_unload_model(self):
        hindi_asr._model = MagicMock()
        hindi_asr._processor = MagicMock()
        assert hindi_asr.is_loaded() is True
        hindi_asr.unload_model()
        assert hindi_asr.is_loaded() is False


class TestIsLoaded:
    """Tests for is_loaded."""

    def test_not_loaded_initially(self):
        assert hindi_asr.is_loaded() is False

    def test_loaded_when_both_set(self):
        hindi_asr._model = MagicMock()
        hindi_asr._processor = MagicMock()
        assert hindi_asr.is_loaded() is True

    def test_not_loaded_if_only_model(self):
        hindi_asr._model = MagicMock()
        assert hindi_asr.is_loaded() is False

    def test_not_loaded_if_only_processor(self):
        hindi_asr._processor = MagicMock()
        assert hindi_asr.is_loaded() is False


class TestTranscribe:
    """Tests for transcribe."""

    def test_not_loaded_raises(self):
        audio = np.zeros(16000, dtype=np.float32)
        with pytest.raises(RuntimeError, match="not loaded"):
            hindi_asr.transcribe(audio)

    def test_transcribe_returns_string(self):
        mock_model = MagicMock()
        mock_processor = MagicMock()

        # Set up mock chain
        import torch
        mock_logits = torch.zeros(1, 10, 32)
        mock_output = MagicMock()
        mock_output.logits = mock_logits
        mock_model.return_value = mock_output

        mock_inputs = MagicMock()
        mock_inputs.input_values = torch.zeros(1, 16000)
        mock_processor.return_value = mock_inputs
        mock_processor.batch_decode.return_value = ["namaste duniya"]

        hindi_asr._model = mock_model
        hindi_asr._processor = mock_processor
        hindi_asr._device = "cpu"

        audio = np.zeros(16000, dtype=np.float32)
        result = hindi_asr.transcribe(audio, sample_rate=16000)

        assert isinstance(result, str)
        assert result == "namaste duniya"
        mock_processor.assert_called_once()

    def test_transcribe_strips_whitespace(self):
        mock_model = MagicMock()
        mock_processor = MagicMock()

        import torch
        mock_output = MagicMock()
        mock_output.logits = torch.zeros(1, 10, 32)
        mock_model.return_value = mock_output

        mock_inputs = MagicMock()
        mock_inputs.input_values = torch.zeros(1, 16000)
        mock_processor.return_value = mock_inputs
        mock_processor.batch_decode.return_value = ["  hello world  "]

        hindi_asr._model = mock_model
        hindi_asr._processor = mock_processor
        hindi_asr._device = "cpu"

        audio = np.zeros(16000, dtype=np.float32)
        result = hindi_asr.transcribe(audio)
        assert result == "hello world"

    def test_default_device_from_env(self):
        with patch.dict(os.environ, {"ASR_DEVICE": "cuda:0"}):
            # Re-import to pick up env change
            import importlib
            importlib.reload(hindi_asr)
            assert hindi_asr.DEFAULT_DEVICE == "cuda:0"
        # Restore
        importlib.reload(hindi_asr)
