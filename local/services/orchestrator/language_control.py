"""Language control module.

Manages primary language, explanation mode, and auto-reversion.
Rules:
- Interview language is locked at session start
- Temporary switching only on explicit request
- Automatic reversion after explanation
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum


class Language(Enum):
    ENGLISH = "en"
    HINDI = "hi"


# Patterns that trigger explanation mode (Hindi explanation request)
HINDI_SWITCH_PATTERNS = [
    r"hindi\s+m(?:e|ei)n\s+(?:samjh|bata|explain)",
    r"can\s+you\s+explain\s+(?:this\s+)?in\s+hindi",
    r"explain\s+(?:again\s+)?(?:but\s+)?in\s+hindi",
    r"hindi\s+m(?:e|ei)n\s+samjha\s*(?:do|o|iye)",
    r"mujhe\s+hindi\s+m(?:e|ei)n",
    r"please\s+(?:say|tell|explain)\s+in\s+hindi",
]

# Patterns that revert to English
ENGLISH_REVERT_PATTERNS = [
    r"(?:ok|okay|alright|fine|haan)\s*,?\s*(?:english|eng)",
    r"(?:let'?s?\s+)?continue\s+in\s+english",
    r"back\s+to\s+english",
    r"english\s+m(?:e|ei)n",
]


@dataclass
class LanguageState:
    """Tracks language state for a session."""
    primary_language: Language = Language.ENGLISH
    current_output_language: Language = Language.ENGLISH
    explanation_mode: bool = False
    explanation_language: Language = Language.HINDI
    switch_count: int = 0
    switch_history: list = field(default_factory=list)

    @property
    def is_explanation_active(self) -> bool:
        return self.explanation_mode


class LanguageController:
    """Controls language switching during the interview."""

    def __init__(self, primary_language: Language = Language.ENGLISH):
        self.state = LanguageState(
            primary_language=primary_language,
            current_output_language=primary_language,
        )

    def detect_switch_request(self, text: str) -> bool:
        """Check if the user is explicitly requesting a language switch to Hindi."""
        lower = text.lower().strip()
        for pattern in HINDI_SWITCH_PATTERNS:
            if re.search(pattern, lower):
                return True
        return False

    def detect_revert_request(self, text: str) -> bool:
        """Check if the user wants to revert to English."""
        lower = text.lower().strip()
        for pattern in ENGLISH_REVERT_PATTERNS:
            if re.search(pattern, lower):
                return True
        return False

    def process_input(self, text: str, question_id: int = 0) -> dict:
        """Process user input and determine language action.

        Returns dict with:
            - action: 'none', 'switch_to_hindi', 'revert_to_english'
            - explanation_mode: bool
            - output_language: Language
        """
        if self.state.explanation_mode:
            # In explanation mode, check for revert
            if self.detect_revert_request(text):
                return self._revert_to_primary()
            # Stay in explanation mode
            return {
                "action": "none",
                "explanation_mode": True,
                "output_language": self.state.explanation_language,
            }

        # Normal mode — check for switch request
        if self.detect_switch_request(text):
            return self._switch_to_explanation(question_id)

        # No switch — continue in primary language
        return {
            "action": "none",
            "explanation_mode": False,
            "output_language": self.state.primary_language,
        }

    def activate_explanation_mode(self, question_id: int = 0) -> None:
        """Manually activate explanation mode."""
        self.state.explanation_mode = True
        self.state.current_output_language = self.state.explanation_language
        self.state.switch_count += 1
        self.state.switch_history.append({
            "question_id": question_id,
            "direction": "to_hindi",
        })

    def auto_revert(self) -> str:
        """Automatically revert to primary language after explanation.

        Returns the reversion message.
        """
        self.state.explanation_mode = False
        self.state.current_output_language = self.state.primary_language
        return "Let's continue with the interview."

    def _switch_to_explanation(self, question_id: int) -> dict:
        self.activate_explanation_mode(question_id)
        return {
            "action": "switch_to_hindi",
            "explanation_mode": True,
            "output_language": self.state.explanation_language,
        }

    def _revert_to_primary(self) -> dict:
        self.auto_revert()
        return {
            "action": "revert_to_english",
            "explanation_mode": False,
            "output_language": self.state.primary_language,
        }
