import { useEffect, useMemo, useState } from "react"
import { ArrowRight, BrainCircuit, ScrollText, ShieldCheck } from "lucide-react"

import { Button } from "@/components/ui/button"
import { FeatureGrid } from "@/components/landing/feature-grid"
import { HeroSection } from "@/components/landing/hero-section"

import "./App.css"

const jokeModes = [
  "Launch fast, replay failures later",
  "From messy prompts to deterministic delivery",
  "Ship bold AI automations with calm observability",
  "Build once, retry forever, panic never",
]

const features = [
  {
    icon: BrainCircuit,
    title: "Visual AI orchestration",
    description:
      "Design multi-step AI workflows with loops, branches, and conditions directly on a visual canvas.",
    proof:
      "Non-technical stakeholders can reason about the graph while engineers still keep deterministic backend guarantees.",
  },
  {
    icon: ScrollText,
    title: "Absolute execution transparency",
    description:
      "Track prompts, system instructions, token usage, and raw model outputs for every single node execution.",
    proof:
      "When something fails in production, you get context-rich logs instead of mystery stack traces and blame spirals.",
  },
  {
    icon: ShieldCheck,
    title: "Durable retry engine",
    description:
      "Temporal-backed retries and state tracking make flaky APIs survivable, auditable, and boring to maintain.",
    proof:
      "Teams recover from third-party outages without manually replaying every failed workflow by hand.",
  },
]

function App() {
  const [modeIndex, setModeIndex] = useState(0)
  const [isDarkMode, setIsDarkMode] = useState(false)

  const currentMode = useMemo(() => jokeModes[modeIndex], [modeIndex])

  useEffect(() => {
    document.documentElement.classList.toggle("dark", isDarkMode)
  }, [isDarkMode])

  return (
    <main className="landing min-h-screen">
      <div className="noise-overlay" aria-hidden />
      <div className="float-shape float-shape--a" aria-hidden />
      <div className="float-shape float-shape--b" aria-hidden />

      <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 px-4 py-6 md:px-8 md:py-10">
        <HeroSection
          currentMode={currentMode}
          isDarkMode={isDarkMode}
          onShuffleMode={() => setModeIndex((i) => (i + 1) % jokeModes.length)}
          onToggleTheme={() => setIsDarkMode((value) => !value)}
        />

        <FeatureGrid features={features} />

        <section id="pricing" className="reveal reveal-delay-4 brutal-panel flex flex-col gap-4 p-5 md:flex-row md:items-center md:justify-between md:p-6">
          <div className="flex flex-col gap-2">
            <h2 className="display-subtitle text-3xl font-black md:text-4xl">
              Start free. Upgrade when your workflows become mission-critical.
            </h2>
            <p className="max-w-[58ch] text-foreground/80">
              Primary conversion path: launch one real workflow this week. No
              card required. Transparent pricing when you are ready to scale.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Button size="lg">
              Start Free Canvas
              <ArrowRight data-icon="inline-end" />
            </Button>
            <Button asChild size="lg" variant="outline">
              <a href="#proof">
                See Technical Proof
                <ArrowRight data-icon="inline-end" />
              </a>
            </Button>
          </div>
        </section>
      </div>
    </main>
  )
}

export default App
