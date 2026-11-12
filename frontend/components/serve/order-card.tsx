import Image from "next/image"
import Link from "next/link"
import { CalendarClockIcon, MapPinIcon } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Card } from "@/components/ui/card"
import { formatPrice } from "@/lib/format"
import type { Order, OrderStatus } from "@/lib/types"
import { cn } from "@/lib/utils"

const statusLabel: Record<OrderStatus, string> = {
  meetup_today: "Meetup today",
  meetup_scheduled: "Meetup scheduled",
  slot_booked: "Slot booked",
}

export function OrderCard({ order }: { order: Order }) {
  const { listing, counterpart } = order
  const buying = order.role === "buying"

  return (
    <Card className="p-0 ring-foreground/5 transition hover:ring-foreground/15">
      <Link
        href={`/orders/${order.id}`}
        className="flex gap-4 p-4 focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none"
      >
        <div className="relative size-24 shrink-0 overflow-hidden rounded-xl bg-muted ring-1 ring-foreground/5">
          <Image
            src={listing.image}
            alt=""
            fill
            sizes="96px"
            className="object-cover"
          />
        </div>
        <div className="flex min-w-0 flex-1 flex-col gap-1">
          <div className="flex items-start justify-between gap-2">
            <span className="text-lg font-semibold">
              {formatPrice(order.price)}
            </span>
            <Badge
              className={cn(
                "h-6 px-2.5",
                order.status === "meetup_today"
                  ? "bg-brand text-brand-foreground"
                  : "bg-secondary text-secondary-foreground"
              )}
            >
              {statusLabel[order.status]}
            </Badge>
          </div>
          <p className="truncate text-base text-foreground/80">
            {listing.title}
          </p>
          <p className="text-sm text-muted-foreground">
            {buying ? "From" : "To"} {counterpart.name}
          </p>
          <div className="mt-1 flex flex-col gap-1 text-sm text-muted-foreground">
            <span className="flex items-center gap-1.5">
              <CalendarClockIcon aria-hidden className="size-4 shrink-0" />
              {order.when}
            </span>
            <span className="flex items-center gap-1.5">
              <MapPinIcon aria-hidden className="size-4 shrink-0" />
              <span className="truncate">{order.spot}</span>
            </span>
          </div>
          {buying && order.handoverCode && (
            <p className="mt-2 text-sm">
              Handover code{" "}
              <span className="rounded-md bg-muted px-1.5 py-0.5 font-semibold tracking-widest tabular-nums">
                {order.handoverCode}
              </span>
            </p>
          )}
        </div>
      </Link>
    </Card>
  )
}
