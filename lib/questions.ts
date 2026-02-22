export interface VisaQuestion {
  id: number
  question_en: string
  hint_hi: string
  category: string
  follow_ups: string[]
}

export const VISA_QUESTIONS: VisaQuestion[] = [
  {
    id: 1,
    question_en:
      "Why have you chosen to study in this country instead of studying in India?",
    hint_hi:
      "Aapne is desh mein padhne ka faisla kyun kiya? India mein kyun nahi padh rahe?",
    category: "study_plans",
    follow_ups: [
      "What specific program have you been accepted into?",
      "How did you hear about this university?",
    ],
  },
  {
    id: 2,
    question_en: "How will you fund your education and living expenses?",
    hint_hi:
      "Aap apni padhai aur rehne ka kharcha kaise uthayenge? Kaun pay karega?",
    category: "financial",
    follow_ups: [
      "Do you have a scholarship or education loan?",
      "What is your family's annual income?",
    ],
  },
  {
    id: 3,
    question_en:
      "What are your plans after completing your studies? Will you return to India?",
    hint_hi:
      "Padhai khatam hone ke baad aap kya karenge? Kya aap India wapas aayenge?",
    category: "return_intent",
    follow_ups: [
      "Do you have any family ties in the destination country?",
      "What job opportunities exist for you back in India?",
    ],
  },
  {
    id: 4,
    question_en:
      "Can you tell me about your academic background and how it relates to your chosen course?",
    hint_hi:
      "Apni padhai ke baare mein bataiye aur yeh course aapke liye kaise relevant hai?",
    category: "academic",
    follow_ups: [
      "What was your percentage or GPA in your last qualification?",
      "Have you done any internships or projects in this field?",
    ],
  },
  {
    id: 5,
    question_en:
      "Have you taken any English proficiency tests like IELTS or TOEFL? What was your score?",
    hint_hi: "Kya aapne IELTS ya TOEFL diya hai? Kitne marks aaye the?",
    category: "english_proficiency",
    follow_ups: [
      "Which section did you find most challenging?",
      "How long have you been preparing for this interview?",
    ],
  },
]

export function getAllQuestions(): VisaQuestion[] {
  return VISA_QUESTIONS
}

export function getQuestionById(id: number): VisaQuestion | undefined {
  return VISA_QUESTIONS.find((q) => q.id === id)
}

export function getQuestionsByCategory(category: string): VisaQuestion[] {
  return VISA_QUESTIONS.filter((q) => q.category === category)
}
