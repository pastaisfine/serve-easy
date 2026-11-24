import { LoadingRing } from "@/components/ui/loading-ring"

export function LoadingScreen() {
  return (
    <main className="fixed inset-0 z-[9999] flex min-h-svh items-center justify-center bg-background">
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

export default function Loading() {
  return <LoadingScreen />
}
