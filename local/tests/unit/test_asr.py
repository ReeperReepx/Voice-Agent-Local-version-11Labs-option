"""Unit tests for ASR: model loading, transcription, and language detection.

Tests use mocked model since Pingala V1 requires GPU and model weights.
"""

import os
import sys
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from services.asr.pingala.lang_detection import (
    detect_language,
    detect_language_from_audio_start,
)
from services.asr.pingala.streaming_asr import StreamingASR, TranscriptSegment
from services.asr.pingala import model_loader


class TestLanguageDetection:
    """Test language detection from text."""

    def test_detect_english(self):
        assert detect_language("I want to study computer science") == "en"

    def test_detect_hindi_devanagari(self):
        assert detect_language("मैं कंप्यूटर साइंस पढ़ना चाहता हूँ") == "hi"

    def test_detect_mixed_hinglish(self):
        assert detect_language("Mujhe yeh course bahut accha lagta hai") == "mixed"

    def test_detect_english_no_hindi_words(self):
        assert detect_language("The university has excellent facilities") == "en"

    def test_empty_string_defaults_english(self):
        assert detect_language("") == "en"

    def test_detect_from_audio_start(self):
        assert detect_language_from_audio_start("Hello my name is Preet") == "en"

    def test_detect_hindi_start(self):
        assert detect_language_from_audio_start("Mera naam hai aur mein padhai karna chahta hoon") == "mixed"


class TestStreamingASR:
    """Test streaming ASR with mocked Pingala transcriber."""

    def test_create_streaming_asr(self):
        asr = StreamingASR()
        assert asr.sample_rate == 16000
        assert asr.chunk_duration_s == 0.5

    def test_feed_audio_short_chunk(self):
        """Short chunk should not produce output."""
        asr = StreamingASR()
        asr._transcriber = MagicMock()

        # 100ms of audio (too short for 500ms chunk)
        short_audio = np.zeros(1600, dtype=np.float32)
        result = asr.feed_audio(short_audio)
        assert result is None

    def test_feed_audio_sufficient_chunk(self):
        """Sufficient audio should produce a transcript."""
        asr = StreamingASR()

        # Create mock transcriber
        mock_segment = MagicMock()
        mock_segment.text = "Hello my name is Preet"
        mock_transcriber = MagicMock()
        mock_transcriber.transcribe_file.return_value = ([mock_segment], {})

        asr._transcriber = mock_transcriber

        # 500ms of audio (16000 * 0.5 = 8000 samples)
        audio = np.zeros(8000, dtype=np.float32)

        with patch("services.asr.pingala.streaming_asr.sf") as mock_sf:
            result = asr.feed_audio(audio)

        assert result is not None
        assert result.text == "Hello my name is Preet"
        assert result.is_partial is True
        assert result.language == "en"

    def test_finalize_empty_buffer(self):
        asr = StreamingASR()
        asr._transcriber = MagicMock()
        result = asr.finalize()
        assert result is None

    def test_reset(self):
        asr = StreamingASR()
        asr._buffer = [np.zeros(100)]
        asr._transcripts = [TranscriptSegment(text="test", is_partial=False, language="en")]
        asr._total_duration = 5.0

        asr.reset()

        assert len(asr._buffer) == 0
        assert len(asr._transcripts) == 0
        assert asr._total_duration == 0.0

    def test_get_full_transcript(self):
        asr = StreamingASR()
        asr._transcripts = [
            TranscriptSegment(text="Hello", is_partial=False, language="en"),
            TranscriptSegment(text="my name is Preet", is_partial=False, language="en"),
        ]
        assert asr.get_full_transcript() == "Hello my name is Preet"

    def test_get_all_segments(self):
        asr = StreamingASR()
        asr._transcripts = [
            TranscriptSegment(text="Hello", is_partial=False, language="en"),
        ]
        segments = asr.get_all_segments()
        assert len(segments) == 1
        assert segments[0].text == "Hello"

    def test_not_initialized_raises(self):
        asr = StreamingASR()
        audio = np.zeros(8000, dtype=np.float32)
        with pytest.raises(RuntimeError, match="not initialized"):
            asr._transcribe(audio)


class TestModelLoader:
    """Test model loader functionality."""

    def test_is_loaded_initially_false(self):
        model_loader._transcriber = None
        assert not model_loader.is_loaded()

    def test_unload_model(self):
        model_loader._transcriber = MagicMock()
        model_loader.unload_model()
        assert not model_loader.is_loaded()


class TestMixedLanguageHandling:
    """Test handling of mixed Hindi/English (Hinglish) input."""

    def test_hinglish_sentence(self):
        text = "Mera father mein se sponsor kar rahe hain aur unki income hai"
        lang = detect_language(text)
        assert lang in ("mixed", "hi")

    def test_english_with_one_hindi_word(self):
        """Mostly English with one Hindi word should still be English."""
        text = "I am studying at the university and doing accha"
        lang = detect_language(text)
        assert lang == "en"  # Only 1/9 words is Hindi

    def test_code_switched_sentence(self):
        text = "Main padhai kar raha hoon computer science mein"
        lang = detect_language(text)
        assert lang == "mixed"
