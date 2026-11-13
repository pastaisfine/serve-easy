"use server"

import { redirect } from "next/navigation"

import { auth } from "@/lib/auth/server"
import {
  ApiError,
  createListing,
  createService,
  getMe,
  uploadImage,
} from "@/lib/api-write"

export interface UploadedPhoto {
  key: string
  url: string
}

export interface ListingFormState {
  message?: string
  fieldErrors?: Record<string, string>
  /** What the user typed, so a failed submit doesn't wipe the form. */
  values?: Record<string, string>
  /** Set when the photo uploaded but the listing didn't save; reused on retry. */
  photo?: UploadedPhoto
}

const REQUIRED = {
  "sell-item": ["title", "price", "category", "condition", "spot"],
  "offer-service": ["title", "price", "category", "spot"],
} as const

const FIELDS = [
  "title",
  "description",
  "price",
  "category",
  "condition",
  "unit",
  "spot",
] as const

function text(formData: FormData, key: string) {
  const value = formData.get(key)
  return typeof value === "string" ? value.trim() : ""
}

/**
 * Publishes an item (kind "sell-item") or a service ("offer-service").
 * Bound to the kind in the form: `createListingAction.bind(null, kind)`.
 */
export async function createListingAction(
  kind: string,
  _prev: ListingFormState,
  formData: FormData
): Promise<ListingFormState> {
  if (kind !== "sell-item" && kind !== "offer-service") {
    return { message: "Unknown listing type." }
  }

  // The page redirects signed-out users too, but an action is a public
  // endpoint: check again here.
  const { data: session } = await auth.getSession()
  if (!session?.user) redirect(`/auth/sign-in?redirectTo=/create/${kind}`)

  const values: Record<string, string> = {}
  for (const key of FIELDS) values[key] = text(formData, key)
  values.useShop = formData.get("useShop") === "on" ? "on" : ""

  // Cheap checks first so we don't upload a photo for a form that can't save.
  const fieldErrors: Record<string, string> = {}
  for (const key of REQUIRED[kind]) {
    if (!values[key]) fieldErrors[key] = "This field is required"
  }
  const file = formData.get("photo")
  const newFile = file instanceof File && file.size > 0 ? file : null
  const previous: UploadedPhoto | undefined = (() => {
    const key = text(formData, "photoKey")
    const url = text(formData, "photoUrl")
    return key && url ? { key, url } : undefined
  })()

  if (Object.keys(fieldErrors).length > 0) {
    return {
      message: "Please fix the highlighted fields.",
      fieldErrors,
      values,
      photo: previous,
    }
  }

  let photo = previous
  let href: string
  try {
    if (newFile) photo = await uploadImage(newFile)
    const image = photo?.key ?? null

    // Resolve the shop on the server: never trust a shop id from the browser.
    const shopId =
      values.useShop === "on" ? ((await getMe()).shop?.id ?? null) : null

    if (kind === "sell-item") {
      const created = await createListing({
        title: values.title,
        description: values.description,
        price: values.price,
        condition: values.condition,
        category: values.category,
        image,
        spot: values.spot,
        shop_id: shopId,
      })
      href = `/listings/${created.id}`
    } else {
      const created = await createService({
        title: values.title,
        description: values.description,
        price: values.price,
        unit: values.unit || null,
        category: values.category,
        image,
        spot: values.spot,
        shop_id: shopId,
      })
      href = `/services/${created.id}`
    }
  } catch (error) {
    if (error instanceof ApiError) {
      // A photo problem belongs on the photo field, not as a vague banner.
      const photoError =
        error.status === 413 || error.status === 415 ? error.message : undefined
      return {
        message: photoError ? undefined : error.message,
        fieldErrors: {
          ...error.fieldErrors,
          ...(photoError ? { photo: photoError } : {}),
        },
        values,
        photo,
      }
    }
    console.error("createListingAction failed", error)
    return {
      message: "Something went wrong on our side. Please try again.",
      values,
      photo,
    }
  }

  redirect(href)
}
