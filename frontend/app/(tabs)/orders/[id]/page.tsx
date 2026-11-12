import type { Metadata } from "next"
import { ClipboardListIcon } from "lucide-react"

import { PlaceholderPage } from "@/components/serve/placeholder-page"

export const metadata: Metadata = { title: "Order details" }

export default function OrderDetailPage() {
  return (
    <PlaceholderPage
      title="Order details"
      icon={ClipboardListIcon}
      description="The meetup spot, time, chat and in-person handover confirmation for this order will live here."
    />
  )
}
