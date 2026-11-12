import Link from "next/link"
import type { LucideIcon } from "lucide-react"

import { Button } from "@/components/ui/button"

/** Temporary screen for tabs and routes that are not built yet. */
export function PlaceholderPage({
  title,
  description,
  icon: Icon,
}: {
  title: string
  description: string
  icon: LucideIcon
}) {
  return (
    <div className="mx-auto flex max-w-6xl flex-col px-4 pt-10 md:px-8 md:pt-14">
      <h1 className="text-3xl font-semibold tracking-tight">{title}</h1>
      <div className="mt-8 flex flex-col items-center gap-4 rounded-2xl bg-card px-6 py-16 text-center ring-1 ring-foreground/5">
        <span className="flex size-14 items-center justify-center rounded-full bg-muted">
          <Icon className="size-6" />
        </span>
        <p className="max-w-sm text-base text-muted-foreground">
          {description}
        </p>
        <Button
          variant="outline"
          className="h-11 rounded-xl px-5"
          nativeButton={false}
          render={<Link href="/" />}
        >
          Back to home
        </Button>
      </div>
    </div>
  )
}
