"""Integration tests for ASR → Language Control → Orchestrator pipeline.

Tests use simulated ASR output since model weights may not be available.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from services.asr.pingala.lang_detection import detect_language
from services.asr.pingala.streaming_asr import TranscriptSegment
from services.orchestrator.language_control import LanguageController, Language
from services.orchestrator.state_machine import InterviewStateMachine, InterviewState


class TestASRToOrchestrator:
    """Test ASR output feeding into orchestrator."""

    def test_english_transcript_stays_english(self):
        lc = LanguageController()
        transcript = "I want to study computer science at MIT"
        lang = detect_language(transcript)
        assert lang == "en"

        result = lc.process_input(transcript)
        assert result["output_language"] == Language.ENGLISH
        assert result["explanation_mode"] is False

    def test_hindi_switch_request_triggers_explanation(self):
        lc = LanguageController()
        transcript = "Hindi mein samjha do please"
        result = lc.process_input(transcript)
        assert result["action"] == "switch_to_hindi"
        assert result["explanation_mode"] is True

    def test_mixed_input_detected(self):
        transcript = "Mera father sponsor kar rahe hain lekin unki income kam hai"
        lang = detect_language(transcript)
        assert lang == "mixed"

    def test_transcript_segment_feeds_state_machine(self):
        sm = InterviewStateMachine(destination_country="US")

        # Simulate ASR output
        segment = TranscriptSegment(
            text="My name is Preet and I want to study in the US",
            is_partial=False,
            language="en",
        )

        # Orchestrator processes it
        sm.record_question(1)
        sm.record_answer(1, segment.text, 0.8)
        assert sm.context.answers[1] == segment.text

    def test_partial_transcript_available(self):
        """Partial transcripts should be accessible before final."""
        segment = TranscriptSegment(
            text="My name is",
            is_partial=True,
            language="en",
        )
        assert segment.is_partial is True

        final_segment = TranscriptSegment(
            text="My name is Preet",
            is_partial=False,
            language="en",
        )
        assert final_segment.is_partial is False

    def test_language_detection_feeds_language_control(self):
        """ASR language detection should inform language controller."""
        lc = LanguageController()

        # English input
        english_seg = TranscriptSegment(text="I have a bachelor's degree", is_partial=False, language="en")
        result = lc.process_input(english_seg.text)
        assert result["output_language"] == Language.ENGLISH

        # Hindi switch request in Hinglish
        hindi_seg = TranscriptSegment(text="Hindi mein explain karo", is_partial=False, language="mixed")
        result = lc.process_input(hindi_seg.text)
        assert result["explanation_mode"] is True

    def test_full_pipeline_english_session(self):
        """Simulate a full English session through ASR → orchestrator."""
        sm = InterviewStateMachine(destination_country="UK")
        lc = LanguageController()

        # Greeting
        seg = TranscriptSegment(text="Hello, my name is Preet", is_partial=False, language="en")
        lc_result = lc.process_input(seg.text)
        assert lc_result["output_language"] == Language.ENGLISH
        sm.record_question(1)
        sm.record_answer(1, seg.text, 0.8)

        # Advance to academics
        sm.advance()
        assert sm.current_state == InterviewState.ACADEMICS

        # Academic answer
        seg2 = TranscriptSegment(
            text="I completed my Bachelor's in Computer Science from Delhi University with 85 percent",
            is_partial=False,
            language="en",
        )
        sm.record_question(2)
        sm.record_answer(2, seg2.text, 0.9)

        assert sm.context.total_questions_asked == 2
