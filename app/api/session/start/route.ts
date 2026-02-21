import { NextResponse } from "next/server";
import { createSession } from "@/lib/session-store";
import { buildSystemPrompt } from "@/lib/questions";

export async function POST() {
  const sessionId = Math.random().toString(36).substring(2, 10);
  const agentId = process.env.ELEVENLABS_AGENT_ID || "";
  const apiKey = process.env.ELEVENLABS_API_KEY || "";

  createSession(sessionId);

  // Try to get a signed URL for the agent
  let signedUrl: string | null = null;
  if (apiKey && agentId) {
    try {
      const res = await fetch(
        `https://api.elevenlabs.io/v1/convai/conversation/get-signed-url?agent_id=${agentId}`,
        {
          headers: { "xi-api-key": apiKey },
        }
      );
      if (res.ok) {
        const data = await res.json();
        signedUrl = data.signed_url;
      }
    } catch {
      // Signed URL is optional; fall back to public agent_id
    }
  }

  return NextResponse.json({
    session_id: sessionId,
    agent_id: agentId,
    signed_url: signedUrl,
    system_prompt: buildSystemPrompt(),
  });
}
