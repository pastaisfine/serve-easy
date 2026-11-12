/** Domain types for the Serve marketplace. Mirrors what the backend will eventually return. */

export type ListingKind = "item" | "service"

export type CategorySlug =
  "textbooks" | "preloved" | "grooming" | "food" | "tutoring" | "tech"

export interface Category {
  slug: CategorySlug
  name: string
  image: string
}

export interface Student {
  id: string
  name: string
  faculty: string
  /** Completed in-person handovers. This count is what "human authenticity" rests on. */
  meetups: number
  online?: boolean
}

export interface Listing {
  id: string
  title: string
  kind: ListingKind
  category: CategorySlug
  price: number
  /** e.g. "session", "hour". Only used for services. */
  unit?: string
  negotiable: boolean
  image: string
  seller: Student
  /** Campus meetup spot (items) or where the service happens. */
  spot: string
  postedAgo: string
}

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
