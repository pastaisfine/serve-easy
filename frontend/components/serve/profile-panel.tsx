"use client"

import Link from "next/link"
import { useEffect, useState } from "react"

import {
  getProfileUserAction,
  signOutAction,
  type ProfileUser,
} from "@/app/auth/actions"
import { StudentAvatar } from "@/components/serve/student"
import { LoadingSubmitButton } from "@/components/ui/loading-submit-button"

type ProfileState = "loading" | "signed-out" | "error" | { user: ProfileUser }

export function ProfilePanel() {
  const [profile, setProfile] = useState<ProfileState>("loading")

  useEffect(() => {
    let active = true

    getProfileUserAction()
      .then((user) => {
        if (active) setProfile(user ? { user } : "signed-out")
      })
      .catch(() => {
        if (active) setProfile("error")
      })

    return () => {
      active = false
    }
  }, [])

  if (profile === "loading") {
    return (
      <div
        className="max-w-xl rounded-2xl bg-card p-6 text-sm text-muted-foreground ring-1 ring-foreground/5"
        role="status"
      >
        Loading profile…
      </div>
    )
  }

  if (profile === "error") {
    return (
      <p className="max-w-xl text-sm text-destructive" role="alert">
        Your profile could not be loaded. Please refresh the page.
      </p>
    )
  }

  if (profile === "signed-out") {
    return (
      <div className="flex max-w-xl flex-col gap-5 rounded-2xl bg-card p-6 ring-1 ring-foreground/5">
        <p className="text-base text-muted-foreground">
          Sign in to sell items, offer services and keep track of your listings.
        </p>
        <Link
          href="/auth/sign-in"
          className="inline-flex h-11 w-fit items-center justify-center rounded-xl bg-primary px-5 font-medium text-primary-foreground hover:bg-primary/90"
        >
          Sign in
        </Link>
      </div>
    )
  }

  const { user } = profile

  return (
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
        <LoadingSubmitButton
          variant="outline"
          className="h-11 rounded-xl px-5"
          pendingLabel="Signing out…"
        >
          Sign out
        </LoadingSubmitButton>
      </form>
    </div>
  )
}
