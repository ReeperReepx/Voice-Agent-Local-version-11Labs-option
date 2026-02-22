import { NextResponse } from "next/server"
import { getSession, endSession } from "@/lib/session"
import { generateFeedback } from "@/lib/feedback"

export async function POST(
  _request: Request,
  { params }: { params: Promise<{ sessionId: string }> }
) {
  const { sessionId } = await params
  const session = getSession(sessionId)

  if (!session) {
    return NextResponse.json({ error: "Session not found" }, { status: 404 })
  }

  endSession(session)
  const feedback = generateFeedback(session)
  return NextResponse.json(feedback)
}
