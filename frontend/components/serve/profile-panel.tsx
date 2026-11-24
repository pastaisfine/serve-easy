"use client"

import Link from "next/link"
import { useEffect, useState, useTransition, type FormEvent } from "react"

import {
  getProfileUserAction,
  saveProfileContactsAction,
  signOutAction,
  type ProfileUser,
} from "@/app/auth/actions"
import { StudentAvatar } from "@/components/serve/student"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { LoadingSubmitButton } from "@/components/ui/loading-submit-button"

type ProfileState = "loading" | "signed-out" | "error" | { user: ProfileUser }

export function ProfilePanel() {
  const [profile, setProfile] = useState<ProfileState>("loading")
  const [contactError, setContactError] = useState("")
  const [contactFieldErrors, setContactFieldErrors] = useState<
    Record<string, string>
  >({})
  const [contactSaved, setContactSaved] = useState(false)
  const [isSavingContacts, startSavingContacts] = useTransition()

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

  function saveContacts(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setContactError("")
    setContactFieldErrors({})
    setContactSaved(false)
    const formData = new FormData(event.currentTarget)
    const whatsapp = String(formData.get("whatsapp") ?? "").trim()
    const telegramUsername = String(
      formData.get("telegram_username") ?? ""
    ).trim()

    startSavingContacts(async () => {
      const result = await saveProfileContactsAction({
        whatsapp: whatsapp || null,
        telegram_username: telegramUsername || null,
      })
      if (result.error) {
        setContactError(result.error)
        setContactFieldErrors(result.fieldErrors ?? {})
        return
      }
      const savedContacts = result.data
      if (!savedContacts) return
      setProfile((current) =>
        typeof current === "object"
          ? {
              user: {
                ...current.user,
                whatsapp: savedContacts.whatsapp,
                telegram_username: savedContacts.telegram_username,
              },
            }
          : current
      )
      setContactSaved(true)
    })
  }

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
      <form
        onSubmit={saveContacts}
        className="flex flex-col gap-4 border-t pt-5"
      >
        <div>
          <h2 className="font-semibold">Public contact details</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            These links are visible to anyone viewing your listings or services.
          </p>
        </div>
        <div className="flex flex-col gap-2">
          <label htmlFor="profile-whatsapp" className="text-sm font-medium">
            WhatsApp number
          </label>
          <Input
            id="profile-whatsapp"
            name="whatsapp"
            type="tel"
            autoComplete="tel"
            defaultValue={user.whatsapp ?? ""}
            placeholder="+60 12 345 6789"
            aria-describedby={
              contactFieldErrors.whatsapp ? "profile-whatsapp-error" : undefined
            }
          />
          <p className="text-xs text-muted-foreground">
            Include the country code so the WhatsApp link works.
          </p>
          {contactFieldErrors.whatsapp && (
            <p id="profile-whatsapp-error" className="text-sm text-destructive">
              {contactFieldErrors.whatsapp}
            </p>
          )}
        </div>
        <div className="flex flex-col gap-2">
          <label htmlFor="profile-telegram" className="text-sm font-medium">
            Telegram username
          </label>
          <Input
            id="profile-telegram"
            name="telegram_username"
            autoComplete="username"
            defaultValue={
              user.telegram_username ? `@${user.telegram_username}` : ""
            }
            placeholder="@username"
            aria-describedby={
              contactFieldErrors.telegram_username
                ? "profile-telegram-error"
                : undefined
            }
          />
          {contactFieldErrors.telegram_username && (
            <p id="profile-telegram-error" className="text-sm text-destructive">
              {contactFieldErrors.telegram_username}
            </p>
          )}
        </div>
        {contactError && (
          <p role="alert" className="text-sm text-destructive">
            {contactError}
          </p>
        )}
        {contactSaved && (
          <p role="status" className="text-sm text-muted-foreground">
            Contact details saved.
          </p>
        )}
        <Button type="submit" className="w-fit" disabled={isSavingContacts}>
          {isSavingContacts ? "Saving…" : "Save contact details"}
        </Button>
      </form>
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
