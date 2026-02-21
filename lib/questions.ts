export interface VisaQuestion {
  id: number;
  question_en: string;
  hint_hi: string;
  category: string;
  follow_ups: string[];
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
];

export function getAllQuestions(): VisaQuestion[] {
  return VISA_QUESTIONS;
}

export function getQuestionById(id: number): VisaQuestion | undefined {
  return VISA_QUESTIONS.find((q) => q.id === id);
}

export function buildSystemPrompt(): string {
  const questions = getAllQuestions();
  let questionsText = "";
  for (const q of questions) {
    questionsText += `\n${q.id}. ${q.question_en}`;
    questionsText += `\n   Hindi hint: ${q.hint_hi}`;
    for (const fu of q.follow_ups) {
      questionsText += `\n   - Follow-up: ${fu}`;
    }
    questionsText += "\n";
  }

  return `You are a visa interview officer conducting a mock student visa interview.

BEHAVIOR:
- Be professional, neutral, and realistic — like a real visa officer.
- Ask questions in English by default.
- If the student shows confusion (says "Hindi mein samjhao", "I don't understand", gives an off-topic answer, or stays silent for too long), switch to Hindi to explain the question simply, then re-ask in English.
- After a Hindi explanation, say something like: "Let me ask that again in English..." and re-ask.
- Encourage the student to answer in English, but accept Hindi answers (note it internally).
- Ask follow-up questions when answers are vague or incomplete.
- Keep track of which questions needed Hindi help.

QUESTIONS TO ASK (in order):
${questionsText}

FLOW:
1. Greet the student and introduce yourself as the visa officer.
2. Ask each question, listen to the response, ask follow-ups if needed.
3. After all questions, thank the student and end the interview.
4. Summarize how they did.

LANGUAGE SWITCHING RULES:
- Default: English
- Switch trigger: student confusion, explicit Hindi request, silence, off-topic response
- After Hindi help: always re-ask the same question in English
- Track every language switch with the question ID`;
}
