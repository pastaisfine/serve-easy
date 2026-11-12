import type { Metadata } from "next"
import { CircleUserRoundIcon } from "lucide-react"

import { PlaceholderPage } from "@/components/serve/placeholder-page"

export const metadata: Metadata = { title: "Profile" }

export default function ProfilePage() {
  return (
    <PlaceholderPage
      title="Profile"
      icon={CircleUserRoundIcon}
      description="Your listings, requests, meetup history and UTM verification will live here."
    />
  )
}
