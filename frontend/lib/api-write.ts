/**
 * Authenticated calls to the FastAPI backend. Server-side only (Server Actions,
 * Server Components, Route Handlers).
 *
 * The browser never sees the API. For each call we ask Neon Auth for a
 * short-lived JWT for the signed-in user and send it as a Bearer token; the
 * backend verifies it against the auth server's JWKS.
 */
import { API_URL } from "@/lib/api"
import type { ApiListing, ApiService, ApiUserSummary } from "@/lib/api"
import { auth } from "@/lib/auth/server"
import type { ShopRef } from "@/lib/types"

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
    /** Field name -> message, from FastAPI validation errors (422). */
    readonly fieldErrors: Record<string, string> = {}
  ) {
    super(message)
    this.name = "ApiError"
  }
}

interface ValidationIssue {
  loc: (string | number)[]
  msg: string
  type: string
}

/** Pydantic's wording is technical; say what the user needs to fix. */
function describeIssue({ loc, msg, type }: ValidationIssue) {
  const field = String(loc[loc.length - 1])
  if (field === "price") {
    return "Enter a price above RM 0 and up to RM 99,999.99, with at most 2 decimals"
  }
  if (type === "string_too_short") return "This field is required"
  if (type === "string_too_long") return "This is too long"
  return msg
}

async function authedFetch(path: string, init: RequestInit = {}) {
  // The SDK's token() returns an opaque union that TypeScript sees as unknown.
  // The backend verifies the JWT, so this check only guards for a missing token.
  // Use type assertion to work around the package's type definitions.
  // @ts-expect-error - token() returns a union that TypeScript sees as unknown
  const token = await auth.token()
  if (!token?.data?.token) throw new ApiError(401, "You need to sign in")

  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    cache: "no-store",
    headers: { ...init.headers, Authorization: `Bearer ${token.data.token}` },
  })
  if (res.ok) return res

  const body = await res.json().catch(() => null)
  const detail = body?.detail
  if (Array.isArray(detail)) {
    const fieldErrors: Record<string, string> = {}
    for (const issue of detail as ValidationIssue[]) {
      fieldErrors[String(issue.loc[issue.loc.length - 1])] =
        describeIssue(issue)
    }
    throw new ApiError(
      res.status,
      "Please fix the highlighted fields",
      fieldErrors
    )
  }
  throw new ApiError(
    res.status,
    typeof detail === "string" ? detail : `Request failed (${res.status})`
  )
}

export interface Me extends ApiUserSummary {
  email: string
  role: "student" | "food_seller" | "service_provider"
  shop: ShopRef | null
}

export interface RegistrationProfile {
  role: "student" | "service_provider"
  student_id: string | null
}

export async function getMe(): Promise<Me> {
  return (await authedFetch("/me")).json()
}

export async function saveRegistrationProfile(
  profile: RegistrationProfile
): Promise<void> {
  await authedFetch("/me/registration", {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(profile),
  })
}

/** Uploads a photo. Pass `key` as `image` on create; `url` previews it. */
export async function uploadImage(
  file: File
): Promise<{ key: string; url: string }> {
  const body = new FormData()
  body.set("file", file)
  const res = await authedFetch("/uploads/images", { method: "POST", body })
  return res.json()
}

export interface NewListing {
  title: string
  description: string
  price: string
  condition: string
  category: string
  image: string | null
  spot: string
  shop_id: string | null
}

export interface NewService {
  title: string
  description: string
  price: string
  unit: string | null
  category: string
  image: string | null
  spot: string
  shop_id: string | null
}

function postJson(path: string, payload: unknown) {
  return authedFetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
}

export async function createListing(payload: NewListing): Promise<ApiListing> {
  return (await postJson("/listings", payload)).json()
}

export async function createService(payload: NewService): Promise<ApiService> {
  return (await postJson("/services", payload)).json()
}
