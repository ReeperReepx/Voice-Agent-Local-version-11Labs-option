"use client"

import { Clock, BarChart3, Languages, TrendingUp } from "lucide-react"

interface FeedbackData {
  session_id: string
  duration_minutes: number
  total_questions_faced: number
  english_proficiency: string
  english_response_ratio: number
  language_switches: number
  hindi_responses: number
  improvements: string[]
  summary: string
}

export function FeedbackSummary({ data }: { data: FeedbackData }) {
  return (
    <div className="space-y-5">
      <h2 className="text-lg font-semibold text-primary">Session Summary</h2>

      <div className="grid grid-cols-2 gap-3">
        <StatCard
          icon={<Clock className="h-4 w-4" />}
          label="Duration"
          value={`${data.duration_minutes} min`}
        />
        <StatCard
          icon={<BarChart3 className="h-4 w-4" />}
          label="Proficiency"
          value={data.english_proficiency}
        />
        <StatCard
          icon={<Languages className="h-4 w-4" />}
          label="Hindi Help"
          value={`${data.language_switches}x`}
        />
        <StatCard
          icon={<TrendingUp className="h-4 w-4" />}
          label="English Ratio"
          value={`${Math.round(data.english_response_ratio * 100)}%`}
        />
      </div>

      {data.improvements.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-muted-foreground">
            Areas for Improvement
          </h3>
          <ul className="space-y-1.5">
            {data.improvements.map((imp, i) => (
              <li
                key={i}
                className="text-sm text-foreground bg-secondary/50 rounded-md px-3 py-2 border-l-2 border-primary"
              >
                {imp}
              </li>
            ))}
          </ul>
        </div>
      )}

      {data.improvements.length === 0 && (
        <p className="text-sm text-muted-foreground bg-secondary/50 rounded-md px-3 py-2 border-l-2 border-primary">
          Great job! No major areas to improve.
        </p>
      )}

      <p className="text-xs text-muted-foreground text-center pt-2">
        Keep practicing -- each session will help you feel more confident!
      </p>
    </div>
  )
}

function StatCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode
  label: string
  value: string
}) {
  return (
    <div className="bg-secondary/50 border border-border rounded-lg px-3 py-3 flex flex-col gap-1">
      <div className="flex items-center gap-1.5 text-muted-foreground">
        {icon}
        <span className="text-xs">{label}</span>
      </div>
      <span className="text-sm font-semibold text-foreground">{value}</span>
    </div>
  )
}
