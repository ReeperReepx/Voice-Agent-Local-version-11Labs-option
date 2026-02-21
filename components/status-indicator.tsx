"use client";

import { cn } from "@/lib/utils";

type Status = "idle" | "connecting" | "active" | "speaking" | "listening" | "ended" | "error";

const statusConfig: Record<Status, { label: string; color: string; pulse: boolean }> = {
  idle: { label: "Ready to start", color: "bg-muted-foreground", pulse: false },
  connecting: { label: "Connecting...", color: "bg-warning", pulse: true },
  active: { label: "Connected", color: "bg-success", pulse: false },
  speaking: { label: "Riya is speaking", color: "bg-primary", pulse: true },
  listening: { label: "Riya is listening", color: "bg-success", pulse: true },
  ended: { label: "Session ended", color: "bg-warning", pulse: false },
  error: { label: "Connection error", color: "bg-destructive", pulse: false },
};

export function StatusIndicator({ status }: { status: Status }) {
  const config = statusConfig[status];

  return (
    <div className="flex items-center justify-center gap-2">
      <span className="relative flex h-2.5 w-2.5">
        {config.pulse && (
          <span
            className={cn(
              "absolute inline-flex h-full w-full animate-ping rounded-full opacity-75",
              config.color
            )}
          />
        )}
        <span
          className={cn(
            "relative inline-flex h-2.5 w-2.5 rounded-full",
            config.color
          )}
        />
      </span>
      <span className="text-sm text-muted-foreground">{config.label}</span>
    </div>
  );
}
