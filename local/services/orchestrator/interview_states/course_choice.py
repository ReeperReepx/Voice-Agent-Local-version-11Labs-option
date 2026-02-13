"""Course choice state: justify university and program selection."""


def get_entry_message(context) -> str:
    return "Now I would like to understand why you chose this particular course and university."


def get_exit_message() -> str:
    return "Thank you. Let us now discuss your financial arrangements."


def evaluate_answer(answer: str) -> dict:
    words = answer.strip().split()
    if len(words) < 5:
        return {"score": 0.3, "feedback": "Your answer is too brief. Please explain your choice in detail."}
    if len(words) < 20:
        return {"score": 0.6, "feedback": "Can you mention specific features of the program?"}
    return {"score": 0.8, "feedback": "Good explanation."}
