"""Language detection from transcribed text.

Detects whether text is English, Hindi, or mixed (Hinglish).
Uses character-based heuristics — no ML model needed.
"""

import re
from typing import Literal

# Devanagari Unicode range
DEVANAGARI_PATTERN = re.compile(r"[\u0900-\u097F]")
# Basic Latin letters
LATIN_PATTERN = re.compile(r"[a-zA-Z]")
# Common Hindi words in romanized form (Hinglish markers)
HINGLISH_MARKERS = {
    "hai", "hain", "nahi", "kya", "mein", "aur", "ka", "ki", "ke",
    "ko", "se", "par", "yeh", "woh", "hum", "tum", "aap", "kaise",
    "kyun", "kab", "kahan", "kaun", "lekin", "agar", "toh", "bhi",
    "abhi", "bahut", "accha", "theek", "haan", "ji", "matlab",
    "padhai", "paisa", "kaam", "desh", "ghar", "wapas", "samjh",
    "bata", "chalo", "dekho", "suno", "mujhe", "unka", "unki",
    "main", "hoon", "raha", "rahi", "rahe", "kar", "karna",
    "chahta", "chahti", "chahte", "tha", "thi", "the",
    "kuch", "sab", "apna", "apni", "apne", "isko", "usko",
    "mera", "meri", "mere", "tera", "teri", "tere",
}


def detect_language(text: str) -> Literal["en", "hi", "mixed"]:
    """Detect language of transcribed text.

    Args:
        text: The transcribed text string

    Returns:
        "en" for English, "hi" for Hindi, "mixed" for Hinglish/code-mixed
    """
    if not text or not text.strip():
        return "en"  # Default

    # Check for Devanagari characters
    devanagari_count = len(DEVANAGARI_PATTERN.findall(text))
    latin_count = len(LATIN_PATTERN.findall(text))
    total_chars = devanagari_count + latin_count

    if total_chars == 0:
        return "en"

    devanagari_ratio = devanagari_count / total_chars

    # Pure Devanagari
    if devanagari_ratio > 0.7:
        return "hi"

    # Pure Latin — check for romanized Hindi
    if devanagari_ratio < 0.1:
        hindi_word_count = _count_hinglish_words(text)
        total_words = len(text.split())
        if total_words > 0 and hindi_word_count / total_words > 0.3:
            return "mixed"
        return "en"

    # Mix of both scripts
    return "mixed"


def detect_language_from_audio_start(text: str) -> Literal["en", "hi", "mixed"]:
    """Detect primary language from the first few words (1-2 seconds of speech).

    Used to set the initial session language.
    """
    words = text.strip().split()[:10]  # First ~10 words
    if not words:
        return "en"
    return detect_language(" ".join(words))


def _count_hinglish_words(text: str) -> int:
    """Count recognized Hindi/Hinglish words in romanized text."""
    words = text.lower().split()
    return sum(1 for w in words if w.strip(".,!?") in HINGLISH_MARKERS)
