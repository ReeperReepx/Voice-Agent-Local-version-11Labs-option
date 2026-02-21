"use client";

import { cn } from "@/lib/utils";
import { Clock, BarChart3, Languages, TrendingUp } from "lucide-react";

export interface FeedbackData {
  session_id: string;
  duration_minutes: number;
  total_questions_faced: number;
  english_proficiency: string;
  english_response_ratio: number;
  language_switches: number;
  questions_needing_hindi_help: number[];
  hindi_responses: number;
  improvements: string[];
  summary: string;
}

function StatCard({
  icon: Icon,
  label,
  value,
  accent = false,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string | number;
  accent?: boolean;
}) {
  return (
    <div className="flex items-center gap-3 rounded-lg bg-muted px-4 py-3">
      <Icon
        className={cn("h-5 w-5", accent ? "text-primary" : "text-muted-foreground")}
      />
      <div className="flex flex-col">
        <span className="text-xs text-muted-foreground">{label}</span>
        <span className="text-sm font-semibold text-foreground">{value}</span>
      </div>
    </div>
  );
}

export function FeedbackPanel({ feedback }: { feedback: FeedbackData }) {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-2">
        <h2 className="text-lg font-semibold text-foreground">Session Summary</h2>
        <p className="text-sm text-muted-foreground">
          Here is how your practice session went.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <StatCard
          icon={Clock}
          label="Duration"
          value={`${feedback.duration_minutes} min`}
        />
        <StatCard
          icon={BarChart3}
          label="Proficiency"
          value={feedback.english_proficiency}
          accent
        />
        <StatCard
          icon={Languages}
          label="Hindi Help"
          value={`${feedback.language_switches} time(s)`}
        />
        <StatCard
          icon={TrendingUp}
          label="English Ratio"
          value={`${Math.round(feedback.english_response_ratio * 100)}%`}
          accent
        />
      </div>

      {feedback.improvements.length > 0 && (
        <div className="flex flex-col gap-2">
          <h3 className="text-sm font-semibold text-foreground">
            Areas for Improvement
          </h3>
          <ul className="flex flex-col gap-2">
            {feedback.improvements.map((imp, i) => (
              <li
                key={i}
                className="rounded-lg border border-border bg-muted px-4 py-3 text-sm leading-relaxed text-muted-foreground"
              >
                {imp}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="rounded-lg border border-border bg-muted p-4">
        <pre className="whitespace-pre-wrap font-mono text-xs leading-relaxed text-muted-foreground">
          {feedback.summary}
        </pre>
      </div>
    </div>
  );
}
