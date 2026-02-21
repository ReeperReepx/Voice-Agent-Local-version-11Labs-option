"use client";

import { useEffect, useRef } from "react";
import { cn } from "@/lib/utils";

export interface TranscriptMessage {
  id: string;
  role: "agent" | "user";
  text: string;
  timestamp: number;
}

export function Transcript({ messages }: { messages: TranscriptMessage[] }) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex items-center justify-center py-12 text-sm text-muted-foreground">
        Transcript will appear here once the session starts...
      </div>
    );
  }

  return (
    <div
      ref={scrollRef}
      className="flex max-h-[400px] flex-col gap-3 overflow-y-auto pr-1"
    >
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={cn(
            "flex flex-col gap-1 rounded-lg px-4 py-3",
            msg.role === "agent"
              ? "bg-accent/30 mr-8"
              : "bg-muted ml-8"
          )}
        >
          <span
            className={cn(
              "text-xs font-semibold uppercase tracking-wider",
              msg.role === "agent" ? "text-primary" : "text-muted-foreground"
            )}
          >
            {msg.role === "agent" ? "Riya" : "You"}
          </span>
          <p className="text-sm leading-relaxed text-foreground">{msg.text}</p>
        </div>
      ))}
    </div>
  );
}
