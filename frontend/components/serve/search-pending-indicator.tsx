"use client"

import { useFormStatus } from "react-dom"

import { LoadingRing } from "@/components/ui/loading-ring"

export function SearchPendingIndicator() {
  const { pending } = useFormStatus()

  if (!pending) return null

  return (
    <span
      role="status"
      className="absolute top-1/2 right-4 -translate-y-1/2 text-muted-foreground"
    >
      <LoadingRing className="size-5" />
      <span className="sr-only">Searching</span>
    </span>
  )
}
