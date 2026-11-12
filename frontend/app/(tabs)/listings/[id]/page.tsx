import type { Metadata } from "next"
import { TagIcon } from "lucide-react"

import { PlaceholderPage } from "@/components/serve/placeholder-page"

export const metadata: Metadata = { title: "Listing" }

export default function ListingDetailPage() {
  return (
    <PlaceholderPage
      title="Listing"
      icon={TagIcon}
      description="Photos, price, the seller's meetup history, and buttons to buy, make an offer or book a slot will live here."
    />
  )
}
