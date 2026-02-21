"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { Mic, Square, RotateCcw } from "lucide-react";
import { StatusIndicator } from "@/components/status-indicator";
import { Transcript, type TranscriptMessage } from "@/components/transcript";
import { FeedbackPanel, type FeedbackData } from "@/components/feedback-panel";
import { cn } from "@/lib/utils";

type SessionStatus =
  | "idle"
  | "connecting"
  | "active"
  | "speaking"
  | "listening"
  | "ended"
  | "error";

export function InterviewSession() {
  const [status, setStatus] = useState<SessionStatus>("idle");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<TranscriptMessage[]>([]);
  const [seconds, setSeconds] = useState(0);
  const [feedback, setFeedback] = useState<FeedbackData | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const conversationRef = useRef<ReturnType<typeof import("@elevenlabs/client").Conversation.startSession> | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const messageIdRef = useRef(0);

  // Timer
  useEffect(() => {
    if (status === "active" || status === "speaking" || status === "listening") {
      timerRef.current = setInterval(() => {
        setSeconds((s) => s + 1);
      }, 1000);
    } else {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [status]);

  const formattedTime = `${String(Math.floor(seconds / 60)).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}`;

  const addMessage = useCallback((role: "agent" | "user", text: string) => {
    messageIdRef.current += 1;
    setMessages((prev) => [
      ...prev,
      { id: String(messageIdRef.current), role, text, timestamp: Date.now() },
    ]);
  }, []);

  const startInterview = useCallback(async () => {
    setErrorMessage(null);
    setStatus("connecting");
    setMessages([]);
    setFeedback(null);
    setSeconds(0);

    // Request mic permission
    try {
      await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch {
      setStatus("error");
      setErrorMessage(
        "Microphone access denied. Please allow microphone access and try again."
      );
      return;
    }

    try {
      // Create server session
      const res = await fetch("/api/session/start", { method: "POST" });
      if (!res.ok) throw new Error("Failed to start session");
      const data = await res.json();
      setSessionId(data.session_id);

      // Dynamically import ElevenLabs client
      const { Conversation } = await import("@elevenlabs/client");

      const sessionOptions: Parameters<typeof Conversation.startSession>[0] = {
        onConnect: () => {
          setStatus("listening");
        },
        onDisconnect: () => {
          // Don't override if we intentionally ended
        },
        onMessage: (message: { source: string; message: string }) => {
          if (message.source === "ai") {
            addMessage("agent", message.message);
          } else if (message.source === "user") {
            addMessage("user", message.message);
          }
        },
        onModeChange: (mode: { mode: string }) => {
          if (mode.mode === "speaking") {
            setStatus("speaking");
          } else {
            setStatus("listening");
          }
        },
        onError: (error: Error) => {
          console.error("Conversation error:", error);
          setStatus("error");
          setErrorMessage("Connection error. Please try again.");
        },
      };

      if (data.signed_url) {
        (sessionOptions as Record<string, unknown>).signedUrl = data.signed_url;
      } else {
        (sessionOptions as Record<string, unknown>).agentId = data.agent_id;
      }

      const conversation = await Conversation.startSession(sessionOptions);
      conversationRef.current = conversation as typeof conversationRef.current;
    } catch (err) {
      setStatus("error");
      setErrorMessage(
        err instanceof Error ? err.message : "Failed to start session"
      );
    }
  }, [addMessage]);

  const stopInterview = useCallback(async () => {
    setStatus("ended");

    // End the ElevenLabs conversation
    if (conversationRef.current) {
      try {
        const conv = await conversationRef.current;
        if (conv && typeof conv.endSession === "function") {
          await conv.endSession();
        }
      } catch (e) {
        console.warn("Error ending conversation:", e);
      }
      conversationRef.current = null;
    }

    // Get feedback from API
    if (sessionId) {
      try {
        const res = await fetch(`/api/session/${sessionId}/end`, {
          method: "POST",
        });
        if (res.ok) {
          const data = await res.json();
          setFeedback(data);
        }
      } catch {
        // Feedback is optional, session still ends
      }
    }
  }, [sessionId]);

  const resetSession = useCallback(() => {
    setStatus("idle");
    setSessionId(null);
    setMessages([]);
    setFeedback(null);
    setSeconds(0);
    setErrorMessage(null);
    conversationRef.current = null;
  }, []);

  const isActive =
    status === "active" || status === "speaking" || status === "listening";
  const isIdle = status === "idle" || status === "error";

  return (
    <div className="flex flex-col gap-6">
      {/* Main Control Card */}
      <div className="rounded-xl border border-border bg-card p-6">
        <div className="flex flex-col items-center gap-5">
          <StatusIndicator status={status} />

          {/* Timer */}
          {(isActive || status === "ended") && (
            <div className="font-mono text-4xl font-light tabular-nums tracking-wider text-foreground">
              {formattedTime}
            </div>
          )}

          {/* Error message */}
          {errorMessage && (
            <p className="text-center text-sm text-destructive">
              {errorMessage}
            </p>
          )}

          {/* Controls */}
          <div className="flex items-center gap-3">
            {isIdle && (
              <button
                onClick={startInterview}
                className="flex items-center gap-2 rounded-lg bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90"
              >
                <Mic className="h-4 w-4" />
                Start Session
              </button>
            )}

            {isActive && (
              <button
                onClick={stopInterview}
                className="flex items-center gap-2 rounded-lg bg-destructive px-6 py-3 text-sm font-semibold text-destructive-foreground transition-opacity hover:opacity-90"
              >
                <Square className="h-4 w-4" />
                End Session
              </button>
            )}

            {status === "ended" && (
              <button
                onClick={resetSession}
                className="flex items-center gap-2 rounded-lg bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90"
              >
                <RotateCcw className="h-4 w-4" />
                New Session
              </button>
            )}
          </div>

          {/* Tip */}
          {isIdle && !errorMessage && (
            <div className="w-full rounded-lg border-l-2 border-primary bg-accent/20 px-4 py-3 text-sm leading-relaxed text-muted-foreground">
              Riya will guide you through interview prep. Just talk naturally
              -- she will ask questions, give feedback, and coach you in
              real-time.
            </div>
          )}
        </div>
      </div>

      {/* Transcript Card */}
      {(isActive || status === "ended") && (
        <div className="rounded-xl border border-border bg-card p-6">
          <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-muted-foreground">
            Transcript
          </h2>
          <Transcript messages={messages} />
        </div>
      )}

      {/* Feedback Card */}
      {feedback && (
        <div className="rounded-xl border border-border bg-card p-6">
          <FeedbackPanel feedback={feedback} />
        </div>
      )}
    </div>
  );
}
