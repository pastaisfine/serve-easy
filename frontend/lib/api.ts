/**
 * Server-side client for the ServeEasy FastAPI backend.
 *
 * Only call this from Server Components: `SERVE_API_URL` has no NEXT_PUBLIC_
 * prefix, so it is not available in the browser.
 */
import type {
  ItemCategory,
  Listing,
  ServiceCategory,
  ShopRef,
  Student,
} from "@/lib/types"

const API_URL = process.env.SERVE_API_URL ?? "http://localhost:8000"

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
}

export interface ApiMenu {
  cafeteria: ApiCafeteria
  items: ApiFoodItem[]
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
    // There is no service detail page yet; this shares the listing placeholder.
    href: `/listings/${service.id}`,
  }
}

function newestFirst(a: Listing, b: Listing) {
  return Date.parse(b.postedAt) - Date.parse(a.postedAt)
}

// ------------------------------------------------------------------ queries

/** Newest items and services, merged. Fine for a short rail; not for paging. */
export async function getFreshListings(limit = 8): Promise<Listing[]> {
  const [listings, services] = await Promise.all([
    getList<ApiListing>(`/listings?limit=${limit}`),
    getList<ApiService>(`/services?limit=${limit}`),
  ])
  return [...listings.map(fromApiListing), ...services.map(fromApiService)]
    .sort(newestFirst)
    .slice(0, limit)
}

export function getCafeterias() {
  return getList<ApiCafeteria>("/cafeterias")
}

export function getMenu(cafeteriaId: string) {
  return get<ApiMenu>(`/cafeterias/${encodeURIComponent(cafeteriaId)}/menu`)
}

export function getShop(shopId: string) {
  return get<ApiShopDetail>(`/shops/${encodeURIComponent(shopId)}`)
}
