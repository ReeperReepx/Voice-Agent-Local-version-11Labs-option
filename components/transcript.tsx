"use client"

import { useEffect, useRef } from "react"

interface Message {
  role: "agent" | "user"
  text: string
}

export function Transcript({ messages }: { messages: Message[] }) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  if (messages.length === 0) return null

  return (
    <div className="rounded-lg bg-secondary/50 border border-border p-4 max-h-72 overflow-y-auto">
      <div className="space-y-3">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex gap-2 text-sm leading-relaxed ${
              msg.role === "agent" ? "text-primary" : "text-foreground"
            }`}
          >
            <span className="font-semibold text-xs uppercase shrink-0 pt-0.5 w-10">
              {msg.role === "agent" ? "Riya" : "You"}
            </span>
            <span>{msg.text}</span>
          </div>
        ))}
      </div>
      <div ref={bottomRef} />
    </div>
  )
}
