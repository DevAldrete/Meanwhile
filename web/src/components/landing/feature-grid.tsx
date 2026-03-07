import type { LucideIcon } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

type Feature = {
  icon: LucideIcon
  title: string
  description: string
  proof: string
}

type FeatureGridProps = {
  features: Feature[]
}

export function FeatureGrid({ features }: FeatureGridProps) {
  return (
    <section id="proof" className="reveal reveal-delay-3 grid gap-4 md:grid-cols-3 md:gap-5">
      {features.map((feature) => {
        const Icon = feature.icon

        return (
          <Card className="brutal-card h-full" key={feature.title}>
            <CardHeader>
              <Badge className="w-fit" variant="secondary">
                <Icon data-icon="inline-start" />
                Feature
              </Badge>
              <CardTitle className="text-xl font-bold">{feature.title}</CardTitle>
              <CardDescription>{feature.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-foreground/70">{feature.proof}</p>
            </CardContent>
          </Card>
        )
      })}
    </section>
  )
}
