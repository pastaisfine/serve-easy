"use client"

import { useActionState, useState } from "react"
import Link from "next/link"

import {
  signInAction,
  signUpAction,
  type AuthState,
  type RegistrationRole,
} from "@/app/auth/actions"
import { FormField } from "@/components/serve/form-field"
import { Input } from "@/components/ui/input"
import { LoadingSubmitButton } from "@/components/ui/loading-submit-button"
import { NativeSelect } from "@/components/ui/native-select"
import type { ApiCafeteria } from "@/lib/api"

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

function HiddenRegistrationFields({
  state,
  step,
}: {
  state: AuthState
  step: NonNullable<AuthState["step"]>
}) {
  return (
    <>
      <input type="hidden" name="step" value={step} />
      <input type="hidden" name="name" value={state.name ?? ""} />
      <input type="hidden" name="email" value={state.email ?? ""} />
      <input
        type="hidden"
        name="accountType"
        value={state.accountType ?? "student"}
      />
      {step !== "complete-profile" && (
        <input type="hidden" name="studentId" value={state.studentId ?? ""} />
      )}
      {step !== "complete-profile" && (
        <input
          type="hidden"
          name="foodProviderId"
          value={state.foodProviderId ?? ""}
        />
      )}
      <input type="hidden" name="redirectTo" value={state.redirectTo ?? "/"} />
    </>
  )
}

function StudentNumberField({ state }: { state: AuthState }) {
  return (
    <FormField
      label="UTM matric number"
      hint="Enter your number as shown on your student ID, for example A26KT0123."
      error={state.fieldErrors?.studentId}
    >
      <Input
        name="studentId"
        type="text"
        autoComplete="off"
        autoCapitalize="characters"
        required
        minLength={9}
        maxLength={9}
        pattern="[Aa][0-9]{2}[A-Za-z]{2}[0-9]{4}"
        defaultValue={state.studentId}
        className="h-11 rounded-xl"
      />
    </FormField>
  )
}

export function AuthForm({
  mode,
  redirectTo,
  providers = [],
}: {
  mode: "sign-in" | "sign-up"
  redirectTo: string
  providers?: ApiCafeteria[]
}) {
  const c = copy[mode]
  const [state, formAction] = useActionState(
    mode === "sign-in" ? signInAction : signUpAction,
    {}
  )
  const [selectedRole, setSelectedRole] = useState<RegistrationRole>(
    state.accountType ?? "student"
  )
  const switchHref =
    redirectTo === "/"
      ? c.switchPath
      : `${c.switchPath}?redirectTo=${encodeURIComponent(redirectTo)}`
  const signUpStep = mode === "sign-up" ? state.step : undefined

  return (
    <div className="flex flex-col gap-6 rounded-2xl bg-card p-6 ring-1 ring-foreground/5 md:p-8">
      <div className="flex flex-col gap-1.5">
        <h1 className="text-2xl font-semibold tracking-tight">{c.title}</h1>
        <p className="text-base text-muted-foreground">{c.subtitle}</p>
      </div>

      <form action={formAction} className="flex flex-col gap-4">
        {mode === "sign-in" && (
          <input type="hidden" name="redirectTo" value={redirectTo} />
        )}

        {mode === "sign-up" && !signUpStep && (
          <>
            <input type="hidden" name="redirectTo" value={redirectTo} />
            <fieldset className="flex flex-col gap-2">
              <legend className="mb-1 text-sm font-medium">
                How will you use Serve?
              </legend>
              <label className="flex min-h-11 items-center gap-3 rounded-xl bg-background px-3">
                <input
                  type="radio"
                  name="accountType"
                  value="student"
                  checked={selectedRole === "student"}
                  onChange={() => setSelectedRole("student")}
                  className="accent-primary"
                />
                <span className="text-sm">Student</span>
              </label>
              <label className="flex min-h-11 items-center gap-3 rounded-xl bg-background px-3">
                <input
                  type="radio"
                  name="accountType"
                  value="service_provider"
                  checked={selectedRole === "service_provider"}
                  onChange={() => setSelectedRole("service_provider")}
                  className="accent-primary"
                />
                <span className="text-sm">Service provider</span>
              </label>
              <label className="flex min-h-11 items-center gap-3 rounded-xl bg-background px-3">
                <input
                  type="radio"
                  name="accountType"
                  value="food_seller"
                  checked={selectedRole === "food_seller"}
                  onChange={() => setSelectedRole("food_seller")}
                  className="accent-primary"
                />
                <span className="text-sm">Food service staff</span>
              </label>
              {state.fieldErrors?.accountType && (
                <p className="text-sm text-destructive">
                  {state.fieldErrors.accountType}
                </p>
              )}
            </fieldset>
          </>
        )}

        {mode === "sign-up" && signUpStep && (
          <HiddenRegistrationFields state={state} step={signUpStep} />
        )}

        {mode === "sign-up" && !signUpStep && (
          <FormField label="Full name" error={state.fieldErrors?.name}>
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

        {mode === "sign-in" && (
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
        )}

        {mode === "sign-up" && !signUpStep && (
          <FormField
            label="Email"
            hint={
              selectedRole === "student"
                ? "Students must use their @graduate.utm.my address."
                : "Use an email address you can access."
            }
            error={state.fieldErrors?.email}
          >
            <Input
              name="email"
              type="email"
              autoComplete="email"
              required
              defaultValue={state.email}
              className="h-11 rounded-xl"
            />
          </FormField>
        )}

        {mode === "sign-up" && !signUpStep && selectedRole === "student" && (
          <StudentNumberField state={state} />
        )}
        {mode === "sign-up" &&
          !signUpStep &&
          selectedRole === "food_seller" && (
            <FormField
              label="Food provider"
              hint="Choose the provider you represent."
              error={state.fieldErrors?.foodProviderId}
            >
              <NativeSelect
                name="foodProviderId"
                required
                defaultValue={state.foodProviderId ?? ""}
                className="h-11 rounded-xl"
              >
                <option value="" disabled>
                  Choose a provider
                </option>
                {providers.map((provider) => (
                  <option key={provider.id} value={provider.id}>
                    {provider.name}
                  </option>
                ))}
              </NativeSelect>
            </FormField>
          )}

        {mode === "sign-in" && (
          <FormField label="Password">
            <Input
              name="password"
              type="password"
              autoComplete="current-password"
              required
              className="h-11 rounded-xl"
            />
          </FormField>
        )}

        {mode === "sign-up" && !signUpStep && (
          <FormField
            label="Password"
            hint="At least 8 characters."
            error={state.fieldErrors?.password}
          >
            <Input
              name="password"
              type="password"
              autoComplete="new-password"
              required
              minLength={8}
              className="h-11 rounded-xl"
            />
          </FormField>
        )}

        {signUpStep === "verify-email" && (
          <>
            <p className="text-sm text-muted-foreground">
              {state.message ?? `Enter the code sent to ${state.email}.`}
            </p>
            <FormField
              label="6-digit verification code"
              error={state.fieldErrors?.verificationCode}
            >
              <Input
                name="verificationCode"
                type="text"
                inputMode="numeric"
                autoComplete="one-time-code"
                required
                maxLength={6}
                pattern="[0-9]{6}"
                className="h-11 rounded-xl"
              />
            </FormField>
          </>
        )}

        {signUpStep === "complete-sign-in" && (
          <>
            <p className="text-sm text-muted-foreground">
              {state.message ?? "Sign in to finish setting up your account."}
            </p>
            <FormField label="Password">
              <Input
                name="password"
                type="password"
                autoComplete="current-password"
                required
                className="h-11 rounded-xl"
              />
            </FormField>
          </>
        )}

        {signUpStep === "complete-profile" && (
          <>
            <p className="text-sm text-muted-foreground">
              Finish setting up your{" "}
              {state.accountType === "student"
                ? "student"
                : state.accountType === "food_seller"
                  ? "food service staff"
                  : "service provider"}{" "}
              account.
            </p>
            {state.accountType === "student" && (
              <StudentNumberField state={state} />
            )}
            {state.accountType === "food_seller" && (
              <FormField
                label="Food provider"
                error={state.fieldErrors?.foodProviderId}
              >
                <NativeSelect
                  name="foodProviderId"
                  required
                  defaultValue={state.foodProviderId ?? ""}
                  className="h-11 rounded-xl"
                >
                  <option value="" disabled>
                    Choose a provider
                  </option>
                  {providers.map((provider) => (
                    <option key={provider.id} value={provider.id}>
                      {provider.name}
                    </option>
                  ))}
                </NativeSelect>
              </FormField>
            )}
          </>
        )}

        {state.error && (
          <p role="alert" className="text-sm text-destructive">
            {state.error}
          </p>
        )}

        {mode === "sign-up" && signUpStep === "verify-email" ? (
          <>
            <LoadingSubmitButton
              type="submit"
              className="h-11 rounded-xl"
              pendingLabel="Verifying…"
            >
              Verify email
            </LoadingSubmitButton>
            <button
              type="submit"
              name="intent"
              value="resend"
              formNoValidate
              className="text-sm font-medium underline-offset-2 hover:underline"
            >
              Resend code
            </button>
          </>
        ) : (
          <LoadingSubmitButton
            type="submit"
            className="h-11 rounded-xl"
            pendingLabel={
              mode === "sign-in"
                ? c.pending
                : signUpStep === "complete-sign-in"
                  ? "Signing in…"
                  : signUpStep === "complete-profile"
                    ? "Finishing setup…"
                    : c.pending
            }
          >
            {mode === "sign-in"
              ? c.submit
              : signUpStep === "complete-sign-in"
                ? "Continue"
                : signUpStep === "complete-profile"
                  ? "Finish account setup"
                  : c.submit}
          </LoadingSubmitButton>
        )}
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
