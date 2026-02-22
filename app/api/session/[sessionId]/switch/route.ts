import { NextResponse } from "next/server"
import { getSession, addLanguageSwitch } from "@/lib/session"

export async function POST(
  request: Request,
  { params }: { params: Promise<{ sessionId: string }> }
) {
  const { sessionId } = await params
  const session = getSession(sessionId)

  if (!session) {
    return NextResponse.json({ error: "Session not found" }, { status: 404 })
  }

  const body = await request.json()
  addLanguageSwitch(session, body.question_id, body.reason)

  return NextResponse.json({ status: "ok" })
}
