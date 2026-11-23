"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { useState, useTransition, type FormEvent } from "react"

import {
  placeProductOrder,
  requestServiceBooking,
} from "@/app/(tabs)/orders/actions"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"

type Props = {
  kind: "item" | "service"
  recordId: string
  isSignedIn: boolean
  isOwner: boolean
  unavailable?: "reserved" | "sold"
}

function localDate() {
  const now = new Date()
  const offset = now.getTimezoneOffset() * 60_000
  return new Date(now.getTime() - offset).toISOString().slice(0, 10)
}

export function MarketplaceRequestForm({
  kind,
  recordId,
  isSignedIn,
  isOwner,
  unavailable,
}: Props) {
  const router = useRouter()
  const [details, setDetails] = useState("")
  const [requestedDate, setRequestedDate] = useState(localDate)
  const [error, setError] = useState("")
  const [needsSignIn, setNeedsSignIn] = useState(false)
  const [isPending, startTransition] = useTransition()
  const service = kind === "service"

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError("")
    setNeedsSignIn(false)
    const form = new FormData(event.currentTarget)

    startTransition(async () => {
      const result = service
        ? await requestServiceBooking(
            recordId,
            String(form.get("details") ?? ""),
            String(form.get("requested_date") ?? "")
          )
        : await placeProductOrder(recordId, String(form.get("details") ?? ""))
      if (result.error) {
        setError(result.error)
        setNeedsSignIn(result.needsSignIn ?? false)
        return
      }
      router.push("/orders")
      router.refresh()
    })
  }

  return (
    <section
      aria-labelledby="request-heading"
      className="flex flex-col gap-4 rounded-2xl bg-muted/50 p-4 sm:p-5"
    >
      <div>
        <h2 id="request-heading" className="text-lg font-semibold">
          {service ? "Request this service" : "Request to buy"}
        </h2>
        <p className="mt-1 text-sm text-muted-foreground">
          {service
            ? "Choose a date and tell the provider what you need."
            : "The seller will review your request before confirming the handover."}
        </p>
      </div>

      {isOwner ? (
        <p className="text-sm text-muted-foreground">
          You can’t request your own {service ? "service" : "listing"}.
        </p>
      ) : unavailable ? (
        <p className="text-sm text-muted-foreground">
          {unavailable === "reserved"
            ? "A request is already in progress for this item."
            : "This item has been sold."}
        </p>
      ) : !isSignedIn ? (
        <p className="text-sm">
          <Link
            href={`/auth/sign-in?redirectTo=${encodeURIComponent(
              `/${service ? "services" : "listings"}/${recordId}`
            )}`}
            className="font-medium underline underline-offset-4"
          >
            Sign in
          </Link>{" "}
          to {service ? "request a booking" : "request to buy this item"}.
        </p>
      ) : (
        <form className="flex flex-col gap-3" onSubmit={submit}>
          {service && (
            <label className="flex flex-col gap-1.5 text-sm font-medium">
              Requested date
              <input
                type="date"
                name="requested_date"
                required
                min={localDate()}
                value={requestedDate}
                onChange={(event) => setRequestedDate(event.target.value)}
                className="h-11 rounded-xl border border-input bg-background px-3 text-base font-normal focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none md:text-sm"
              />
            </label>
          )}
          <label className="flex flex-col gap-1.5 text-sm font-medium">
            {service ? "What do you need?" : "Note to the seller (optional)"}
            <Textarea
              name="details"
              value={details}
              onChange={(event) => setDetails(event.target.value)}
              required={service}
              maxLength={service ? 5000 : 1000}
              placeholder={
                service
                  ? "Describe the work or help you need"
                  : "Suggest a meetup time or add a short note"
              }
            />
          </label>
          {error && (
            <div role="alert" className="text-sm text-destructive">
              <p>{error}</p>
              {needsSignIn && (
                <Link
                  href={`/auth/sign-in?redirectTo=${encodeURIComponent(
                    `/${service ? "services" : "listings"}/${recordId}`
                  )}`}
                  className="mt-1 inline-block font-medium underline underline-offset-4"
                >
                  Sign in again
                </Link>
              )}
            </div>
          )}
          <div className="flex flex-wrap items-center gap-3">
            <Button type="submit" disabled={isPending}>
              {isPending
                ? "Sending request…"
                : service
                  ? "Send booking request"
                  : "Send purchase request"}
            </Button>
            <span className="text-sm text-muted-foreground">
              {service
                ? "The provider must accept before it is booked."
                : "This item is reserved while the request is active."}
            </span>
          </div>
        </form>
      )}
    </section>
  )
}
