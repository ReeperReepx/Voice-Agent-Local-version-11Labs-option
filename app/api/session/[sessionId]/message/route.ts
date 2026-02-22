import { NextResponse } from "next/server"
import { getSession, addMessage } from "@/lib/session"

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
  addMessage(session, body.role, body.text, body.language || "en")

  return NextResponse.json({ status: "ok" })
}
