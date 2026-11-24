"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { useState, useTransition } from "react"

import {
  changeProductOrderStatus,
  changeServiceBookingStatus,
} from "@/app/(tabs)/orders/actions"
import { ContactLinks } from "@/components/serve/contact-links"
import { Button } from "@/components/ui/button"
import { formatPrice } from "@/lib/format"
import type {
  ApiProductOrder,
  ApiServiceBooking,
  RequestStatus,
} from "@/lib/api"
import { cn } from "@/lib/utils"

type RequestEntry =
  | { kind: "item"; request: ApiProductOrder }
  | { kind: "service"; request: ApiServiceBooking }

function statusName(entry: RequestEntry) {
  const { request } = entry
  if (request.status === "pending") {
    return request.role === "selling" || request.role === "providing"
      ? "Needs your response"
      : "Waiting for a response"
  }
  return {
    accepted: "Accepted",
    declined: "Declined",
    completed: "Completed",
    cancelled: "Cancelled",
  }[request.status]
}

function actionsFor(entry: RequestEntry): {
  status: RequestStatus
  label: string
}[] {
  const { request } = entry
  if (
    (request.role === "buying" || request.role === "requesting") &&
    (request.status === "pending" || request.status === "accepted")
  ) {
    return [{ status: "cancelled", label: "Cancel request" }]
  }
  if (
    (request.role === "selling" || request.role === "providing") &&
    request.status === "pending"
  ) {
    return [
      { status: "accepted", label: "Accept" },
      { status: "declined", label: "Decline" },
    ]
  }
  if (
    (request.role === "selling" || request.role === "providing") &&
    request.status === "accepted"
  ) {
    return [{ status: "completed", label: "Mark complete" }]
  }
  return []
}

function RequestCard({
  entry,
  compact,
}: {
  entry: RequestEntry
  compact: boolean
}) {
  const router = useRouter()
  const [error, setError] = useState("")
  const [isPending, startTransition] = useTransition()
  const { request } = entry
  const title =
    entry.kind === "item"
      ? entry.request.listing_title
      : entry.request.service_title
  const counterpartLabel =
    entry.kind === "item"
      ? entry.request.role === "buying"
        ? "Seller"
        : "Buyer"
      : entry.request.role === "requesting"
        ? "Provider"
        : "Student"
  const href = `/orders/${entry.kind === "item" ? "item" : "booking"}-${request.id}`

  function update(status: RequestStatus) {
    setError("")
    startTransition(async () => {
      const result =
        entry.kind === "item"
          ? await changeProductOrderStatus(request.id, status)
          : await changeServiceBookingStatus(request.id, status)
      if (result.error) {
        setError(result.error)
        return
      }
      router.refresh()
    })
  }

  return (
    <article
      className={cn(
        "flex flex-col gap-3 border-b py-4 last:border-b-0 sm:flex-row sm:items-start sm:justify-between",
        compact && "py-3"
      )}
    >
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-baseline justify-between gap-3">
          <Link
            href={href}
            className="truncate font-medium underline-offset-4 hover:underline focus-visible:underline focus-visible:outline-none"
          >
            {title}
          </Link>
          <span className="shrink-0 font-medium tabular-nums">
            {entry.kind === "item"
              ? formatPrice(Number(entry.request.price))
              : formatPrice(
                  Number(entry.request.service_price),
                  entry.request.service_unit ?? undefined
                )}
          </span>
        </div>
        <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted-foreground">
          <span>
            {counterpartLabel}: {request.counterpart.name}
          </span>
          <span>
            {entry.kind === "item"
              ? entry.request.meetup_spot
              : `Requested ${entry.request.requested_date} · ${entry.request.service_spot}`}
          </span>
        </div>
        <div className="mt-2">
          <ContactLinks
            whatsapp={request.counterpart.whatsapp}
            telegramUsername={request.counterpart.telegram_username}
          />
        </div>
        {!compact && (
          <p className="mt-2 text-sm text-foreground/80">
            {entry.kind === "item"
              ? entry.request.buyer_note ||
                (entry.request.role === "buying"
                  ? "You didn’t add a note."
                  : "The buyer left no note.")
              : entry.request.details}
          </p>
        )}
        {error && (
          <p role="alert" className="mt-2 text-sm text-destructive">
            {error}
          </p>
        )}
      </div>
      <div className="flex shrink-0 flex-wrap items-center gap-2 sm:justify-end">
        <span
          className={cn(
            "rounded-full px-2.5 py-1 text-xs font-medium",
            request.status === "pending"
              ? "bg-secondary text-secondary-foreground"
              : request.status === "accepted"
                ? "bg-brand/15 text-foreground"
                : "bg-muted text-muted-foreground"
          )}
        >
          {statusName(entry)}
        </span>
        {actionsFor(entry).map((action) => (
          <Button
            key={action.status}
            type="button"
            size="sm"
            variant={
              action.status === "declined" || action.status === "cancelled"
                ? "outline"
                : "default"
            }
            disabled={isPending}
            onClick={() => update(action.status)}
          >
            {isPending ? "Saving…" : action.label}
          </Button>
        ))}
      </div>
    </article>
  )
}

export function MarketplaceRequests({
  productOrders,
  serviceBookings,
  compact = false,
  activeOnly = false,
}: {
  productOrders: ApiProductOrder[]
  serviceBookings: ApiServiceBooking[]
  compact?: boolean
  activeOnly?: boolean
}) {
  const entries: RequestEntry[] = [
    ...productOrders.map((request) => ({ kind: "item" as const, request })),
    ...serviceBookings.map((request) => ({
      kind: "service" as const,
      request,
    })),
  ]
    .filter(
      ({ request }) =>
        !activeOnly ||
        request.status === "pending" ||
        request.status === "accepted"
    )
    .sort(
      (a, b) =>
        Date.parse(b.request.created_at) - Date.parse(a.request.created_at)
    )

  if (entries.length === 0) {
    return (
      <p className="rounded-2xl bg-card px-5 py-6 text-sm text-muted-foreground">
        {activeOnly
          ? "No active purchase requests or service bookings."
          : "Your purchase requests and service bookings will appear here."}
      </p>
    )
  }

  return (
    <div className="rounded-2xl bg-card px-4 sm:px-5">
      {entries.map((entry) => (
        <RequestCard
          key={`${entry.kind}-${entry.request.id}`}
          entry={entry}
          compact={compact}
        />
      ))}
    </div>
  )
}
