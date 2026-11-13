/**
 * View models the UI renders. Raw backend response shapes live in `lib/api.ts`,
 * which converts them into these.
 */

export type ListingKind = "item" | "service"

/** Must match the backend's `listing_category` enum. */
export type ItemCategory =
  | "books"
  | "electronics"
  | "clothing"
  | "kitchen"
  | "stationery"
  | "sports"
  | "snacks"
  | "daily_essentials"
  | "hobbies"
  | "tickets"
  | "other"

/** Must match the backend's `service_category` enum. */
export type ServiceCategory =
  | "printing"
  | "tailoring"
  | "repair"
  | "grooming"
  | "tutoring"
  | "design"
  | "media"
  | "programming"
  | "errands"
  | "rentals"
  | "other"

/** A home tile: either a listing category or a shortcut such as cafeterias. */
export interface Category {
  key: string
  name: string
  image: string
  href: string
}

export interface Student {
  id: string
  name: string
  faculty: string | null
}

export interface ShopRef {
  id: string
  name: string
  logo: string | null
}

/** An item listing or a service, rendered by the same card. */
export interface Listing {
  id: string
  title: string
  kind: ListingKind
  category: ItemCategory | ServiceCategory
  price: number
  /** e.g. "session", "hour". Only services have one. */
  unit?: string
  image: string
  seller: Student
  /** Free-text campus meetup spot (items) or where the service happens. */
  spot: string
  /** ISO timestamp, used to order the merged home feed. */
  postedAt: string
  /** Set when the listing belongs to a student shop. */
  shop?: ShopRef
  href: string
}

/** Mock only: not part of the PRD, and hidden on the home page. */
export interface Offer {
  id: string
  listing: Pick<Listing, "title" | "image" | "kind" | "price" | "unit">
  counterpart: Student
  /** Short line describing the offer, from the current user's point of view. */
  summary: string
  offerPrice: number
  /** Meetup spot, plus the time or booked slot. */
  spot: string
  when: string
  expiresAt: string
}

export type OrderStatus = "meetup_today" | "meetup_scheduled" | "slot_booked"

/** Mock only until orders and auth are wired to the backend. */
export interface Order {
  id: string
  role: "buying" | "selling"
  listing: Pick<Listing, "title" | "image" | "kind">
  counterpart: Student
  price: number
  status: OrderStatus
  spot: string
  when: string
  /** Shown to the buyer; the seller enters it at the meetup to confirm the in-person handover. */
  handoverCode?: string
}
