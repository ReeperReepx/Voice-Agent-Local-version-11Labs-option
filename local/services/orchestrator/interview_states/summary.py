"""Summary state: wrap up interview and provide assessment."""


def get_entry_message(context) -> str:
    return "We have covered all the major areas. Let me summarize your performance."


def get_exit_message() -> str:
    return "This concludes your practice interview. Good luck with your real visa interview."


def generate_summary(context) -> dict:
    """Generate interview summary from context."""
    scores = getattr(context, "scores", {})
    total = len(scores)
    if total == 0:
        avg_score = 0.0
    else:
        avg_score = sum(scores.values()) / total

    if avg_score >= 0.7:
        readiness = "Well Prepared"
    elif avg_score >= 0.5:
        readiness = "Needs Some Improvement"
    else:
        readiness = "Needs Significant Improvement"

    weak_areas = [qid for qid, score in scores.items() if score < 0.5]
    strong_areas = [qid for qid, score in scores.items() if score >= 0.7]

    return {
        "average_score": round(avg_score, 2),
        "total_questions": total,
        "readiness": readiness,
        "weak_question_ids": weak_areas,
        "strong_question_ids": strong_areas,
    }
