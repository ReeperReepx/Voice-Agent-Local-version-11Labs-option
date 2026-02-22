"use client"

import { useEffect, useState } from "react"

export function SessionTimer({ running }: { running: boolean }) {
  const [seconds, setSeconds] = useState(0)

  useEffect(() => {
    if (!running) {
      setSeconds(0)
      return
    }

    const interval = setInterval(() => {
      setSeconds((s) => s + 1)
    }, 1000)

    return () => clearInterval(interval)
  }, [running])

  const m = String(Math.floor(seconds / 60)).padStart(2, "0")
  const s = String(seconds % 60).padStart(2, "0")

  if (!running && seconds === 0) return null

  return (
    <div className="text-center text-4xl font-mono text-foreground tabular-nums tracking-wider py-2">
      {m}:{s}
    </div>
  )
}
