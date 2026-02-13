"""Unit tests for audio pipeline utilities."""

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from services.audio_pipeline import (
    pcm16_to_float32,
    float32_to_pcm16,
    resample_audio,
    chunk_pcm_bytes,
)


class TestPCM16ToFloat32:
    """Test PCM16 → float32 conversion."""

    def test_silence(self):
        pcm = np.zeros(100, dtype=np.int16).tobytes()
        result = pcm16_to_float32(pcm)
        assert result.dtype == np.float32
        assert len(result) == 100
        np.testing.assert_array_equal(result, np.zeros(100, dtype=np.float32))

    def test_max_positive(self):
        pcm = np.array([32767], dtype=np.int16).tobytes()
        result = pcm16_to_float32(pcm)
        assert result[0] == pytest.approx(1.0, abs=1e-4)

    def test_max_negative(self):
        pcm = np.array([-32768], dtype=np.int16).tobytes()
        result = pcm16_to_float32(pcm)
        assert result[0] == pytest.approx(-1.0, abs=1e-4)

    def test_empty(self):
        result = pcm16_to_float32(b"")
        assert len(result) == 0


class TestFloat32ToPCM16:
    """Test float32 → PCM16 conversion."""

    def test_silence(self):
        audio = np.zeros(100, dtype=np.float32)
        result = float32_to_pcm16(audio)
        assert len(result) == 200  # 100 samples * 2 bytes

    def test_max_positive(self):
        audio = np.array([1.0], dtype=np.float32)
        result = float32_to_pcm16(audio)
        samples = np.frombuffer(result, dtype=np.int16)
        assert samples[0] == 32767

    def test_clipping(self):
        audio = np.array([2.0, -3.0], dtype=np.float32)
        result = float32_to_pcm16(audio)
        samples = np.frombuffer(result, dtype=np.int16)
        assert samples[0] == 32767
        assert samples[1] == -32767  # clipped to -1.0 * 32767

    def test_roundtrip(self):
        original = np.array([0.0, 0.5, -0.5, 0.25], dtype=np.float32)
        pcm = float32_to_pcm16(original)
        recovered = pcm16_to_float32(pcm)
        np.testing.assert_allclose(recovered, original, atol=1e-4)


class TestResampleAudio:
    """Test audio resampling."""

    def test_same_rate_passthrough(self):
        audio = np.random.randn(1000).astype(np.float32)
        result = resample_audio(audio, 24000, 24000)
        np.testing.assert_array_equal(result, audio)

    def test_upsample_length(self):
        audio = np.ones(16000, dtype=np.float32)
        result = resample_audio(audio, 16000, 24000)
        assert len(result) == 24000

    def test_downsample_length(self):
        audio = np.ones(44100, dtype=np.float32)
        result = resample_audio(audio, 44100, 24000)
        assert len(result) == 24000

    def test_preserves_dc(self):
        """Constant signal should stay constant after resample."""
        audio = np.full(16000, 0.5, dtype=np.float32)
        result = resample_audio(audio, 16000, 24000)
        np.testing.assert_allclose(result, 0.5, atol=1e-5)

    def test_empty_input(self):
        audio = np.array([], dtype=np.float32)
        result = resample_audio(audio, 16000, 24000)
        assert len(result) == 0

    def test_output_dtype(self):
        audio = np.ones(100, dtype=np.float32)
        result = resample_audio(audio, 16000, 24000)
        assert result.dtype == np.float32


class TestChunkPCMBytes:
    """Test PCM byte chunking."""

    def test_exact_division(self):
        pcm = b"\x00" * (4800 * 2)  # exactly 1 chunk
        chunks = chunk_pcm_bytes(pcm, chunk_size=4800)
        assert len(chunks) == 1
        assert len(chunks[0]) == 4800 * 2

    def test_multiple_chunks(self):
        pcm = b"\x00" * (4800 * 2 * 3)  # exactly 3 chunks
        chunks = chunk_pcm_bytes(pcm, chunk_size=4800)
        assert len(chunks) == 3

    def test_remainder_chunk(self):
        pcm = b"\x00" * (4800 * 2 + 100)  # 1 full + 1 partial
        chunks = chunk_pcm_bytes(pcm, chunk_size=4800)
        assert len(chunks) == 2
        assert len(chunks[0]) == 4800 * 2
        assert len(chunks[1]) == 100

    def test_empty(self):
        chunks = chunk_pcm_bytes(b"", chunk_size=4800)
        assert chunks == []

    def test_small_input(self):
        pcm = b"\x01\x02"
        chunks = chunk_pcm_bytes(pcm, chunk_size=4800)
        assert len(chunks) == 1
        assert chunks[0] == b"\x01\x02"
