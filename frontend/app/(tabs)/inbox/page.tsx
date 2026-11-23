import type { Metadata } from "next"
import { redirect } from "next/navigation"

import { Inbox } from "@/components/serve/inbox"
import { getMyNotifications } from "@/lib/api-write"
import { auth } from "@/lib/auth/server"
import { formatExpiry } from "@/lib/format"

export const metadata: Metadata = { title: "Inbox" }

export default async function InboxPage() {
  const { data: session, error } = await auth.getSession()
  if (error) throw new Error(error.message || "Could not verify your session.")
  if (!session?.user) {
    redirect("/auth/sign-in?redirectTo=%2Finbox")
  }

  const notifications = await getMyNotifications()
  return (
    <Inbox
      notifications={notifications.map((notification) => ({
        ...notification,
        createdAtLabel: formatExpiry(notification.created_at),
      }))}
    />
  )
}
