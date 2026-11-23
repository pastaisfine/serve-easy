"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { useState, useTransition } from "react"

import {
  markAllInboxNotificationsRead,
  markInboxNotificationRead,
} from "@/app/(tabs)/inbox/actions"
import { Button } from "@/components/ui/button"
import type { ApiNotification } from "@/lib/api"
import { cn } from "@/lib/utils"

type InboxNotification = ApiNotification & { createdAtLabel: string }

function NotificationRow({
  notification,
}: {
  notification: InboxNotification
}) {
  const router = useRouter()
  const [error, setError] = useState("")
  const [isPending, startTransition] = useTransition()
  const isUnread = notification.read_at === null

  function markRead() {
    setError("")
    startTransition(async () => {
      const result = await markInboxNotificationRead(notification.id)
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
        "flex flex-col gap-3 border-b py-4 last:border-b-0 sm:flex-row sm:items-start sm:justify-between sm:gap-6",
        isUnread && "bg-muted/35"
      )}
    >
      <div className="flex min-w-0 flex-1 gap-3">
        <span
          aria-hidden="true"
          className={cn(
            "mt-2 size-2 shrink-0 rounded-full",
            isUnread ? "bg-notify" : "bg-transparent"
          )}
        />
        <span className="sr-only">{isUnread ? "Unread" : "Read"}</span>
        <div className="min-w-0">
          <Link
            href={notification.href}
            className="font-medium underline-offset-4 hover:underline focus-visible:underline focus-visible:outline-none"
          >
            {notification.title}
          </Link>
          <p className="mt-1 text-sm leading-6 text-muted-foreground">
            {notification.message}
          </p>
          {error && (
            <p role="alert" className="mt-2 text-sm text-destructive">
              {error}
            </p>
          )}
        </div>
      </div>
      <div className="flex shrink-0 items-center justify-between gap-3 pl-5 sm:justify-end sm:pl-0">
        <time
          dateTime={notification.created_at}
          className="text-sm text-muted-foreground"
        >
          {notification.createdAtLabel}
        </time>
        {isUnread && (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            disabled={isPending}
            onClick={markRead}
          >
            {isPending ? "Saving…" : "Mark read"}
          </Button>
        )}
      </div>
    </article>
  )
}

export function Inbox({
  notifications,
}: {
  notifications: InboxNotification[]
}) {
  const router = useRouter()
  const [error, setError] = useState("")
  const [isPending, startTransition] = useTransition()
  const unreadCount = notifications.filter(
    (notification) => notification.read_at === null
  ).length

  function markAllRead() {
    setError("")
    startTransition(async () => {
      const result = await markAllInboxNotificationsRead()
      if (result.error) {
        setError(result.error)
        return
      }
      router.refresh()
    })
  }

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-6 px-4 pt-8 md:px-8 md:pt-12">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">Inbox</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Updates about your campus marketplace requests and exchanges.
          </p>
        </div>
        {unreadCount > 0 && (
          <Button
            type="button"
            variant="outline"
            disabled={isPending}
            onClick={markAllRead}
          >
            {isPending ? "Saving…" : "Mark all read"}
          </Button>
        )}
      </header>

      <section aria-labelledby="updates-heading">
        <div className="mb-3 flex items-baseline justify-between gap-4">
          <h2 id="updates-heading" className="text-lg font-semibold">
            Updates
          </h2>
          <span className="text-sm text-muted-foreground">
            {unreadCount} unread
          </span>
        </div>
        {error && (
          <p role="alert" className="mb-3 text-sm text-destructive">
            {error}
          </p>
        )}
        {notifications.length === 0 ? (
          <div className="flex flex-col items-start gap-4 rounded-2xl bg-card px-5 py-8">
            <p className="text-sm text-muted-foreground">
              No marketplace updates yet. Purchase requests and exchange
              updates will appear here.
            </p>
            <Button
              nativeButton={false}
              render={<Link href="/" />}
              variant="outline"
            >
              Explore listings
            </Button>
          </div>
        ) : (
          <div className="rounded-2xl bg-card px-4 sm:px-5">
            {notifications.map((notification) => (
              <NotificationRow
                key={notification.id}
                notification={notification}
              />
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
