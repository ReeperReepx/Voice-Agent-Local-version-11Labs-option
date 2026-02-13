"""Country-specific state: questions tailored to the destination country."""


def get_entry_message(context) -> str:
    country = getattr(context, "destination_country", "your destination")
    return f"Let me ask a few questions specific to studying in {country}."


def get_exit_message() -> str:
    return "Thank you. We are now approaching the end of this practice interview."


def evaluate_answer(answer: str) -> dict:
    words = answer.strip().split()
    if len(words) < 3:
        return {"score": 0.3, "feedback": "Please provide a more detailed response."}
    if len(words) < 10:
        return {"score": 0.6, "feedback": "Can you elaborate on that?"}
    return {"score": 0.8, "feedback": "Good awareness of country-specific requirements."}
