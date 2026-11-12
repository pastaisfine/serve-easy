import type { Metadata } from "next"
import { SearchIcon } from "lucide-react"

import { PlaceholderPage } from "@/components/serve/placeholder-page"
import { categories } from "@/lib/data"

export const metadata: Metadata = { title: "Search" }

export default async function SearchPage(props: PageProps<"/search">) {
  const { q, category } = await props.searchParams
  const query = typeof q === "string" ? q.trim() : ""
  const categoryName = categories.find((c) => c.slug === category)?.name

  const title = query ? `Results for "${query}"` : (categoryName ?? "Search")

  return (
    <PlaceholderPage
      title={title}
      icon={SearchIcon}
      description="Search results and filters (category, price, item or service, meetup spot) will live here."
    />
  )
}
