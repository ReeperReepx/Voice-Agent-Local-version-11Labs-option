"""Intent state: assess immigration intent and return plans."""


def get_entry_message(context) -> str:
    return "I would like to understand your plans after completing your studies."


def get_exit_message() -> str:
    return "Thank you. Let me ask a few questions specific to your destination country."


def evaluate_answer(answer: str) -> dict:
    words = answer.strip().split()
    lower = answer.lower()

    # Red flags for immigration intent
    stay_keywords = ["stay permanently", "settle", "never come back", "immigration", "green card", "pr"]
    has_red_flag = any(kw in lower for kw in stay_keywords)

    if has_red_flag:
        return {"score": 0.3, "feedback": "Your answer suggests permanent immigration intent. A visa officer would probe further."}
    if len(words) < 5:
        return {"score": 0.4, "feedback": "Please elaborate on your post-study plans."}

    return_keywords = ["return", "come back", "home country", "family", "career back", "job at home"]
    has_return_intent = any(kw in lower for kw in return_keywords)

    if has_return_intent:
        return {"score": 0.8, "feedback": "Good, you demonstrate clear return intent."}
    return {"score": 0.6, "feedback": "You could strengthen your answer by mentioning ties to your home country."}
