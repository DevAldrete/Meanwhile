import { ArrowRight, MoonStar, Sparkles, Star, SunMedium } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

type HeroSectionProps = {
  currentMode: string
  isDarkMode: boolean
  onShuffleMode: () => void
  onToggleTheme: () => void
}

export function HeroSection({
  currentMode,
  isDarkMode,
  onShuffleMode,
  onToggleTheme,
}: HeroSectionProps) {
  return (
    <>
      <header className="reveal brutal-panel flex flex-wrap items-center justify-between gap-3 p-3 md:p-4">
        <div className="flex items-center gap-3">
          <Badge className="badge-sticker" variant="secondary">
            <Star data-icon="inline-start" />
            Meanwhile manages Chaos
          </Badge>
          <p className="text-sm font-medium text-foreground/80">
            Visual AI orchestration with deterministic execution under the hood.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Button variant="outline" size="sm" onClick={onToggleTheme}>
            {isDarkMode ? <SunMedium data-icon="inline-start" /> : <MoonStar data-icon="inline-start" />}
            {isDarkMode ? "Light Brutal" : "Dark Brutal"}
          </Button>
          <Button asChild variant="outline" size="sm">
            <a href="#proof">See Proof First</a>
          </Button>
        </div>
      </header>

      <section className="grid items-start gap-8 md:grid-cols-[1.2fr_0.8fr] md:gap-10">
        <div className="reveal reveal-delay-1 flex flex-col gap-5">
          <Badge className="w-fit" variant="outline">
            Built for AI teams shipping in production
          </Badge>

          <h1 className="display-headline max-w-[22ch] text-5xl font-black tracking-tight md:text-7xl">
            Orchestrate AI chaos without guessing what failed.
          </h1>

          <p className="max-w-[58ch] text-base leading-relaxed text-foreground/80 md:text-lg">
            Meanwhile separates your workflow into a visual canvas, deterministic
            orchestration logic, and resilient non-deterministic activities. You
            get fewer silent failures, clearer accountability, and faster shipping.
          </p>

          <div className="hero-kpis">
            <article className="hero-kpi">
              <strong>Primary CTA:</strong>
              <span>Start Free Canvas</span>
            </article>
            <article className="hero-kpi">
              <strong>Secondary CTA:</strong>
              <span>Watch 3-min Architecture Demo</span>
            </article>
            <article className="hero-kpi">
              <strong>Proof CTA:</strong>
              <span>Inspect Real Execution Logs</span>
            </article>
          </div>

          <div className="cta-stack flex flex-wrap items-center gap-3">
            <Button size="lg">
              Start Free Canvas
              <ArrowRight data-icon="inline-end" />
            </Button>
            <Button asChild variant="outline" size="lg">
              <a href="#pricing">
                Watch 3-min Demo
                <ArrowRight data-icon="inline-end" />
              </a>
            </Button>
            <Button variant="secondary" size="lg" onClick={onShuffleMode}>
              Shuffle Launch Tone
              <Sparkles data-icon="inline-end" />
            </Button>
          </div>

          <Card className="brutal-card rotate-[-1.2deg]">
            <CardHeader>
              <CardTitle className="font-bold">Current launch tone</CardTitle>
              <CardDescription>
                Use this to test messaging styles before publishing.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-xl font-semibold md:text-2xl">{currentMode}</p>
            </CardContent>
            <CardFooter>
              <Badge variant="default">No card required to start</Badge>
            </CardFooter>
          </Card>
        </div>

        <aside className="reveal reveal-delay-2 md:pt-8">
          <Card className="brutal-card brutal-card--tilt">
            <CardHeader>
              <CardTitle className="display-subtitle text-2xl">
                Conversion Strategy
              </CardTitle>
              <CardDescription>
                This page is optimized to move curious visitors into first-run
                workflow builders.
              </CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col gap-3">
              <div className="brutal-list-item">
                <span>Value in 6 words</span>
                <Badge variant="outline">Above the fold</Badge>
              </div>
              <div className="brutal-list-item">
                <span>Risk reversal</span>
                <Badge variant="outline">Free + no card</Badge>
              </div>
              <div className="brutal-list-item">
                <span>Technical proof</span>
                <Badge variant="outline">Logs + replay</Badge>
              </div>
            </CardContent>
            <CardFooter>
              <Button asChild className="w-full" variant="secondary">
                <a href="#proof">Inspect Production Proof</a>
              </Button>
            </CardFooter>
          </Card>
        </aside>
      </section>
    </>
  )
}
