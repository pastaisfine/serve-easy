import Link from "next/link"
import { ArrowLeftIcon } from "lucide-react"

/** Title block for inner pages, with a back link. */
export function PageHeader({
  title,
  backHref,
  backLabel,
  children,
}: {
  title: string
  backHref: string
  backLabel: string
  children?: React.ReactNode
}) {
  return (
    <div className="flex flex-col gap-3">
      <Link
        href={backHref}
        className="flex w-fit items-center gap-1.5 rounded-md text-sm font-medium text-muted-foreground hover:text-foreground focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none"
      >
        <ArrowLeftIcon aria-hidden className="size-4" />
        {backLabel}
      </Link>
      <h1 className="text-3xl font-semibold tracking-tight">{title}</h1>
      {children}
    </div>
  )
}
