"""Post-session feedback summary generator."""

from server.agent import SessionLog


def generate_feedback(session: SessionLog) -> dict:
    """Generate a structured feedback report from a session log."""
    total_switches = len(session.language_switches)
    total_messages = len([t for t in session.transcript if t["role"] == "student"])
    hindi_responses = session.student_language_usage.get("hindi", 0)
    english_responses = session.student_language_usage.get("english", 0)

    # English proficiency rating
    if total_messages == 0:
        english_ratio = 0.0
    else:
        english_ratio = english_responses / total_messages

    if english_ratio >= 0.9:
        proficiency = "Strong"
    elif english_ratio >= 0.7:
        proficiency = "Good"
    elif english_ratio >= 0.5:
        proficiency = "Needs Improvement"
    else:
        proficiency = "Weak — practice answering in English"

    # Questions that needed Hindi help
    questions_needing_help = list({s["question_id"] for s in session.language_switches})

    # Build improvement areas
    improvements = []
    if total_switches > 0:
        improvements.append(
            f"You needed Hindi help on {total_switches} occasion(s). "
            f"Practice answering questions about: "
            + ", ".join(
                _category_for_question(qid) for qid in questions_needing_help
            )
        )
    if hindi_responses > 0:
        improvements.append(
            f"You answered {hindi_responses} question(s) in Hindi. "
            "Try to answer fully in English during the real interview."
        )
    if total_messages < 5:
        improvements.append(
            "You gave very few responses. Practice giving detailed answers."
        )

    return {
        "session_id": session.session_id,
        "duration_minutes": session.duration_minutes(),
        "total_questions_faced": total_messages,
        "english_proficiency": proficiency,
        "english_response_ratio": round(english_ratio, 2),
        "language_switches": total_switches,
        "questions_needing_hindi_help": questions_needing_help,
        "hindi_responses": hindi_responses,
        "improvements": improvements,
        "summary": _build_summary_text(
            proficiency, total_switches, improvements, session.duration_minutes()
        ),
    }


def _category_for_question(question_id: int) -> str:
    """Map question ID to its category name."""
    category_map = {
        1: "study plans",
        2: "financial capability",
        3: "return intent",
        4: "academic background",
        5: "English proficiency",
    }
    return category_map.get(question_id, "general")


def _build_summary_text(
    proficiency: str,
    switches: int,
    improvements: list,
    duration: float,
) -> str:
    """Build a human-readable summary string."""
    lines = [
        f"Interview Duration: {duration} minutes",
        f"English Proficiency: {proficiency}",
        f"Hindi Assistance Needed: {switches} time(s)",
        "",
        "Areas for Improvement:",
    ]
    if improvements:
        for imp in improvements:
            lines.append(f"  - {imp}")
    else:
        lines.append("  Great job! No major areas to improve.")

    lines.append("")
    lines.append("Keep practicing — each session will help you feel more confident!")
    return "\n".join(lines)
