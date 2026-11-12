import Link from "next/link"

import { cn } from "@/lib/utils"

/** A home section: heading with an optional "See all" link, like Fiverr's. */
export function Section({
  id,
  title,
  seeAllHref,
  className,
  children,
}: {
  id: string
  title: string
  seeAllHref?: string
  className?: string
  children: React.ReactNode
}) {
  const headingId = `${id}-heading`
  return (
    <section
      aria-labelledby={headingId}
      className={cn("flex flex-col gap-4", className)}
    >
      <div className="flex items-baseline justify-between gap-4">
        <h2
          id={headingId}
          className="text-2xl font-semibold tracking-tight md:text-[1.75rem]"
        >
          {title}
        </h2>
        {seeAllHref && (
          <Link
            href={seeAllHref}
            className="shrink-0 text-base font-medium underline underline-offset-4 hover:text-muted-foreground"
          >
            See all<span className="sr-only"> {title.toLowerCase()}</span>
          </Link>
        )}
      </div>
      {children}
    </section>
  )
}

/** Horizontal snap carousel on mobile that bleeds to the screen edge. */
export function Rail({
  className,
  children,
}: {
  className?: string
  children: React.ReactNode
}) {
  return (
    <div
      className={cn(
        "-mx-4 no-scrollbar flex snap-x snap-mandatory scroll-px-4 gap-3 overflow-x-auto px-4 pb-1",
        className
      )}
    >
      {children}
    </div>
  )
}
