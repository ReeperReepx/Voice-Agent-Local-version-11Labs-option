"""Tests for eSpeak-NG TTS fallback."""

import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pytest
from unittest.mock import patch, MagicMock
from services.tts.fallback import espeak


@pytest.fixture(autouse=True)
def reset_state():
    """Reset module state between tests."""
    espeak._loaded = False
    yield
    espeak._loaded = False


class TestIsAvailable:
    """Tests for is_available."""

    @patch("shutil.which", return_value="/usr/bin/espeak-ng")
    def test_available_when_installed(self, mock_which):
        assert espeak.is_available() is True

    @patch("shutil.which", return_value=None)
    def test_unavailable_when_not_installed(self, mock_which):
        assert espeak.is_available() is False


class TestLoadModel:
    """Tests for load_model."""

    @patch("shutil.which", return_value="/usr/bin/espeak-ng")
    def test_load_succeeds_when_available(self, mock_which):
        espeak.load_model()
        assert espeak.is_loaded() is True

    @patch("shutil.which", return_value=None)
    def test_load_raises_when_unavailable(self, mock_which):
        with pytest.raises(RuntimeError, match="espeak-ng is not installed"):
            espeak.load_model()

    @patch("shutil.which", return_value="/usr/bin/espeak-ng")
    def test_unload_model(self, mock_which):
        espeak.load_model()
        assert espeak.is_loaded() is True
        espeak.unload_model()
        assert espeak.is_loaded() is False


class TestSynthesize:
    """Tests for synthesize."""

    def test_not_loaded_raises(self):
        with pytest.raises(RuntimeError, match="not loaded"):
            espeak.synthesize("hello")

    @patch("shutil.which", return_value="/usr/bin/espeak-ng")
    @patch("subprocess.run")
    @patch("soundfile.read")
    def test_synthesize_calls_espeak(self, mock_sf_read, mock_run, mock_which):
        mock_sf_read.return_value = (np.zeros(1000, dtype=np.float32), 22050)
        espeak.load_model()

        audio = espeak.synthesize("namaste")

        assert mock_run.called
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert cmd[0] == "espeak-ng"
        assert "-v" in cmd
        assert "hi" in cmd
        assert isinstance(audio, np.ndarray)
        assert len(audio) == 1000

    @patch("shutil.which", return_value="/usr/bin/espeak-ng")
    @patch("subprocess.run")
    @patch("soundfile.read")
    def test_synthesize_writes_wav(self, mock_sf_read, mock_run, mock_which):
        mock_sf_read.return_value = (np.zeros(500, dtype=np.float32), 22050)
        espeak.load_model()

        espeak.synthesize("test text")

        call_args = mock_run.call_args[0][0]
        assert "-w" in call_args
        # The argument after -w should be a temp file path
        w_idx = call_args.index("-w")
        assert call_args[w_idx + 1].endswith(".wav")

    @patch("shutil.which", return_value="/usr/bin/espeak-ng")
    @patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "espeak-ng"))
    def test_synthesize_raises_on_subprocess_error(self, mock_run, mock_which):
        espeak.load_model()

        with pytest.raises(subprocess.CalledProcessError):
            espeak.synthesize("fail text")
