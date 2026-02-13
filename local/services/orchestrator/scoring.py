"""Per-question scoring and overall assessment.

Scores are continuous (0.0–1.0) and hidden from the user during the interview.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class QuestionScore:
    """Score for a single question."""
    question_id: int
    score: float  # 0.0 to 1.0
    category: str = ""
    feedback: str = ""
    retries: int = 0
    contradiction_detected: bool = False


@dataclass
class InterviewScorer:
    """Tracks and computes scores across the interview."""
    scores: dict[int, QuestionScore] = field(default_factory=dict)

    def record_score(
        self,
        question_id: int,
        score: float,
        category: str = "",
        feedback: str = "",
        retries: int = 0,
    ) -> None:
        """Record or update a score for a question."""
        score = max(0.0, min(1.0, score))  # Clamp to [0, 1]
        self.scores[question_id] = QuestionScore(
            question_id=question_id,
            score=score,
            category=category,
            feedback=feedback,
            retries=retries,
        )

    def update_score(self, question_id: int, new_score: float) -> None:
        """Update an existing score (e.g., after retry)."""
        if question_id in self.scores:
            self.scores[question_id].score = max(0.0, min(1.0, new_score))

    def mark_contradiction(self, question_id: int) -> None:
        """Mark a question as having a contradiction detected."""
        if question_id in self.scores:
            self.scores[question_id].contradiction_detected = True
            # Penalize score for contradiction
            current = self.scores[question_id].score
            self.scores[question_id].score = max(0.0, current - 0.2)

    def get_average_score(self) -> float:
        """Compute overall average score."""
        if not self.scores:
            return 0.0
        return sum(s.score for s in self.scores.values()) / len(self.scores)

    def get_category_scores(self) -> dict[str, float]:
        """Compute average score per category."""
        categories: dict[str, list[float]] = {}
        for s in self.scores.values():
            if s.category:
                categories.setdefault(s.category, []).append(s.score)
        return {cat: sum(scores) / len(scores) for cat, scores in categories.items()}

    def get_weak_areas(self, threshold: float = 0.5) -> list[QuestionScore]:
        """Get questions scored below threshold."""
        return [s for s in self.scores.values() if s.score < threshold]

    def get_strong_areas(self, threshold: float = 0.7) -> list[QuestionScore]:
        """Get questions scored above threshold."""
        return [s for s in self.scores.values() if s.score >= threshold]

    def get_contradictions(self) -> list[QuestionScore]:
        """Get all questions with contradictions."""
        return [s for s in self.scores.values() if s.contradiction_detected]

    def generate_report(self) -> dict:
        """Generate a summary report."""
        avg = self.get_average_score()
        if avg >= 0.7:
            readiness = "Well Prepared"
        elif avg >= 0.5:
            readiness = "Needs Improvement"
        else:
            readiness = "Needs Significant Preparation"

        return {
            "average_score": round(avg, 2),
            "total_questions": len(self.scores),
            "readiness": readiness,
            "category_scores": {
                k: round(v, 2) for k, v in self.get_category_scores().items()
            },
            "weak_areas": [
                {"question_id": s.question_id, "score": s.score, "category": s.category}
                for s in self.get_weak_areas()
            ],
            "contradictions": [
                {"question_id": s.question_id, "score": s.score}
                for s in self.get_contradictions()
            ],
        }
