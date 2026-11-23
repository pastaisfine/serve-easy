/**
 * Server-side client for the ServeEasy FastAPI backend.
 *
 * Only call this from Server Components: `SERVE_API_URL` has no NEXT_PUBLIC_
 * prefix, so it is not available in the browser.
 */
import type { SearchCriteria } from "@/lib/search"
import type {
  ItemCategory,
  Listing,
  ServiceCategory,
  ShopRef,
  Student,
} from "@/lib/types"

export const API_URL = process.env.SERVE_API_URL ?? "http://localhost:8000"

/** Used when a listing has no photo. PNG because next/image rejects SVG. */
const NO_PHOTO = "https://placehold.co/600x600/png?text=No+photo"

// ------------------------------------------------- response shapes (snake_case)
// Money arrives as a decimal string, e.g. "8.50".

export interface ApiUserSummary {
  id: string
  name: string
  image: string | null
  faculty: string | null
}

export interface ApiListing {
  id: string
  title: string
  description: string
  price: string
  condition: "new" | "like_new" | "good" | "fair" | "poor"
  category: ItemCategory
  image: string | null
  spot: string
  status: "active" | "sold" | "removed"
  created_at: string
  seller: ApiUserSummary
  shop: ShopRef | null
}

export interface ApiService {
  id: string
  title: string
  description: string
  price: string
  unit: string | null
  category: ServiceCategory
  image: string | null
  spot: string
  created_at: string
  provider: ApiUserSummary
  shop: ShopRef | null
}

export interface ApiCafeteria {
  id: string
  name: string
  image: string | null
}

export interface ApiFoodItem {
  id: string
  name: string
  price: string
  meal_session: "lunch" | "dinner"
  available: boolean
  image: string | null
  is_demo: boolean
}

export interface ApiMenu {
  cafeteria: ApiCafeteria
  items: ApiFoodItem[]
}

export interface ApiMealDeliveryBatch {
  id: string
  provider_id: string
  meal_session: "lunch" | "dinner"
  delivery_date: string
  pickup_location: string
  status: "preparing" | "on_the_way" | "delivered"
  proof_image: string | null
  delivered_at: string | null
  provider: ApiCafeteria
}

export interface ApiMealOrderLine {
  item_id: string
  name: string
  quantity: number
  unit_price: string
}

export interface ApiMealOrder {
  id: string
  total: string
  status: string
  created_at: string
  provider: ApiCafeteria
  meal_session: "lunch" | "dinner"
  pickup_location: string
  delivery_batch: ApiMealDeliveryBatch
  lines: ApiMealOrderLine[]
}

export interface ApiProviderDeliveryBatch extends ApiMealDeliveryBatch {
  orders: {
    id: string
    student_name: string
    total: string
    lines: { name: string; quantity: number }[]
  }[]
}

export interface MealOrderPayload {
  meal_session: "lunch" | "dinner"
  pickup_location: string
  items: { item_id: string; quantity: number }[]
}

export interface MealMenuItemPayload {
  name: string
  price: string
  meal_session: "lunch" | "dinner"
  image?: string | null
}

export interface ApiShop {
  id: string
  name: string
  description: string
  logo: string | null
  location: string
  hours: string | null
  owner: ApiUserSummary
}

export interface ApiShopDetail extends ApiShop {
  listings: ApiListing[]
  services: ApiService[]
}

// ------------------------------------------------------------------ fetching

/** GET a backend path. Returns null on 404; throws on any other failure. */
async function get<T>(path: string): Promise<T | null> {
  const res = await fetch(`${API_URL}${path}`, { cache: "no-store" })
  if (res.status === 404) return null
  if (!res.ok) {
    throw new Error(`Serve API responded ${res.status} for ${path}`)
  }
  return (await res.json()) as T
}

async function getList<T>(path: string): Promise<T[]> {
  return (await get<T[]>(path)) ?? []
}

// ------------------------------------------------------------------ adapters

export function toStudent(user: ApiUserSummary): Student {
  return { id: user.id, name: user.name, faculty: user.faculty }
}

export function fromApiListing(listing: ApiListing): Listing {
  return {
    id: listing.id,
    title: listing.title,
    kind: "item",
    category: listing.category,
    price: Number(listing.price),
    image: listing.image ?? NO_PHOTO,
    seller: toStudent(listing.seller),
    spot: listing.spot,
    postedAt: listing.created_at,
    shop: listing.shop ?? undefined,
    href: `/listings/${listing.id}`,
  }
}

export function fromApiService(service: ApiService): Listing {
  return {
    id: service.id,
    title: service.title,
    kind: "service",
    category: service.category,
    price: Number(service.price),
    unit: service.unit ?? undefined,
    image: service.image ?? NO_PHOTO,
    seller: toStudent(service.provider),
    spot: service.spot,
    postedAt: service.created_at,
    shop: service.shop ?? undefined,
    href: `/services/${service.id}`,
  }
}

function newestFirst(a: Listing, b: Listing) {
  return Date.parse(b.postedAt) - Date.parse(a.postedAt)
}

// ------------------------------------------------------------------ queries

/**
 * Items and services matching the criteria, merged newest first.
 *
 * Each endpoint returns up to `limit` rows, then the merge keeps the first
 * `limit`. That is correct for one page; it can't page further.
 */
export async function searchCatalog(
  criteria: SearchCriteria,
  limit = 20
): Promise<Listing[]> {
  const params = new URLSearchParams({ limit: String(limit) })
  if (criteria.category) params.set("category", criteria.category)
  if (criteria.q) params.set("q", criteria.q)
  const query = params.toString()

  const [listings, services] = await Promise.all([
    criteria.type === "service"
      ? []
      : getList<ApiListing>(`/listings?${query}`),
    criteria.type === "item" ? [] : getList<ApiService>(`/services?${query}`),
  ])
  return [...listings.map(fromApiListing), ...services.map(fromApiService)]
    .sort(newestFirst)
    .slice(0, limit)
}

/** Newest items and services, merged. Fine for a short rail; not for paging. */
export function getFreshListings(limit = 8): Promise<Listing[]> {
  return searchCatalog({}, limit)
}

export function getCafeterias() {
  return getList<ApiCafeteria>("/cafeterias")
}

export function getMenu(cafeteriaId: string) {
  return get<ApiMenu>(`/cafeterias/${encodeURIComponent(cafeteriaId)}/menu`)
}

export async function getMealLocations() {
  return getList<string>("/meals/locations")
}

export function getShop(shopId: string) {
  return get<ApiShopDetail>(`/shops/${encodeURIComponent(shopId)}`)
}

export function getListing(listingId: string) {
  return get<ApiListing>(`/listings/${encodeURIComponent(listingId)}`)
}

export function getService(serviceId: string) {
  return get<ApiService>(`/services/${encodeURIComponent(serviceId)}`)
}
