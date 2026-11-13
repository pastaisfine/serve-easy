import type { Metadata } from "next"
import Link from "next/link"

import { signOutAction } from "@/app/auth/actions"
import { StudentAvatar } from "@/components/serve/student"
import { Button } from "@/components/ui/button"
import { auth } from "@/lib/auth/server"

export const metadata: Metadata = { title: "Profile" }

export default async function ProfilePage() {
  const { data: session } = await auth.getSession()
  const user = session?.user

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-8 px-4 pt-10 md:px-8 md:pt-14">
      <h1 className="text-3xl font-semibold tracking-tight">Profile</h1>

      {user ? (
        <div className="flex max-w-xl flex-col gap-6 rounded-2xl bg-card p-6 ring-1 ring-foreground/5">
          <div className="flex items-center gap-4">
            <StudentAvatar student={user} size="lg" />
            <div className="flex min-w-0 flex-col">
              <span className="truncate text-lg font-medium">{user.name}</span>
              <span className="truncate text-sm text-muted-foreground">
                {user.email}
              </span>
            </div>
          </div>
          <form action={signOutAction}>
            <Button type="submit" variant="outline" className="h-11 rounded-xl px-5">
              Sign out
            </Button>
          </form>
        </div>
      ) : (
        <div className="flex max-w-xl flex-col gap-5 rounded-2xl bg-card p-6 ring-1 ring-foreground/5">
          <p className="text-base text-muted-foreground">
            Sign in to sell items, offer services and keep track of your
            listings.
          </p>
          <Link
            href="/auth/sign-in"
            className="inline-flex h-11 w-fit items-center justify-center rounded-xl bg-primary px-5 font-medium text-primary-foreground hover:bg-primary/90"
          >
            Sign in
          </Link>
        </div>
      )}
    </div>
  )
}
