"use client"

import { useState, useCallback, useRef } from "react"
import { Mic, Square, Radio } from "lucide-react"
import { SessionTimer } from "./session-timer"
import { Transcript } from "./transcript"
import { FeedbackSummary } from "./feedback-summary"

type SessionState = "idle" | "connecting" | "active" | "ending" | "ended"

interface TranscriptMsg {
  role: "agent" | "user"
  text: string
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type FeedbackData = any

export function InterviewCoach() {
  const [state, setState] = useState<SessionState>("idle")
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [messages, setMessages] = useState<TranscriptMsg[]>([])
  const [feedback, setFeedback] = useState<FeedbackData | null>(null)
  const [agentMode, setAgentMode] = useState<string>("")
  const [error, setError] = useState<string>("")
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const conversationRef = useRef<any>(null)

  const startInterview = useCallback(async () => {
    setError("")
    setFeedback(null)
    setMessages([])
    setState("connecting")

    try {
      // Request mic permission
      await navigator.mediaDevices.getUserMedia({ audio: true })
    } catch {
      setError("Microphone access denied. Please allow mic access and try again.")
      setState("idle")
      return
    }

    try {
      // Create server session
      const res = await fetch("/api/session/start", { method: "POST" })
      if (!res.ok) throw new Error("Failed to start session")
      const data = await res.json()
      setSessionId(data.session_id)

      // Dynamically import ElevenLabs client
      const { Conversation } = await import(
        "https://esm.sh/@elevenlabs/client@latest"
      )

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const sessionOptions: any = {
        onConnect: () => {
          setState("active")
          setAgentMode("Riya is listening...")
        },
        onDisconnect: () => {
          setAgentMode("Session ended")
        },
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        onMessage: (message: any) => {
          if (message.source === "ai") {
            setMessages((prev) => [
              ...prev,
              { role: "agent", text: message.message },
            ])
          } else if (message.source === "user") {
            setMessages((prev) => [
              ...prev,
              { role: "user", text: message.message },
            ])
          }
        },
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        onModeChange: (mode: any) => {
          if (mode.mode === "speaking") {
            setAgentMode("Riya is speaking...")
          } else {
            setAgentMode("Riya is listening...")
          }
        },
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        onError: (err: any) => {
          console.error("Conversation error:", err)
          setAgentMode("Connection error -- try again")
        },
      }

      if (data.signed_url) {
        sessionOptions.signedUrl = data.signed_url
      } else {
        sessionOptions.agentId = data.agent_id
      }

      conversationRef.current = await Conversation.startSession(sessionOptions)
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to connect to Riya"
      )
      setState("idle")
    }
  }, [])

  const stopInterview = useCallback(async () => {
    setState("ending")
    setAgentMode("")

    // End the ElevenLabs conversation
    if (conversationRef.current) {
      try {
        await conversationRef.current.endSession()
      } catch {
        // Ignore
      }
      conversationRef.current = null
    }

    if (sessionId) {
      try {
        const res = await fetch(`/api/session/${sessionId}/end`, {
          method: "POST",
        })
        if (res.ok) {
          const data = await res.json()
          setFeedback(data)
        }
      } catch {
        // Ignore
      }
    }

    setState("ended")
  }, [sessionId])

  const isActive = state === "active"
  const isConnecting = state === "connecting"
  const isEnding = state === "ending"

  return (
    <div className="flex flex-col gap-5 w-full max-w-xl mx-auto">
      {/* Main session card */}
      <div className="bg-card border border-border rounded-xl p-6 space-y-5">
        {/* Status */}
        <div className="text-center">
          <p
            className={`text-base ${
              isActive
                ? "text-green-400"
                : state === "ended"
                  ? "text-orange-400"
                  : "text-muted-foreground"
            }`}
          >
            {state === "idle" && "Ready to start your session with Riya"}
            {isConnecting && "Connecting to Riya..."}
            {isActive && "Connected -- talk to Riya!"}
            {isEnding && "Generating summary..."}
            {state === "ended" &&
              "Session complete -- review your summary below"}
          </p>
          {agentMode && (
            <p className="text-sm text-primary mt-1 flex items-center justify-center gap-1.5">
              <Radio className="h-3 w-3 animate-pulse" />
              {agentMode}
            </p>
          )}
        </div>

        {/* Timer */}
        <SessionTimer running={isActive} />

        {/* Controls */}
        <div className="flex items-center justify-center gap-3">
          <button
            onClick={startInterview}
            disabled={isActive || isConnecting || isEnding}
            className="flex items-center gap-2 px-6 py-3 rounded-lg bg-primary text-primary-foreground font-semibold text-sm transition-opacity disabled:opacity-40 disabled:cursor-not-allowed hover:opacity-90"
          >
            <Mic className="h-4 w-4" />
            {state === "ended" ? "New Session" : "Start Session"}
          </button>
          <button
            onClick={stopInterview}
            disabled={!isActive}
            className="flex items-center gap-2 px-6 py-3 rounded-lg bg-destructive text-destructive-foreground font-semibold text-sm transition-opacity disabled:opacity-40 disabled:cursor-not-allowed hover:opacity-90"
          >
            <Square className="h-4 w-4" />
            End Session
          </button>
        </div>

        {/* Error */}
        {error && (
          <p className="text-sm text-destructive text-center">{error}</p>
        )}

        {/* Tip */}
        {state === "idle" && (
          <div className="bg-accent border-l-2 border-primary rounded-r-lg px-4 py-3 text-sm text-muted-foreground">
            Riya will guide you through interview prep. Just talk naturally --
            {"she'll"} ask questions, give feedback, and coach you in real-time.
          </div>
        )}
      </div>

      {/* Transcript */}
      {messages.length > 0 && (
        <div className="bg-card border border-border rounded-xl p-5">
          <h3 className="text-sm font-medium text-muted-foreground mb-3">
            Live Transcript
          </h3>
          <Transcript messages={messages} />
        </div>
      )}

      {/* Feedback */}
      {feedback && (
        <div className="bg-card border border-border rounded-xl p-5">
          <FeedbackSummary data={feedback} />
        </div>
      )}
    </div>
  )
}
