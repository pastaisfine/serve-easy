"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  ClipboardListIcon,
  HouseIcon,
  MailIcon,
  CircleUserRoundIcon,
  type LucideIcon,
} from "lucide-react"

import { CreateDropdown, CreateSheet } from "@/components/serve/create-menu"
import { Logo } from "@/components/serve/logo"
import { cn } from "@/lib/utils"

interface Tab {
  href: string
  label: string
  icon: LucideIcon
  badge?: number
}

function isActive(pathname: string, href: string) {
  return href === "/" ? pathname === "/" : pathname.startsWith(href)
}

function CountBadge({
  count,
  className,
}: {
  count: number
  className?: string
}) {
  return (
    <span
      className={cn(
        "flex min-w-5 items-center justify-center rounded-full bg-notify px-1.5 text-xs leading-5 font-semibold text-white",
        className
      )}
    >
      {count}
      <span className="sr-only"> unread</span>
    </span>
  )
}

/**
 * Mobile: Fiverr-style floating bottom bar with '+' in the centre.
 * Desktop (md+): a plain top bar with the same destinations.
 */
export function AppNav({ inboxCount }: { inboxCount: number }) {
  const pathname = usePathname()

  const left: Tab[] = [
    { href: "/", label: "Home", icon: HouseIcon },
    { href: "/inbox", label: "Inbox", icon: MailIcon, badge: inboxCount },
  ]
  const right: Tab[] = [
    { href: "/orders", label: "Orders", icon: ClipboardListIcon },
    { href: "/profile", label: "Profile", icon: CircleUserRoundIcon },
  ]

  const mobileTab = ({ href, label, icon: Icon, badge }: Tab) => {
    const active = isActive(pathname, href)
    return (
      <Link
        key={href}
        href={href}
        aria-label={label}
        aria-current={active ? "page" : undefined}
        className={cn(
          "relative flex h-14 flex-1 items-center justify-center rounded-full transition-colors focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none",
          active
            ? "bg-muted text-foreground"
            : "text-foreground/80 hover:text-foreground"
        )}
      >
        <Icon className="size-6" strokeWidth={active ? 2.5 : 2} />
        {badge ? (
          <CountBadge
            count={badge}
            className="absolute top-1.5 right-[calc(50%-1.5rem)]"
          />
        ) : null}
      </Link>
    )
  }

  return (
    <>
      {/* Desktop top bar */}
      <header className="sticky top-0 z-40 hidden border-b bg-background/95 md:block">
        <div className="mx-auto flex h-16 max-w-6xl items-center gap-8 px-8">
          <Logo className="text-2xl" />
          <nav aria-label="Main" className="flex items-center gap-1">
            {[...left, ...right].map(({ href, label, badge }) => {
              const active = isActive(pathname, href)
              return (
                <Link
                  key={href}
                  href={href}
                  aria-current={active ? "page" : undefined}
                  className={cn(
                    "flex h-10 items-center gap-2 rounded-xl px-3 text-sm font-medium transition-colors focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none",
                    active
                      ? "bg-muted text-foreground"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  )}
                >
                  {label}
                  {badge ? <CountBadge count={badge} /> : null}
                </Link>
              )
            })}
          </nav>
          <div className="ml-auto">
            <CreateDropdown />
          </div>
        </div>
      </header>

      {/* Mobile bottom bar */}
      <nav
        aria-label="Main"
        className="fixed inset-x-4 bottom-[max(1rem,env(safe-area-inset-bottom))] z-40 flex items-center gap-1 rounded-full bg-card p-1.5 shadow-[0_8px_30px_rgb(0_0_0/0.12)] md:hidden"
      >
        {left.map(mobileTab)}
        <div className="flex flex-1 justify-center">
          <CreateSheet />
        </div>
        {right.map(mobileTab)}
      </nav>
    </>
  )
}
