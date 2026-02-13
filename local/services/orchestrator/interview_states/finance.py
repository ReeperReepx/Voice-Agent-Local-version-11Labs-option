"""Finance state: verify financial capacity and sponsorship."""


def get_entry_message(context) -> str:
    return "Let us discuss how you will fund your education and living expenses."


def get_exit_message() -> str:
    return "Thank you. Now let us talk about your plans after completing your studies."


def evaluate_answer(answer: str) -> dict:
    words = answer.strip().split()
    if len(words) < 5:
        return {"score": 0.3, "feedback": "Please provide more details about your financial arrangements."}
    # Check for financial keywords
    financial_terms = ["bank", "loan", "sponsor", "income", "savings", "scholarship", "fund", "gic", "blocked"]
    has_specifics = any(term in answer.lower() for term in financial_terms)
    if has_specifics:
        return {"score": 0.8, "feedback": "Good, you mentioned specific financial details."}
    return {"score": 0.5, "feedback": "Can you be more specific about funding sources?"}
