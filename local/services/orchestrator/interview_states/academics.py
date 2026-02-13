"""Academics state: verify academic background and progression."""


def get_entry_message(context) -> str:
    return "Let us discuss your academic background."


def get_exit_message() -> str:
    return "Thank you for sharing your academic details. Let us talk about your course choice."


def evaluate_answer(answer: str) -> dict:
    words = answer.strip().split()
    if len(words) < 5:
        return {"score": 0.4, "feedback": "Could you provide more detail about your academic background?"}
    if len(words) < 15:
        return {"score": 0.6, "feedback": "Can you elaborate further?"}
    return {"score": 0.8, "feedback": "Good."}
