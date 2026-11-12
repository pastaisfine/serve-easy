import type { Metadata } from "next"
import { ClipboardListIcon } from "lucide-react"

import { PlaceholderPage } from "@/components/serve/placeholder-page"

export const metadata: Metadata = { title: "Orders" }

export default function OrdersPage() {
  return (
    <PlaceholderPage
      title="Orders"
      icon={ClipboardListIcon}
      description="Everything you're buying and selling, upcoming meetups, booked slots and handover codes will live here."
    />
  )
}
