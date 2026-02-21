export interface SessionMessage {
  role: string;
  text: string;
  language: string;
  timestamp: number;
}

export interface LanguageSwitch {
  question_id: number;
  reason: string;
  timestamp: number;
}

export interface Session {
  session_id: string;
  start_time: number;
  end_time: number | null;
  transcript: SessionMessage[];
  language_switches: LanguageSwitch[];
  student_language_usage: { english: number; hindi: number };
}

// In-memory session store (MVP)
const sessions = new Map<string, Session>();

export function createSession(sessionId: string): Session {
  const session: Session = {
    session_id: sessionId,
    start_time: Date.now(),
    end_time: null,
    transcript: [],
    language_switches: [],
    student_language_usage: { english: 0, hindi: 0 },
  };
  sessions.set(sessionId, session);
  return session;
}

export function getSession(sessionId: string): Session | undefined {
  return sessions.get(sessionId);
}

export function endSession(sessionId: string): Session | undefined {
  const session = sessions.get(sessionId);
  if (session) {
    session.end_time = Date.now();
  }
  return session;
}

export function generateFeedback(session: Session) {
  const totalSwitches = session.language_switches.length;
  const totalMessages = session.transcript.filter(
    (t) => t.role === "student" || t.role === "user"
  ).length;
  const hindiResponses = session.student_language_usage.hindi;
  const englishResponses = session.student_language_usage.english;

  const englishRatio =
    totalMessages === 0 ? 0 : englishResponses / totalMessages;

  let proficiency: string;
  if (englishRatio >= 0.9) proficiency = "Strong";
  else if (englishRatio >= 0.7) proficiency = "Good";
  else if (englishRatio >= 0.5) proficiency = "Needs Improvement";
  else proficiency = "Weak -- practice answering in English";

  const questionsNeedingHelp = [
    ...new Set(session.language_switches.map((s) => s.question_id)),
  ];

  const categoryMap: Record<number, string> = {
    1: "study plans",
    2: "financial capability",
    3: "return intent",
    4: "academic background",
    5: "English proficiency",
  };

  const improvements: string[] = [];
  if (totalSwitches > 0) {
    improvements.push(
      `You needed Hindi help on ${totalSwitches} occasion(s). Practice answering questions about: ${questionsNeedingHelp.map((qid) => categoryMap[qid] || "general").join(", ")}`
    );
  }
  if (hindiResponses > 0) {
    improvements.push(
      `You answered ${hindiResponses} question(s) in Hindi. Try to answer fully in English during the real interview.`
    );
  }
  if (totalMessages < 5) {
    improvements.push(
      "You gave very few responses. Practice giving detailed answers."
    );
  }

  const durationMinutes = session.end_time
    ? Math.round(((session.end_time - session.start_time) / 60000) * 10) / 10
    : 0;

  const summaryLines = [
    `Interview Duration: ${durationMinutes} minutes`,
    `English Proficiency: ${proficiency}`,
    `Hindi Assistance Needed: ${totalSwitches} time(s)`,
    "",
    "Areas for Improvement:",
  ];
  if (improvements.length > 0) {
    for (const imp of improvements) {
      summaryLines.push(`  - ${imp}`);
    }
  } else {
    summaryLines.push("  Great job! No major areas to improve.");
  }
  summaryLines.push("");
  summaryLines.push(
    "Keep practicing -- each session will help you feel more confident!"
  );

  return {
    session_id: session.session_id,
    duration_minutes: durationMinutes,
    total_questions_faced: totalMessages,
    english_proficiency: proficiency,
    english_response_ratio: Math.round(englishRatio * 100) / 100,
    language_switches: totalSwitches,
    questions_needing_hindi_help: questionsNeedingHelp,
    hindi_responses: hindiResponses,
    improvements,
    summary: summaryLines.join("\n"),
  };
}
