"use server"

import { revalidatePath } from "next/cache"

import {
  ApiError,
  markAllNotificationsRead as markAllNotificationsReadRequest,
  markNotificationRead as markNotificationReadRequest,
} from "@/lib/api-write"
import { auth } from "@/lib/auth/server"

type ActionResult = { error?: string }

async function requireSession(): Promise<ActionResult | undefined> {
  const { data: session, error } = await auth.getSession()
  if (error) return { error: error.message || "Could not verify your session." }
  return session?.user ? undefined : { error: "Sign in to continue." }
}

function actionError(error: unknown): ActionResult {
  if (error instanceof ApiError) return { error: error.message }
  throw error
}

export async function markInboxNotificationRead(
  notificationId: string
): Promise<ActionResult> {
  const sessionError = await requireSession()
  if (sessionError) return sessionError

  try {
    await markNotificationReadRequest(notificationId)
    revalidatePath("/inbox")
    return {}
  } catch (error) {
    return actionError(error)
  }
}

export async function markAllInboxNotificationsRead(): Promise<ActionResult> {
  const sessionError = await requireSession()
  if (sessionError) return sessionError

  try {
    await markAllNotificationsReadRequest()
    revalidatePath("/inbox")
    return {}
  } catch (error) {
    return actionError(error)
  }
}
