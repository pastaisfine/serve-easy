import { LoadingRing } from "@/components/ui/loading-ring"

export default function Loading() {
  return (
    <main className="flex min-h-screen items-center justify-center">
      <div
        role="status"
        className="flex items-center gap-2 text-muted-foreground"
      >
        <LoadingRing />
        <span className="sr-only">Loading</span>
      </div>
    </main>
  )
}
