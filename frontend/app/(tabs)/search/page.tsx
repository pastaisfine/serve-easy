import type { Metadata } from "next"

import { ListingCard } from "@/components/serve/listing-card"
import { SearchBar } from "@/components/serve/search-bar"
import { searchCatalog } from "@/lib/api"
import { categoryName } from "@/lib/categories"
import { parseSearchParams, type SearchCriteria } from "@/lib/search"

export const metadata: Metadata = { title: "Search" }

function pageTitle({ type, category, q }: SearchCriteria) {
  if (q) return `Results for "${q}"`
  return categoryName(type, category) ?? "Search"
}

function emptyMessage({ category, q }: SearchCriteria) {
  if (q) return `No results for "${q}".`
  if (category) return "Nothing in this category yet."
  return "Nothing listed yet."
}

export default async function SearchPage(props: PageProps<"/search">) {
  const criteria = parseSearchParams(await props.searchParams)
  const results = await searchCatalog(criteria)

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-6 px-4 pt-6 md:gap-8 md:px-8 md:pt-10">
      <SearchBar defaultValue={criteria.q} />
      <h1 className="text-3xl font-semibold tracking-tight">
        {pageTitle(criteria)}
      </h1>
      {results.length > 0 ? (
        <div className="grid grid-cols-2 gap-3 md:grid-cols-3 md:gap-4 lg:grid-cols-4">
          {results.map((listing) => (
            <ListingCard key={listing.id} listing={listing} />
          ))}
        </div>
      ) : (
        <p className="rounded-2xl bg-card px-6 py-10 text-center text-base text-muted-foreground ring-1 ring-foreground/5">
          {emptyMessage(criteria)}
        </p>
      )}
    </div>
  )
}
