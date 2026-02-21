import { InterviewSession } from "@/components/interview-session";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center px-4 py-8">
      <header className="mb-8 text-center">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">
          Visa<span className="text-primary">Wire</span>
        </h1>
        <p className="mt-2 text-sm text-muted-foreground">
          AI-powered interview prep coach — Talk to Riya
        </p>
      </header>

      <div className="w-full max-w-xl">
        <InterviewSession />
      </div>

      <footer className="mt-auto pt-12 pb-6 text-center text-xs text-muted-foreground">
        Practice makes perfect. Each session helps build your confidence.
      </footer>
    </main>
  );
}
