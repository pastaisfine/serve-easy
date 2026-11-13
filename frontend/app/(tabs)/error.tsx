"use client" // Error boundaries must be Client Components

import { useEffect } from "react"
import { TriangleAlertIcon } from "lucide-react"

import { Button } from "@/components/ui/button"

/** Shown when a tab fails to render, e.g. when the Serve API is unreachable. */
export default function TabsError({
  error,
  retry,
}: {
  error: unknown
  retry: () => void
}) {
  useEffect(() => {
    console.error(error)
  }, [error])

  return (
    <div className="mx-auto flex max-w-6xl flex-col px-4 pt-10 md:px-8 md:pt-14">
      <div className="flex flex-col items-center gap-4 rounded-2xl bg-card px-6 py-16 text-center ring-1 ring-foreground/5">
        <span className="flex size-14 items-center justify-center rounded-full bg-muted">
          <TriangleAlertIcon className="size-6" />
        </span>
        <h1 className="text-2xl font-semibold tracking-tight">
          Couldn&apos;t load this page
        </h1>
        <p className="max-w-sm text-base text-muted-foreground">
          Serve couldn&apos;t reach its server. Check your connection and try
          again.
        </p>
        <Button className="h-11 rounded-xl px-5" onClick={() => retry()}>
          Try again
        </Button>
      </div>
    </div>
  )
}
