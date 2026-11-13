"use server"

import { redirect } from "next/navigation"

import { safeRedirect } from "@/lib/auth/redirect"
import { auth } from "@/lib/auth/server"

export interface AuthState {
  error?: string
  /** Echoed back so a failed attempt doesn't clear what the user typed. */
  name?: string
  email?: string
}

function field(formData: FormData, key: string) {
  const value = formData.get(key)
  return typeof value === "string" ? value : ""
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
  const name = field(formData, "name").trim()
  const email = field(formData, "email").trim()
  const password = field(formData, "password")
  if (!name || !email || !password) {
    return { error: "Fill in your name, email and a password.", name, email }
  }

  const { error } = await auth.signUp.email({ name, email, password })
  if (error) {
    return { error: error.message || "Could not create the account.", name, email }
  }

  redirect(safeRedirect(field(formData, "redirectTo")))
}

export async function signOutAction() {
  await auth.signOut()
  redirect("/")
}
