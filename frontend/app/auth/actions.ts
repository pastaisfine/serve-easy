"use server"

import { redirect } from "next/navigation"

import { ApiError, saveRegistrationProfile } from "@/lib/api-write"
import { safeRedirect } from "@/lib/auth/redirect"
import { auth } from "@/lib/auth/server"

export type RegistrationRole = "student" | "service_provider"

export interface AuthState {
  error?: string
  /** Echoed back so a failed attempt doesn't clear what the user typed. */
  name?: string
  email?: string
  accountType?: RegistrationRole
  studentId?: string
  redirectTo?: string
  step?: "verify-email" | "complete-sign-in" | "complete-profile"
  fieldErrors?: Record<string, string>
  message?: string
}

type EmailOtpResult<T> = {
  data?: T | null
  error?: { message?: string } | null
}

type NeonEmailOtpClient = {
  sendVerificationOtp(input: {
    email: string
    type: "email-verification"
  }): Promise<EmailOtpResult<{ success: boolean }>>
  verifyEmail(input: {
    email: string
    otp: string
  }): Promise<EmailOtpResult<{ status: boolean }>>
}

// The SDK exposes these managed-auth endpoints at runtime but types the plugin namespace as unknown.
const emailOtp = auth.emailOtp as NeonEmailOtpClient

function field(formData: FormData, key: string) {
  const value = formData.get(key)
  return typeof value === "string" ? value : ""
}

function registrationFields(formData: FormData): {
  name: string
  email: string
  accountType: RegistrationRole | null
  studentId: string
  redirectTo: string
} {
  const accountType = field(formData, "accountType")
  const email = field(formData, "email").trim().toLowerCase()
  const name = field(formData, "name").trim()
  const studentId = field(formData, "studentId").trim().toUpperCase()
  const redirectTo = safeRedirect(field(formData, "redirectTo"))

  return {
    name,
    email,
    accountType:
      accountType === "student" || accountType === "service_provider"
        ? accountType
        : null,
    studentId,
    redirectTo,
  }
}

function validateRegistration(
  registration: ReturnType<typeof registrationFields>,
  { requireCredentials }: { requireCredentials: boolean }
): AuthState {
  const fieldErrors: Record<string, string> = {}

  if (!registration.name && requireCredentials) {
    fieldErrors.name = "Enter your full name."
  }
  if (
    requireCredentials &&
    !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(registration.email)
  ) {
    fieldErrors.email = "Enter a valid email address."
  }
  if (!registration.accountType) {
    fieldErrors.accountType = "Choose how you will use Serve."
  }

  if (registration.accountType === "student") {
    if (!/^A\d{2}[A-Z]{2}\d{4}$/.test(registration.studentId)) {
      fieldErrors.studentId = "Use the format A26KT0123."
    }
    if (!registration.email.endsWith("@graduate.utm.my")) {
      fieldErrors.email = "Students must use their @graduate.utm.my email."
    }
  } else if (
    registration.accountType === "service_provider" &&
    registration.studentId
  ) {
    fieldErrors.studentId = "Service providers do not need a matric number."
  }

  return Object.keys(fieldErrors).length > 0
    ? {
        ...registration,
        accountType: registration.accountType ?? undefined,
        fieldErrors,
        error: "Please check the highlighted fields.",
      }
    : {}
}

async function sendVerificationCode(
  email: string
): Promise<string | undefined> {
  const { data, error } = await emailOtp.sendVerificationOtp({
    email,
    type: "email-verification",
  })
  return (
    error?.message ?? (data?.success ? undefined : "Email OTP is unavailable.")
  )
}

async function finishRegistration(
  registration: ReturnType<typeof registrationFields>
): Promise<AuthState> {
  const validation = validateRegistration(registration, {
    requireCredentials: false,
  })
  if (validation.error) {
    return { ...validation, step: "complete-profile" }
  }
  if (!registration.accountType) {
    return {
      ...registration,
      accountType: undefined,
      step: "complete-profile",
      error: "Choose how you will use Serve.",
    }
  }

  try {
    await saveRegistrationProfile({
      role: registration.accountType,
      student_id:
        registration.accountType === "student" ? registration.studentId : null,
    })
  } catch (error) {
    if (error instanceof ApiError) {
      return {
        ...registration,
        accountType: registration.accountType ?? undefined,
        step: "complete-profile",
        error: error.message,
      }
    }
    throw error
  }

  redirect(registration.redirectTo)
}

async function verifySignup(
  formData: FormData,
  registration: ReturnType<typeof registrationFields>
): Promise<AuthState> {
  const validation = validateRegistration(registration, {
    requireCredentials: false,
  })
  if (validation.error) {
    return { ...validation, step: "verify-email" }
  }

  if (field(formData, "intent") === "resend") {
    const error = await sendVerificationCode(registration.email)
    return {
      ...registration,
      accountType: registration.accountType ?? undefined,
      step: "verify-email",
      error,
      message: error ? undefined : "A new verification code has been sent.",
    }
  }

  const code = field(formData, "verificationCode").trim()
  if (!/^\d{6}$/.test(code)) {
    return {
      ...registration,
      accountType: registration.accountType ?? undefined,
      step: "verify-email",
      fieldErrors: {
        verificationCode: "Enter the 6-digit code from your email.",
      },
      error: "Please check the highlighted field.",
    }
  }

  const { data, error } = await emailOtp.verifyEmail({
    email: registration.email,
    otp: code,
  })
  if (error || data?.status !== true) {
    return {
      ...registration,
      accountType: registration.accountType ?? undefined,
      step: "verify-email",
      error: error?.message || "That code could not be verified.",
    }
  }

  const { data: session } = await auth.getSession()
  if (session?.user) return finishRegistration(registration)

  return {
    ...registration,
    accountType: registration.accountType ?? undefined,
    step: "complete-sign-in",
    message: "Email verified. Sign in once to finish setting up your account.",
  }
}

export async function signInAction(
  _prev: AuthState,
  formData: FormData
): Promise<AuthState> {
  const email = field(formData, "email").trim()
  const password = field(formData, "password")
  if (!email || !password) {
    return { error: "Enter your email and password.", email }
  }

  const { error } = await auth.signIn.email({ email, password })
  if (error) return { error: error.message || "Could not sign in.", email }

  redirect(safeRedirect(field(formData, "redirectTo")))
}

export async function signUpAction(
  _prev: AuthState,
  formData: FormData
): Promise<AuthState> {
  const registration = registrationFields(formData)
  const step = field(formData, "step")

  if (step === "verify-email") return verifySignup(formData, registration)

  if (step === "complete-sign-in") {
    const password = field(formData, "password")
    if (!password) {
      return {
        ...registration,
        accountType: registration.accountType ?? undefined,
        step,
        error: "Enter your password to finish signing in.",
      }
    }

    const { error } = await auth.signIn.email({
      email: registration.email,
      password,
    })
    if (error) {
      return {
        ...registration,
        accountType: registration.accountType ?? undefined,
        step,
        error: error.message || "Could not sign in.",
      }
    }

    return finishRegistration(registration)
  }

  if (step === "complete-profile") {
    const { data: session } = await auth.getSession()
    if (!session?.user) {
      return {
        ...registration,
        accountType: registration.accountType ?? undefined,
        step: "complete-sign-in",
        error: "Sign in to finish setting up your account.",
      }
    }
    return finishRegistration(registration)
  }

  const { name, email, accountType } = registration
  const password = field(formData, "password")
  const validation = validateRegistration(registration, {
    requireCredentials: true,
  })
  const fieldErrors = { ...validation.fieldErrors }
  if (password.length < 8) fieldErrors.password = "Use at least 8 characters."
  if (Object.keys(fieldErrors).length > 0) {
    return {
      ...registration,
      accountType: accountType ?? undefined,
      fieldErrors,
      error: "Please check the highlighted fields.",
    }
  }

  const { error } = await auth.signUp.email({ name, email, password })
  if (error) {
    return {
      ...registration,
      accountType: accountType ?? undefined,
      error: error.message || "Could not create the account.",
    }
  }

  const otpError = await sendVerificationCode(email)
  return {
    ...registration,
    accountType: accountType ?? undefined,
    step: "verify-email",
    error: otpError
      ? "Your account was created, but email code verification is unavailable. Enable Email OTP in the Neon Auth project, then resend the code."
      : undefined,
    message: otpError ? undefined : "We sent a 6-digit code to your email.",
  }
}

export async function signOutAction() {
  await auth.signOut()
  redirect("/")
}
