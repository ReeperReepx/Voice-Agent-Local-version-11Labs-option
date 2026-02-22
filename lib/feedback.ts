import { SessionLog, durationMinutes } from "./session"

const CATEGORY_MAP: Record<number, string> = {
  1: "study plans",
  2: "financial capability",
  3: "return intent",
  4: "academic background",
  5: "English proficiency",
}

function categoryForQuestion(questionId: number): string {
  return CATEGORY_MAP[questionId] || "general"
}

export function generateFeedback(session: SessionLog) {
  const totalSwitches = session.language_switches.length
  const totalMessages = session.transcript.filter(
    (t) => t.role === "student"
  ).length
  const hindiResponses = session.student_language_usage.hindi
  const englishResponses = session.student_language_usage.english

  let englishRatio = 0
  if (totalMessages > 0) {
    englishRatio = englishResponses / totalMessages
  }

  let proficiency: string
  if (englishRatio >= 0.9) {
    proficiency = "Strong"
  } else if (englishRatio >= 0.7) {
    proficiency = "Good"
  } else if (englishRatio >= 0.5) {
    proficiency = "Needs Improvement"
  } else {
    proficiency = "Weak — practice answering in English"
  }

  const questionsNeedingHelp = [
    ...new Set(session.language_switches.map((s) => s.question_id)),
  ]

  const improvements: string[] = []
  if (totalSwitches > 0) {
    const categories = questionsNeedingHelp
      .map((qid) => categoryForQuestion(qid))
      .join(", ")
    improvements.push(
      `You needed Hindi help on ${totalSwitches} occasion(s). Practice answering questions about: ${categories}`
    )
  }
  if (hindiResponses > 0) {
    improvements.push(
      `You answered ${hindiResponses} question(s) in Hindi. Try to answer fully in English during the real interview.`
    )
  }
  if (totalMessages < 5) {
    improvements.push(
      "You gave very few responses. Practice giving detailed answers."
    )
  }

  const duration = durationMinutes(session)

  const summaryLines = [
    `Interview Duration: ${duration} minutes`,
    `English Proficiency: ${proficiency}`,
    `Hindi Assistance Needed: ${totalSwitches} time(s)`,
    "",
    "Areas for Improvement:",
  ]

  if (improvements.length > 0) {
    for (const imp of improvements) {
      summaryLines.push(`  - ${imp}`)
    }
  } else {
    summaryLines.push("  Great job! No major areas to improve.")
  }

  summaryLines.push("")
  summaryLines.push(
    "Keep practicing — each session will help you feel more confident!"
  )

  return {
    session_id: session.session_id,
    duration_minutes: duration,
    total_questions_faced: totalMessages,
    english_proficiency: proficiency,
    english_response_ratio: Math.round(englishRatio * 100) / 100,
    language_switches: totalSwitches,
    questions_needing_hindi_help: questionsNeedingHelp,
    hindi_responses: hindiResponses,
    improvements,
    summary: summaryLines.join("\n"),
  }
}
