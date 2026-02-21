import { NextResponse } from "next/server";
import { endSession, generateFeedback, getSession } from "@/lib/session-store";

export async function POST(
  _request: Request,
  { params }: { params: Promise<{ sessionId: string }> }
) {
  const { sessionId } = await params;
  const session = getSession(sessionId);

  if (!session) {
    return NextResponse.json(
      { error: "Session not found" },
      { status: 404 }
    );
  }

  endSession(sessionId);
  const feedback = generateFeedback(session);

  return NextResponse.json(feedback);
}
