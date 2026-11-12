import type { Metadata } from "next"
import { MailIcon } from "lucide-react"

import { PlaceholderPage } from "@/components/serve/placeholder-page"

export const metadata: Metadata = { title: "Inbox" }

export default function InboxPage() {
  return (
    <PlaceholderPage
      title="Inbox"
      icon={MailIcon}
      description="Chats with buyers and sellers, offers and counter-offers, and meetup planning will live here."
    />
  )
}
