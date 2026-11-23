import type { Metadata } from "next"

import { ProfilePanel } from "@/components/serve/profile-panel"

export const metadata: Metadata = { title: "Profile" }

export default function ProfilePage() {
  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-8 px-4 pt-10 md:px-8 md:pt-14">
      <h1 className="text-3xl font-semibold tracking-tight">Profile</h1>
      <ProfilePanel />
    </div>
  )
}
