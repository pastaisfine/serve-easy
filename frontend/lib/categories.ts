import type {
  Category,
  ItemCategory,
  ListingKind,
  ServiceCategory,
} from "@/lib/types"

/** Display names, keyed by the backend's category values. */
export const itemCategoryNames: Record<ItemCategory, string> = {
  books: "Textbooks",
  electronics: "Tech & gadgets",
  furniture: "Furniture",
  clothing: "Clothing",
  kitchen: "Kitchen",
  stationery: "Stationery",
  sports: "Sports",
  other: "Other items",
}

export const serviceCategoryNames: Record<ServiceCategory, string> = {
  printing: "Printing",
  tailoring: "Tailoring",
  repair: "Repairs",
  grooming: "Haircuts & grooming",
  tutoring: "Tutoring",
  other: "Other services",
}

/**
 * `type` is part of the URL because both lists have an `other` value.
 * e.g. /search?type=item&category=books
 */
export function categoryHref(type: ListingKind, category: string) {
  return `/search?type=${type}&category=${category}`
}

export function categoryName(type: unknown, category: unknown) {
  if (typeof category !== "string") return undefined
  if (type === "service" && category in serviceCategoryNames) {
    return serviceCategoryNames[category as ServiceCategory]
  }
  if (type === "item" && category in itemCategoryNames) {
    return itemCategoryNames[category as ItemCategory]
  }
  return undefined
}

const photo = (id: string, w = 600) =>
  `https://images.unsplash.com/photo-${id}?w=${w}&q=75&auto=format&fit=crop`

/** The home page's category tiles. Food goes to cafeterias, not search. */
export const homeCategories: Category[] = [
  {
    key: "item:books",
    name: itemCategoryNames.books,
    image: photo("1512820790803-83ca734da794"),
    href: categoryHref("item", "books"),
  },
  {
    key: "item:electronics",
    name: itemCategoryNames.electronics,
    image: photo("1588508065123-287b28e013da"),
    href: categoryHref("item", "electronics"),
  },
  {
    key: "service:grooming",
    name: serviceCategoryNames.grooming,
    image: photo("1599351431202-1e0f0137899a"),
    href: categoryHref("service", "grooming"),
  },
  {
    key: "cafeterias",
    name: "Food & drinks",
    image: photo("1567620905732-2d1ec7ab7445"),
    href: "/cafeterias",
  },
  {
    key: "service:tutoring",
    name: serviceCategoryNames.tutoring,
    image: photo("1434030216411-0b793f4b4173"),
    href: categoryHref("service", "tutoring"),
  },
  {
    key: "service:repair",
    name: serviceCategoryNames.repair,
    image: photo("1517336714731-489689fd1ca8"),
    href: categoryHref("service", "repair"),
  },
]
