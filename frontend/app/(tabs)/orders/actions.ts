"use server"

import { revalidatePath } from "next/cache"

import {
  ApiError,
  createProductOrder,
  createServiceBooking,
  updateProductOrder,
  updateServiceBooking,
  type ProductOrderPayload,
  type ServiceBookingPayload,
} from "@/lib/api-write"
import type {
  ApiProductOrder,
  ApiServiceBooking,
  RequestStatus,
} from "@/lib/api"
import { auth } from "@/lib/auth/server"

type ActionResult<T> = {
  data?: T
  error?: string
  needsSignIn?: boolean
}

async function requireSession(): Promise<ActionResult<never> | undefined> {
  const { data: session, error } = await auth.getSession()
  if (error) return { error: error.message || "Could not verify your session." }
  return session?.user ? undefined : { error: "Sign in to continue.", needsSignIn: true }
}

function actionError<T>(error: unknown): ActionResult<T> {
  if (error instanceof ApiError) {
    return {
      error: error.message,
      needsSignIn: error.status === 401,
    }
  }
  throw error
}

export async function placeProductOrder(
  listingId: string,
  buyerNote: string
): Promise<ActionResult<ApiProductOrder>> {
  const sessionError = await requireSession()
  if (sessionError) return sessionError
  const payload: ProductOrderPayload = {
    listing_id: listingId,
    buyer_note: buyerNote.trim() || undefined,
  }
  try {
    const data = await createProductOrder(payload)
    revalidatePath("/orders")
    revalidatePath("/")
    revalidatePath(`/listings/${listingId}`)
    return { data }
  } catch (error) {
    return actionError(error)
  }
}

export async function requestServiceBooking(
  serviceId: string,
  details: string,
  requestedDate: string
): Promise<ActionResult<ApiServiceBooking>> {
  const sessionError = await requireSession()
  if (sessionError) return sessionError
  const payload: ServiceBookingPayload = {
    service_id: serviceId,
    details: details.trim(),
    requested_date: requestedDate,
  }
  try {
    const data = await createServiceBooking(payload)
    revalidatePath("/orders")
    revalidatePath("/")
    revalidatePath(`/services/${serviceId}`)
    return { data }
  } catch (error) {
    return actionError(error)
  }
}

export async function changeProductOrderStatus(
  orderId: string,
  status: RequestStatus
): Promise<ActionResult<ApiProductOrder>> {
  const sessionError = await requireSession()
  if (sessionError) return sessionError
  try {
    const data = await updateProductOrder(orderId, status)
    revalidatePath("/orders")
    revalidatePath("/")
    revalidatePath(`/orders/item-${orderId}`)
    revalidatePath(`/listings/${data.listing_id}`)
    return { data }
  } catch (error) {
    return actionError(error)
  }
}

export async function changeServiceBookingStatus(
  bookingId: string,
  status: RequestStatus
): Promise<ActionResult<ApiServiceBooking>> {
  const sessionError = await requireSession()
  if (sessionError) return sessionError
  try {
    const data = await updateServiceBooking(bookingId, status)
    revalidatePath("/orders")
    revalidatePath("/")
    revalidatePath(`/orders/booking-${bookingId}`)
    revalidatePath(`/services/${data.service_id}`)
    return { data }
  } catch (error) {
    return actionError(error)
  }
}
