import Link from "next/link"

import { cn } from "@/lib/utils"

/** Wordmark: lowercase "serve" with the brand dot, in the spirit of Fiverr's mark. */
export function Logo({ className }: { className?: string }) {
  return (
    <Link
      href="/"
      aria-label="Serve home"
      className={cn(
        "inline-flex items-baseline text-3xl font-extrabold tracking-tighter text-foreground",
        className
      )}
    >
      serve
      <span
        aria-hidden
        className="ml-0.5 size-[0.28em] rounded-full bg-brand"
      />
    </Link>
  )
}
