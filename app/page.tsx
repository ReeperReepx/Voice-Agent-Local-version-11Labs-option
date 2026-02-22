import { InterviewCoach } from "@/components/interview-coach"

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center px-4 py-10">
      <header className="text-center mb-8">
        <h1 className="text-3xl font-bold text-foreground tracking-tight text-balance">
          Visa<span className="text-primary">Wire</span>
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          AI-powered interview prep coach -- Talk to Riya
        </p>
      </header>

      <InterviewCoach />
    </main>
  )
}
