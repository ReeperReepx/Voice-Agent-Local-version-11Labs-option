"""Adaptive question ranking for visa interview sessions.

Selects the next question based on performance scores, difficulty progression,
risk factors, and re-ask logic for weak answers.
"""

from typing import Optional

from services.visa_db.retrieval import (
    get_questions_by_country,
    get_risk_factors,
    get_followups,
)


class QuestionRanker:
    """Selects questions adaptively based on interview performance."""

    @staticmethod
    def _compute_target_difficulty(scores: dict[int, float]) -> int:
        """Map average score to a target difficulty level (1-3).

        Args:
            scores: Mapping of question_id -> score (0.0 to 1.0).

        Returns:
            1 (easy), 2 (moderate), or 3 (advanced).
        """
        if not scores:
            return 1

        avg = sum(scores.values()) / len(scores)
        if avg >= 0.7:
            return 3  # advanced
        elif avg >= 0.4:
            return 2  # moderate
        else:
            return 1  # easy

    @staticmethod
    def _get_risk_bump(
        country: str,
        origin: Optional[str],
        db_path: Optional[str] = None,
    ) -> int:
        """Return +1 difficulty bump if origin has high scrutiny (level 3).

        Args:
            country: Destination country code.
            origin: Origin country (e.g., "India").
            db_path: Optional database path override.

        Returns:
            1 if high-scrutiny origin, 0 otherwise.
        """
        if not origin:
            return 0
        try:
            risks = get_risk_factors(country, origin_country=origin, db_path=db_path)
        except ValueError:
            return 0
        for risk in risks:
            if risk.get("scrutiny_level", 0) >= 3:
                return 1
        return 0

    @staticmethod
    def _check_reask(
        scores: dict[int, float],
        asked_ids: set[int],
        questions: list[dict],
    ) -> Optional[dict]:
        """If any answered question scored <= 0.3, return it for re-asking.

        Only returns a question if it hasn't already been re-asked
        (appears in asked_ids exactly once via initial ask).

        Args:
            scores: Mapping of question_id -> score.
            asked_ids: Set of question IDs already asked.
            questions: Full list of available questions.

        Returns:
            The question dict to re-ask, or None.
        """
        questions_by_id = {q["id"]: q for q in questions}
        for qid, score in scores.items():
            if score <= 0.3 and qid in questions_by_id and qid in asked_ids:
                return questions_by_id[qid]
        return None

    @classmethod
    def select_next_question(
        cls,
        country_code: str,
        category: str,
        scores: dict[int, float],
        asked_ids: set[int],
        origin_country: Optional[str] = None,
        db_path: Optional[str] = None,
    ) -> Optional[dict]:
        """Select the next best question for the interview.

        Logic:
        1. Check if any weak answer (score <= 0.3) needs re-asking.
        2. Compute target difficulty from average performance + risk bump.
        3. Filter to unanswered questions at target difficulty.
        4. Fall back to adjacent difficulties if none found.

        Args:
            country_code: Destination country code (e.g., "US").
            category: Question category (e.g., "academics").
            scores: Mapping of question_id -> score (0.0-1.0).
            asked_ids: Set of already-asked question IDs.
            origin_country: Origin country for risk bump calculation.
            db_path: Optional database path override.

        Returns:
            A question dict, or None if no questions remain.
        """
        try:
            questions = get_questions_by_country(
                country_code, category=category, db_path=db_path
            )
        except ValueError:
            return None

        if not questions:
            return None

        # Step 1: Re-ask weak answers
        reask = cls._check_reask(scores, asked_ids, questions)
        if reask is not None:
            return reask

        # Step 2: Compute target difficulty with risk bump
        target = cls._compute_target_difficulty(scores)
        bump = cls._get_risk_bump(country_code, origin_country, db_path)
        target = min(3, target + bump)

        # Step 3: Filter unanswered questions
        unanswered = [q for q in questions if q["id"] not in asked_ids]
        if not unanswered:
            return None

        # Step 4: Try target difficulty, then adjacent
        for difficulty in [target, target - 1, target + 1]:
            if difficulty < 1 or difficulty > 3:
                continue
            matches = [q for q in unanswered if q.get("difficulty_level") == difficulty]
            if matches:
                return matches[0]

        # Last resort: return any unanswered question
        return unanswered[0]

    @classmethod
    def get_followup_for_weak_answer(
        cls,
        question_id: int,
        score: float,
        db_path: Optional[str] = None,
    ) -> Optional[dict]:
        """Get a follow-up question if the answer was weak.

        Args:
            question_id: The parent question ID.
            score: The score for that question (0.0-1.0).
            db_path: Optional database path override.

        Returns:
            A follow-up question dict, or None.
        """
        if score > 0.5:
            return None

        followups = get_followups(question_id, db_path=db_path)
        if not followups:
            return None

        # Return first available follow-up
        return followups[0]
