import type {
  Category,
  ItemCategory,
  ListingCondition,
  ListingKind,
  ServiceCategory,
} from "@/lib/types"

/** Display names for an item's condition, best first. */
export const conditionNames: Record<ListingCondition, string> = {
  new: "Brand new",
  like_new: "Like new",
  good: "Good",
  fair: "Fair",
  poor: "Well used",
}

/** Display names, keyed by the backend's category values. */
export const itemCategoryNames: Record<ItemCategory, string> = {
  books: "Textbooks",
  electronics: "Tech & gadgets",
  clothing: "Clothing",
  kitchen: "Kitchen",
  stationery: "Stationery",
  sports: "Sports",
  snacks: "Snacks & vouchers",
  daily_essentials: "Daily essentials",
  hobbies: "Hobbies & games",
  tickets: "Tickets & passes",
  other: "Other items",
}

export const serviceCategoryNames: Record<ServiceCategory, string> = {
  printing: "Printing",
  tailoring: "Tailoring",
  repair: "Repairs",
  grooming: "Haircuts & grooming",
  tutoring: "Tutoring",
  design: "Design",
  media: "Photo & video",
  programming: "Programming",
  errands: "Errands & help",
  rentals: "Rentals",
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

/**
 * The home page's category tiles: item categories, then the cafeterias
 * shortcut, then services. Photos are hand-picked Unsplash images and some are
 * loose matches. Food goes to cafeterias, not search.
 */
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
    key: "item:hobbies",
    name: itemCategoryNames.hobbies,
    image: photo("1510915361894-db8b60106cb1"),
    href: categoryHref("item", "hobbies"),
  },
  {
    key: "item:snacks",
    name: itemCategoryNames.snacks,
    image: photo("1664854678365-ad59da72356c"),
    href: categoryHref("item", "snacks"),
  },
  {
    key: "item:daily_essentials",
    name: itemCategoryNames.daily_essentials,
    image: photo("1656214296523-2de8d388c115"),
    href: categoryHref("item", "daily_essentials"),
  },
  {
    key: "item:tickets",
    name: itemCategoryNames.tickets,
    image: photo("1578575436955-ef29da568c6c"),
    href: categoryHref("item", "tickets"),
  },
  {
    key: "cafeterias",
    name: "Food & drinks",
    image: photo("1567620905732-2d1ec7ab7445"),
    href: "/cafeterias",
  },
  {
    key: "service:grooming",
    name: serviceCategoryNames.grooming,
    image: photo("1599351431202-1e0f0137899a"),
    href: categoryHref("service", "grooming"),
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
    image: photo("1721333089073-215a56fd710c"),
    href: categoryHref("service", "repair"),
  },
  {
    key: "service:design",
    name: serviceCategoryNames.design,
    image: photo("1626785774573-4b799315345d"),
    href: categoryHref("service", "design"),
  },
  {
    key: "service:media",
    name: serviceCategoryNames.media,
    image: photo("1541516160071-4bb0c5af65ba"),
    href: categoryHref("service", "media"),
  },
  {
    key: "service:programming",
    name: serviceCategoryNames.programming,
    image: photo("1607799279861-4dd421887fb3"),
    href: categoryHref("service", "programming"),
  },
  {
    key: "service:errands",
    name: serviceCategoryNames.errands,
    image: photo("1695653422259-8a74ffe90401"),
    href: categoryHref("service", "errands"),
  },
  {
    key: "service:rentals",
    name: serviceCategoryNames.rentals,
    image: photo("1683821291931-068148564d8c"),
    href: categoryHref("service", "rentals"),
  },
]
