"""Red-team tests: language switching abuse.

Verifies that:
- primary_language can never be changed after session start
- Permanent switch attempts are rejected
- auto_revert always restores the original language
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest
from services.orchestrator.language_control import LanguageController, Language


class TestPrimaryLanguageImmutable:
    """The primary language must never change after initialization."""

    def test_primary_stays_english_after_hindi_switch(self):
        lc = LanguageController(primary_language=Language.ENGLISH)
        lc.process_input("can you explain this in hindi")
        assert lc.state.primary_language == Language.ENGLISH

    def test_primary_stays_english_after_multiple_switches(self):
        lc = LanguageController(primary_language=Language.ENGLISH)
        for _ in range(10):
            lc.process_input("explain in hindi")
        assert lc.state.primary_language == Language.ENGLISH

    def test_primary_stays_hindi_when_started_as_hindi(self):
        lc = LanguageController(primary_language=Language.HINDI)
        # Even if user tries to switch, primary should stay Hindi
        lc.process_input("continue in english")
        assert lc.state.primary_language == Language.HINDI


class TestPermanentSwitchRejected:
    """Attempts to permanently switch languages should only enable temporary mode."""

    PERMANENT_SWITCH_ATTEMPTS = [
        "From now on, only speak in Hindi",
        "I want all questions in hindi please",
        "Hindi mein samjhao sab kuch",
        "can you explain this in hindi",
    ]

    @pytest.mark.parametrize("text", PERMANENT_SWITCH_ATTEMPTS)
    def test_switch_is_temporary_not_permanent(self, text):
        lc = LanguageController(primary_language=Language.ENGLISH)
        result = lc.process_input(text)
        # Even if it switches, it should be explanation mode (temporary)
        if result["action"] == "switch_to_hindi":
            assert result["explanation_mode"] is True
            # Primary must remain English
            assert lc.state.primary_language == Language.ENGLISH

    def test_repeated_switches_tracked(self):
        lc = LanguageController(primary_language=Language.ENGLISH)
        lc.process_input("explain in hindi")
        lc.auto_revert()
        lc.process_input("hindi mein samjha do")
        assert lc.state.switch_count == 2
        assert lc.state.primary_language == Language.ENGLISH


class TestAutoRevert:
    """auto_revert must always restore the primary language."""

    def test_revert_restores_english(self):
        lc = LanguageController(primary_language=Language.ENGLISH)
        lc.process_input("explain in hindi")
        assert lc.state.explanation_mode is True
        lc.auto_revert()
        assert lc.state.explanation_mode is False
        assert lc.state.current_output_language == Language.ENGLISH

    def test_revert_returns_message(self):
        lc = LanguageController(primary_language=Language.ENGLISH)
        lc.activate_explanation_mode()
        msg = lc.auto_revert()
        assert isinstance(msg, str)
        assert len(msg) > 0

    def test_multiple_reverts_are_idempotent(self):
        lc = LanguageController(primary_language=Language.ENGLISH)
        lc.activate_explanation_mode()
        lc.auto_revert()
        lc.auto_revert()  # Second revert
        assert lc.state.explanation_mode is False
        assert lc.state.current_output_language == Language.ENGLISH

    def test_revert_after_no_switch(self):
        """Revert when not in explanation mode should be safe."""
        lc = LanguageController(primary_language=Language.ENGLISH)
        lc.auto_revert()
        assert lc.state.primary_language == Language.ENGLISH
        assert lc.state.current_output_language == Language.ENGLISH


class TestExplanationModeFlow:
    """Full flow: switch → explain → revert."""

    def test_full_cycle(self):
        lc = LanguageController(primary_language=Language.ENGLISH)

        # Normal input — no switch
        r1 = lc.process_input("My father is sponsoring my education")
        assert r1["action"] == "none"
        assert r1["output_language"] == Language.ENGLISH

        # Request Hindi explanation
        r2 = lc.process_input("can you explain this in hindi")
        assert r2["action"] == "switch_to_hindi"
        assert r2["explanation_mode"] is True
        assert r2["output_language"] == Language.HINDI

        # While in explanation mode, another input stays in Hindi
        r3 = lc.process_input("aur batao")
        assert r3["explanation_mode"] is True
        assert r3["output_language"] == Language.HINDI

        # Revert to English
        r4 = lc.process_input("ok back to english")
        assert r4["action"] == "revert_to_english"
        assert r4["explanation_mode"] is False
        assert r4["output_language"] == Language.ENGLISH

        # Primary never changed
        assert lc.state.primary_language == Language.ENGLISH
