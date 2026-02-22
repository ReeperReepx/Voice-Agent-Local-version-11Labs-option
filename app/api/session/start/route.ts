import { NextResponse } from "next/server"
import { createSession } from "@/lib/session"
import { buildSystemPrompt, getSignedUrl } from "@/lib/agent"

export async function POST() {
  const sessionId = crypto.randomUUID().slice(0, 8)
  const agentId = process.env.ELEVENLABS_AGENT_ID || ""

  let signedUrl: string | null = null
  try {
    signedUrl = await getSignedUrl()
  } catch {
    // Fall back to public agent_id
  }

  createSession(sessionId)

  return NextResponse.json({
    session_id: sessionId,
    agent_id: agentId,
    signed_url: signedUrl,
    system_prompt: buildSystemPrompt(),
  })
}
