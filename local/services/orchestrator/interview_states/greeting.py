"""Greeting state: identity confirmation and introduction."""


def get_entry_message(context) -> str:
    """Generate greeting when entering this state."""
    return (
        "Good morning. I am your visa interview officer today. "
        "This is a practice session to help you prepare for your student visa interview. "
        "Please state your name and the country you wish to study in."
    )


def get_exit_message() -> str:
    return "Thank you. Let us proceed to discuss your academic background."


def select_questions(country_code: str) -> list[str]:
    """Questions for the greeting phase."""
    return [
        "Please state your full name.",
        "Which country are you planning to study in?",
        "What program are you applying for?",
    ]


def evaluate_answer(answer: str) -> dict:
    """Evaluate answer quality for this state."""
    words = answer.strip().split()
    if len(words) < 2:
        return {"score": 0.3, "feedback": "Please provide a more complete response."}
    return {"score": 0.8, "feedback": "Good, let's continue."}
