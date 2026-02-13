"""Contradiction tracker: detect inconsistencies across answers.

Tracks key claims (financial, intent, academic) and flags when
a later answer contradicts an earlier one.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class Claim:
    """A factual claim extracted from an answer."""
    question_id: int
    category: str
    key: str  # e.g., "sponsor", "return_plan", "gpa"
    value: str
    raw_answer: str


@dataclass
class Contradiction:
    """A detected contradiction between two claims."""
    claim_a: Claim
    claim_b: Claim
    reason: str


# Keywords to extract claims from
CLAIM_EXTRACTORS = {
    "sponsor": [
        r"(?:my\s+)?(?:father|mother|dad|mom|parent|uncle|aunt|brother|sister|sponsor)\s+(?:is|will)\s+(?:paying|funding|sponsoring)",
        r"(?:sponsor(?:ed)?|fund(?:ed)?)\s+by\s+(?:my\s+)?(\w+)",
    ],
    "return_plan": [
        r"(?:i\s+will|i\s+plan\s+to|i\s+want\s+to)\s+(return|come\s+back|go\s+back|stay|settle|remain)",
    ],
    "income": [
        r"(?:income|salary|earning).*?(\d[\d,]+)",
        r"(\d[\d,]+).*?(?:per\s+(?:month|year|annum))",
    ],
    "degree": [
        r"(?:i\s+(?:have|completed|did|studied))\s+(?:a\s+)?(?:bachelor|master|btech|bsc|msc|mba|phd|diploma)",
        r"(?:bachelor|master|btech|bsc|msc|mba|phd|diploma)(?:'?s?)?\s+(?:in|of)\s+(\w[\w\s]+)",
    ],
}


class ContradictionTracker:
    """Track claims and detect contradictions across interview answers."""

    def __init__(self):
        self.claims: list[Claim] = []
        self.contradictions: list[Contradiction] = []

    def extract_and_track(self, question_id: int, category: str, answer: str) -> list[Contradiction]:
        """Extract claims from an answer and check for contradictions.

        Returns list of newly detected contradictions.
        """
        new_contradictions = []
        lower = answer.lower()

        for claim_key, patterns in CLAIM_EXTRACTORS.items():
            for pattern in patterns:
                match = re.search(pattern, lower)
                if match:
                    value = match.group(0)
                    new_claim = Claim(
                        question_id=question_id,
                        category=category,
                        key=claim_key,
                        value=value,
                        raw_answer=answer,
                    )
                    # Check against existing claims with same key
                    for existing in self.claims:
                        if existing.key == claim_key and existing.question_id != question_id:
                            contradiction = self._check_contradiction(existing, new_claim)
                            if contradiction:
                                self.contradictions.append(contradiction)
                                new_contradictions.append(contradiction)

                    self.claims.append(new_claim)
                    break  # One claim per key per answer

        return new_contradictions

    def _check_contradiction(self, claim_a: Claim, claim_b: Claim) -> Contradiction | None:
        """Check if two claims about the same topic contradict each other."""
        if claim_a.key == "return_plan":
            return self._check_return_plan_contradiction(claim_a, claim_b)
        if claim_a.key == "sponsor":
            return self._check_sponsor_contradiction(claim_a, claim_b)
        if claim_a.key == "income":
            return self._check_income_contradiction(claim_a, claim_b)
        return None

    def _check_return_plan_contradiction(self, a: Claim, b: Claim) -> Contradiction | None:
        """Check for contradictory return plans."""
        stay_words = {"stay", "settle", "remain"}
        return_words = {"return", "come back", "go back"}

        a_stay = any(w in a.value for w in stay_words)
        a_return = any(w in a.value for w in return_words)
        b_stay = any(w in b.value for w in stay_words)
        b_return = any(w in b.value for w in return_words)

        if (a_stay and b_return) or (a_return and b_stay):
            return Contradiction(
                claim_a=a,
                claim_b=b,
                reason="Contradictory return/stay intentions detected",
            )
        return None

    def _check_sponsor_contradiction(self, a: Claim, b: Claim) -> Contradiction | None:
        """Check for different sponsors mentioned."""
        # Simple check: if the sponsor values are significantly different
        if a.value != b.value:
            # Only flag if they mention different family members
            family = {"father", "mother", "uncle", "aunt", "brother", "sister", "parent"}
            a_family = family.intersection(a.value.split())
            b_family = family.intersection(b.value.split())
            if a_family and b_family and a_family != b_family:
                return Contradiction(
                    claim_a=a,
                    claim_b=b,
                    reason="Different financial sponsors mentioned in different answers",
                )
        return None

    def _check_income_contradiction(self, a: Claim, b: Claim) -> Contradiction | None:
        """Check for significantly different income figures."""
        def extract_number(text: str) -> int | None:
            nums = re.findall(r"(\d[\d,]*)", text)
            if nums:
                return int(nums[0].replace(",", ""))
            return None

        a_num = extract_number(a.value)
        b_num = extract_number(b.value)

        if a_num and b_num:
            ratio = max(a_num, b_num) / max(min(a_num, b_num), 1)
            if ratio > 2.0:  # More than 2x difference
                return Contradiction(
                    claim_a=a,
                    claim_b=b,
                    reason=f"Significantly different income figures: {a_num} vs {b_num}",
                )
        return None

    def has_contradictions(self) -> bool:
        return len(self.contradictions) > 0

    def get_all_contradictions(self) -> list[Contradiction]:
        return self.contradictions.copy()
