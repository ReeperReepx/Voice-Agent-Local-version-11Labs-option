import { NextResponse } from "next/server"
import { getSession, durationMinutes } from "@/lib/session"

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ sessionId: string }> }
) {
  const { sessionId } = await params
  const session = getSession(sessionId)

  if (!session) {
    return NextResponse.json({ error: "Session not found" }, { status: 404 })
  }

  return NextResponse.json({
    session_id: session.session_id,
    duration_minutes: durationMinutes(session),
    questions_asked: session.questions_asked,
    language_switches: session.language_switches,
    transcript: session.transcript,
    student_language_usage: session.student_language_usage,
  })
}
