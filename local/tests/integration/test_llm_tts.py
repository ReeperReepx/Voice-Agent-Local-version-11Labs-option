"""Integration tests for LLM → TTS language selection.

Tests that the correct TTS engine is selected based on output language.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from services.orchestrator.language_control import Language, LanguageController
from services.tts import get_tts_for_language


class TestTTSLanguageSelection:
    """Test correct TTS engine selection based on language."""

    def test_english_selects_qwen3(self):
        tts = get_tts_for_language("en")
        assert tts.__name__.endswith("qwen3_tts")

    def test_hindi_selects_parler(self):
        tts = get_tts_for_language("hi")
        assert tts.__name__.endswith("parler_tts")

    def test_default_is_english(self):
        tts = get_tts_for_language("unknown")
        assert tts.__name__.endswith("qwen3_tts")

    def test_language_control_drives_tts_selection(self):
        """Language controller output should determine TTS selection."""
        lc = LanguageController()

        # English mode → Qwen3-TTS
        result = lc.process_input("I want to study computer science")
        tts = get_tts_for_language(result["output_language"].value)
        assert tts.__name__.endswith("qwen3_tts")

        # Switch to Hindi → Parler-TTS
        result = lc.process_input("Hindi mein samjha do")
        tts = get_tts_for_language(result["output_language"].value)
        assert tts.__name__.endswith("parler_tts")

        # Revert → Qwen3-TTS
        lc.auto_revert()
        result = lc.process_input("OK continue")
        tts = get_tts_for_language(result["output_language"].value)
        assert tts.__name__.endswith("qwen3_tts")

    def test_streaming_available_for_both(self):
        """Both TTS engines should have streaming support."""
        en_tts = get_tts_for_language("en")
        hi_tts = get_tts_for_language("hi")
        assert hasattr(en_tts, "synthesize_streaming")
        assert hasattr(hi_tts, "synthesize_streaming")
