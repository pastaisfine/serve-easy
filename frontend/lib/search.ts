import { itemCategoryNames, serviceCategoryNames } from "@/lib/categories"
import type { ItemCategory, ListingKind, ServiceCategory } from "@/lib/types"

/** The backend rejects a longer `q` with a 422. */
export const MAX_QUERY_LENGTH = 100

/** What to search for. Every field is optional; empty means "everything". */
export interface SearchCriteria {
  type?: ListingKind
  /** Only set together with `type`, and always valid for that type. */
  category?: ItemCategory | ServiceCategory
  q?: string
}

type RawParams = Record<string, string | string[] | undefined>

/** A repeated param (`?q=a&q=b`) arrives as an array; treat it as missing. */
function single(value: string | string[] | undefined) {
  return typeof value === "string" ? value : undefined
}

function parseType(value: string | undefined): ListingKind | undefined {
  return value === "item" || value === "service" ? value : undefined
}

/**
 * Drops a category the backend would reject. `Object.hasOwn` rather than
 * `in`, so keys such as "constructor" don't count.
 */
function parseCategory(
  type: ListingKind | undefined,
  value: string | undefined
) {
  if (!type || !value) return undefined
  const names = type === "item" ? itemCategoryNames : serviceCategoryNames
  return Object.hasOwn(names, value)
    ? (value as ItemCategory | ServiceCategory)
    : undefined
}

function parseQuery(value: string | undefined) {
  // Count code points, as the backend does, so an emoji isn't cut in half.
  const q = Array.from(value?.trim() ?? "")
    .slice(0, MAX_QUERY_LENGTH)
    .join("")
    .trim()
  return q || undefined
}

/** Turns raw `searchParams` into criteria the backend will accept. */
export function parseSearchParams(params: RawParams): SearchCriteria {
  const type = parseType(single(params.type))
  const category = parseCategory(type, single(params.category))
  const q = parseQuery(single(params.q))

  const criteria: SearchCriteria = {}
  if (type) criteria.type = type
  if (category) criteria.category = category
  if (q) criteria.q = q
  return criteria
}
