"use client"

import { useActionState } from "react"
import Link from "next/link"

import { signInAction, signUpAction } from "@/app/auth/actions"
import { FormField } from "@/components/serve/form-field"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

const copy = {
  "sign-in": {
    title: "Welcome back",
    subtitle: "Sign in to sell, offer services and message other students.",
    submit: "Sign in",
    pending: "Signing in…",
    switchText: "New to Serve?",
    switchLabel: "Create an account",
    switchPath: "/auth/sign-up",
  },
  "sign-up": {
    title: "Create your account",
    subtitle: "Join your campus marketplace. It takes a minute.",
    submit: "Create account",
    pending: "Creating account…",
    switchText: "Already have an account?",
    switchLabel: "Sign in",
    switchPath: "/auth/sign-in",
  },
} as const

export function AuthForm({
  mode,
  redirectTo,
}: {
  mode: "sign-in" | "sign-up"
  redirectTo: string
}) {
  const c = copy[mode]
  const [state, formAction, pending] = useActionState(
    mode === "sign-in" ? signInAction : signUpAction,
    {}
  )
  const switchHref =
    redirectTo === "/"
      ? c.switchPath
      : `${c.switchPath}?redirectTo=${encodeURIComponent(redirectTo)}`

  return (
    <div className="flex flex-col gap-6 rounded-2xl bg-card p-6 ring-1 ring-foreground/5 md:p-8">
      <div className="flex flex-col gap-1.5">
        <h1 className="text-2xl font-semibold tracking-tight">{c.title}</h1>
        <p className="text-base text-muted-foreground">{c.subtitle}</p>
      </div>

      <form action={formAction} className="flex flex-col gap-4">
        <input type="hidden" name="redirectTo" value={redirectTo} />

        {mode === "sign-up" && (
          <FormField label="Full name">
            <Input
              name="name"
              type="text"
              autoComplete="name"
              required
              defaultValue={state.name}
              className="h-11 rounded-xl"
            />
          </FormField>
        )}
        <FormField label="Email">
          <Input
            name="email"
            type="email"
            autoComplete="email"
            required
            defaultValue={state.email}
            className="h-11 rounded-xl"
          />
        </FormField>
        <FormField
          label="Password"
          hint={mode === "sign-up" ? "At least 8 characters." : undefined}
        >
          <Input
            name="password"
            type="password"
            autoComplete={mode === "sign-in" ? "current-password" : "new-password"}
            required
            minLength={mode === "sign-up" ? 8 : undefined}
            className="h-11 rounded-xl"
          />
        </FormField>

        {state.error && (
          <p role="alert" className="text-sm text-destructive">
            {state.error}
          </p>
        )}

        <Button type="submit" disabled={pending} className="h-11 rounded-xl">
          {pending ? c.pending : c.submit}
        </Button>
      </form>

      <p className="text-center text-sm text-muted-foreground">
        {c.switchText}{" "}
        <Link
          href={switchHref}
          className="font-medium text-foreground underline-offset-2 hover:underline"
        >
          {c.switchLabel}
        </Link>
      </p>
    </div>
  )
}
