"""Unit tests for language control module."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from services.orchestrator.language_control import (
    Language,
    LanguageController,
)


class TestLanguageDetection:
    """Test switch detection."""

    def test_detect_hindi_explanation_request(self):
        lc = LanguageController()
        assert lc.detect_switch_request("Hindi mein samjha do")
        assert lc.detect_switch_request("Can you explain this in Hindi?")
        assert lc.detect_switch_request("Explain again in Hindi")
        assert lc.detect_switch_request("Hindi mein samjhao")
        assert lc.detect_switch_request("please explain in hindi")

    def test_no_switch_on_normal_english(self):
        lc = LanguageController()
        assert not lc.detect_switch_request("I want to study computer science")
        assert not lc.detect_switch_request("My father is my sponsor")
        assert not lc.detect_switch_request("I plan to return to India")

    def test_no_switch_on_hindi_answer(self):
        """Hindi answer without explicit switch request should NOT trigger switch."""
        lc = LanguageController()
        assert not lc.detect_switch_request("Mera naam Preet hai")
        assert not lc.detect_switch_request("Main India se hoon")

    def test_detect_revert_request(self):
        lc = LanguageController()
        assert lc.detect_revert_request("ok english")
        assert lc.detect_revert_request("let's continue in English")
        assert lc.detect_revert_request("back to English")

    def test_no_revert_on_normal_hindi(self):
        lc = LanguageController()
        assert not lc.detect_revert_request("mujhe aur samjhao")


class TestLanguageSwitching:
    """Test switch and revert behavior."""

    def test_switch_only_on_explicit_request(self):
        lc = LanguageController()
        result = lc.process_input("Hindi mein samjha do", question_id=1)
        assert result["action"] == "switch_to_hindi"
        assert result["explanation_mode"] is True
        assert result["output_language"] == Language.HINDI

    def test_no_switch_without_request(self):
        lc = LanguageController()
        result = lc.process_input("I want to study in the US", question_id=1)
        assert result["action"] == "none"
        assert result["explanation_mode"] is False
        assert result["output_language"] == Language.ENGLISH

    def test_auto_revert_works(self):
        lc = LanguageController()
        # Switch to Hindi
        lc.process_input("Hindi mein samjha do", question_id=1)
        assert lc.state.explanation_mode is True

        # Auto revert
        message = lc.auto_revert()
        assert lc.state.explanation_mode is False
        assert lc.state.current_output_language == Language.ENGLISH
        assert "continue" in message.lower()

    def test_revert_on_explicit_request(self):
        lc = LanguageController()
        # Switch to Hindi
        lc.process_input("Can you explain this in Hindi?", question_id=1)
        # Revert
        result = lc.process_input("ok, back to English", question_id=1)
        assert result["action"] == "revert_to_english"
        assert result["explanation_mode"] is False

    def test_stay_in_explanation_mode_until_revert(self):
        lc = LanguageController()
        lc.process_input("Hindi mein samjha do", question_id=1)
        # Normal input while in explanation mode
        result = lc.process_input("Aur batao", question_id=1)
        assert result["explanation_mode"] is True
        assert result["output_language"] == Language.HINDI

    def test_switch_count_increments(self):
        lc = LanguageController()
        lc.process_input("Hindi mein samjha do", question_id=1)
        assert lc.state.switch_count == 1
        lc.auto_revert()
        lc.process_input("Explain in Hindi please", question_id=2)
        assert lc.state.switch_count == 2

    def test_switch_history_tracked(self):
        lc = LanguageController()
        lc.process_input("Hindi mein samjha do", question_id=5)
        assert len(lc.state.switch_history) == 1
        assert lc.state.switch_history[0]["question_id"] == 5
        assert lc.state.switch_history[0]["direction"] == "to_hindi"


class TestPrimaryLanguage:
    """Test primary language configuration."""

    def test_default_is_english(self):
        lc = LanguageController()
        assert lc.state.primary_language == Language.ENGLISH

    def test_hindi_primary(self):
        lc = LanguageController(primary_language=Language.HINDI)
        assert lc.state.primary_language == Language.HINDI
        assert lc.state.current_output_language == Language.HINDI

    def test_revert_goes_to_primary(self):
        lc = LanguageController(primary_language=Language.ENGLISH)
        lc.activate_explanation_mode(1)
        lc.auto_revert()
        assert lc.state.current_output_language == Language.ENGLISH
