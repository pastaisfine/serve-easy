"use server"

import { revalidatePath } from "next/cache"

import {
  ApiError,
  createMealMenuItem,
  createMealOrders,
  updateMealDeliveryBatch,
  updateMealMenuItem,
  updateMyMealProviderContacts,
  uploadImage,
} from "@/lib/api-write"
import type {
  ApiCafeteria,
  ApiFoodItem,
  ApiMealOrder,
  ApiProviderDeliveryBatch,
  ContactDetailsPayload,
  MealMenuItemPayload,
  MealOrderPayload,
} from "@/lib/api"

type ActionResult<T> = {
  data?: T
  error?: string
  fieldErrors?: Record<string, string>
  needsSignIn?: boolean
}

function actionError<T>(error: unknown): ActionResult<T> {
  if (error instanceof ApiError) {
    return {
      error: error.message,
      fieldErrors: error.fieldErrors,
      needsSignIn: error.status === 401,
    }
  }
  throw error
}

export async function placeMealOrder(
  payload: MealOrderPayload
): Promise<ActionResult<ApiMealOrder[]>> {
  try {
    const result = await createMealOrders(payload)
    revalidatePath("/meals/orders")
    revalidatePath("/cafeterias")
    return { data: result.orders }
  } catch (error) {
    return actionError(error)
  }
}

export async function addMealMenuItem(
  payload: MealMenuItemPayload
): Promise<ActionResult<ApiFoodItem>> {
  try {
    const item = await createMealMenuItem(payload)
    revalidatePath("/meals/manage")
    revalidatePath("/cafeterias")
    return { data: item }
  } catch (error) {
    return actionError(error)
  }
}

export async function saveMealProviderContacts(
  payload: ContactDetailsPayload
): Promise<ActionResult<ApiCafeteria>> {
  try {
    const provider = await updateMyMealProviderContacts(payload)
    revalidatePath("/meals/manage")
    revalidatePath("/cafeterias")
    revalidatePath("/meals/orders")
    return { data: provider }
  } catch (error) {
    return actionError(error)
  }
}

export async function setMealItemAvailability(
  itemId: string,
  available: boolean
): Promise<ActionResult<null>> {
  try {
    await updateMealMenuItem(itemId, { available })
    revalidatePath("/meals/manage")
    revalidatePath("/cafeterias")
    return { data: null }
  } catch (error) {
    return actionError(error)
  }
}

export async function updateMealBatch(
  batchId: string,
  status: "on_the_way" | "delivered",
  proofImage?: string
): Promise<ActionResult<ApiProviderDeliveryBatch>> {
  try {
    const batch = await updateMealDeliveryBatch(batchId, {
      status,
      proof_image: proofImage,
    })
    revalidatePath("/meals/orders")
    revalidatePath("/meals/manage")
    return { data: batch }
  } catch (error) {
    return actionError(error)
  }
}

export async function uploadMealDeliveryPhoto(
  formData: FormData
): Promise<ActionResult<{ key: string; url: string }>> {
  const file = formData.get("photo")
  if (!(file instanceof File) || file.size === 0) {
    return { error: "Choose a delivery photo first." }
  }
  try {
    return { data: await uploadImage(file, "meal") }
  } catch (error) {
    return actionError(error)
  }
}
