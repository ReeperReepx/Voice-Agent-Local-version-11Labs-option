"""Response validator for LLM output.

Rejects scripted answers, hallucinated facts, and immigration advice.
All checks are rule-based — no ML models needed.
"""

import re
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of validating an LLM response."""
    is_valid: bool
    reason: str = ""
    blocked_category: str = ""


# Patterns that indicate scripted answer coaching
SCRIPTED_ANSWER_PATTERNS = [
    r"(?:you\s+should\s+say|say\s+(?:this|exactly)|tell\s+(?:them|the\s+officer))\s+[\"']",
    r"(?:here'?s?\s+(?:a\s+)?(?:the\s+)?(?:perfect|ideal|best|model)\s+answer)",
    r"(?:memorize|repeat\s+after\s+me|copy\s+this)",
    r"(?:the\s+(?:correct|right|perfect)\s+answer\s+is)",
    r"(?:just\s+say|simply\s+say|you\s+can\s+say)\s*:\s*[\"']",
]

# Patterns that indicate immigration/legal advice
LEGAL_ADVICE_PATTERNS = [
    r"(?:you\s+(?:should|can|could)\s+(?:apply\s+for|get|obtain)\s+(?:a\s+)?(?:green\s+card|permanent\s+residenc|citizenship|pr\b|work\s+permit))",
    r"(?:(?:legal(?:ly)?|law)\s+(?:you\s+)?(?:can|should|are\s+(?:allowed|entitled)))",
    r"(?:hire\s+(?:a\s+|an\s+)?(?:lawyer|attorney|immigration\s+consultant))",
    r"(?:(?:immigration|visa)\s+(?:law|regulation|rule)\s+(?:says|states|allows|permits))",
    r"(?:under\s+(?:section|title|act|ina)\s+\d)",
    r"(?:i\s+(?:guarantee|promise|assure)\s+(?:you(?:'ll)?|that)\s+(?:your\s+)?visa\s+(?:will|would)\s+be\s+(?:approved|granted))",
]

# Patterns that suggest hallucinated/fabricated facts
HALLUCINATION_PATTERNS = [
    r"(?:the\s+(?:visa\s+)?(?:fee|cost)\s+is\s+(?:exactly\s+)?\$?\d{1,3}(?:,\d{3})*)",
    r"(?:(?:processing|wait)\s+time\s+is\s+(?:exactly\s+)?\d+\s+(?:days|weeks|months))",
    r"(?:(?:the\s+)?(?:success|approval|acceptance)\s+rate\s+is\s+\d+%)",
    r"(?:according\s+to\s+(?:my|our)\s+(?:data|records|statistics))",
    r"(?:(?:the|this)\s+(?:embassy|consulate)\s+(?:always|never)\s+(?:approves|rejects|asks))",
]


def validate_response(text: str) -> ValidationResult:
    """Validate an LLM response against all safety rules.

    Returns ValidationResult with is_valid=False if any rule is violated.
    """
    lower = text.lower()

    # Check for scripted answers
    for pattern in SCRIPTED_ANSWER_PATTERNS:
        if re.search(pattern, lower):
            return ValidationResult(
                is_valid=False,
                reason="Response contains scripted answer coaching",
                blocked_category="scripted_answer",
            )

    # Check for legal/immigration advice
    for pattern in LEGAL_ADVICE_PATTERNS:
        if re.search(pattern, lower):
            return ValidationResult(
                is_valid=False,
                reason="Response contains immigration or legal advice",
                blocked_category="legal_advice",
            )

    # Check for hallucinated facts
    for pattern in HALLUCINATION_PATTERNS:
        if re.search(pattern, lower):
            return ValidationResult(
                is_valid=False,
                reason="Response contains potentially fabricated specific facts",
                blocked_category="hallucination",
            )

    return ValidationResult(is_valid=True)


def get_safe_fallback(blocked_category: str) -> str:
    """Return a safe fallback response when the original is blocked."""
    fallbacks = {
        "scripted_answer": (
            "I cannot provide you with a scripted answer. "
            "Let me help you understand what the officer is looking for, "
            "and you can formulate your own authentic response."
        ),
        "legal_advice": (
            "I am not able to provide immigration or legal advice. "
            "For specific visa rules and regulations, please consult "
            "the official embassy website or a licensed immigration consultant."
        ),
        "hallucination": (
            "Let me rephrase that without specific figures. "
            "For exact fees, processing times, or statistics, "
            "please check the official embassy or government website."
        ),
    }
    return fallbacks.get(blocked_category, "Let me rephrase my response.")
