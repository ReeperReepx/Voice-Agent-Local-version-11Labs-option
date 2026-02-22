export interface TranscriptMessage {
  role: string
  text: string
  language: string
  timestamp: number
}

export interface LanguageSwitch {
  question_id: number
  reason: string
  timestamp: number
}

export interface SessionLog {
  session_id: string
  start_time: number
  end_time: number | null
  questions_asked: number[]
  language_switches: LanguageSwitch[]
  transcript: TranscriptMessage[]
  student_language_usage: { english: number; hindi: number }
}

// In-memory session store (MVP)
const sessions: Map<string, SessionLog> = new Map()

export function createSession(sessionId: string): SessionLog {
  const session: SessionLog = {
    session_id: sessionId,
    start_time: Date.now() / 1000,
    end_time: null,
    questions_asked: [],
    language_switches: [],
    transcript: [],
    student_language_usage: { english: 0, hindi: 0 },
  }
  sessions.set(sessionId, session)
  return session
}

export function getSession(sessionId: string): SessionLog | undefined {
  return sessions.get(sessionId)
}

export function addMessage(
  session: SessionLog,
  role: string,
  text: string,
  language: string = "en"
) {
  session.transcript.push({
    role,
    text,
    language,
    timestamp: Date.now() / 1000,
  })
  if (role === "student") {
    if (language === "hi") {
      session.student_language_usage.hindi += 1
    } else {
      session.student_language_usage.english += 1
    }
  }
}

export function addLanguageSwitch(
  session: SessionLog,
  questionId: number,
  reason: string
) {
  session.language_switches.push({
    question_id: questionId,
    reason,
    timestamp: Date.now() / 1000,
  })
}

export function endSession(session: SessionLog) {
  session.end_time = Date.now() / 1000
}

export function durationMinutes(session: SessionLog): number {
  const end = session.end_time || Date.now() / 1000
  return Math.round(((end - session.start_time) / 60) * 10) / 10
}
