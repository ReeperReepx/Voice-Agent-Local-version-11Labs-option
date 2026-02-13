"""Core visa interview questions bank."""

VISA_QUESTIONS = [
    {
        "id": 1,
        "question_en": "Why have you chosen to study in this country instead of studying in India?",
        "hint_hi": "Aapne is desh mein padhne ka faisla kyun kiya? India mein kyun nahi padh rahe?",
        "category": "study_plans",
        "follow_ups": [
            "What specific program have you been accepted into?",
            "How did you hear about this university?",
        ],
    },
    {
        "id": 2,
        "question_en": "How will you fund your education and living expenses?",
        "hint_hi": "Aap apni padhai aur rehne ka kharcha kaise uthayenge? Kaun pay karega?",
        "category": "financial",
        "follow_ups": [
            "Do you have a scholarship or education loan?",
            "What is your family's annual income?",
        ],
    },
    {
        "id": 3,
        "question_en": "What are your plans after completing your studies? Will you return to India?",
        "hint_hi": "Padhai khatam hone ke baad aap kya karenge? Kya aap India wapas aayenge?",
        "category": "return_intent",
        "follow_ups": [
            "Do you have any family ties in the destination country?",
            "What job opportunities exist for you back in India?",
        ],
    },
    {
        "id": 4,
        "question_en": "Can you tell me about your academic background and how it relates to your chosen course?",
        "hint_hi": "Apni padhai ke baare mein bataiye aur yeh course aapke liye kaise relevant hai?",
        "category": "academic",
        "follow_ups": [
            "What was your percentage or GPA in your last qualification?",
            "Have you done any internships or projects in this field?",
        ],
    },
    {
        "id": 5,
        "question_en": "Have you taken any English proficiency tests like IELTS or TOEFL? What was your score?",
        "hint_hi": "Kya aapne IELTS ya TOEFL diya hai? Kitne marks aaye the?",
        "category": "english_proficiency",
        "follow_ups": [
            "Which section did you find most challenging?",
            "How long have you been preparing for this interview?",
        ],
    },
]


def get_all_questions():
    """Return all visa questions."""
    return VISA_QUESTIONS


def get_question_by_id(question_id: int):
    """Return a specific question by ID."""
    for q in VISA_QUESTIONS:
        if q["id"] == question_id:
            return q
    return None


def get_questions_by_category(category: str):
    """Return questions filtered by category."""
    return [q for q in VISA_QUESTIONS if q["category"] == category]
