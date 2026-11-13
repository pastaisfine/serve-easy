import type { Metadata } from "next"
import { SearchIcon } from "lucide-react"

import { PlaceholderPage } from "@/components/serve/placeholder-page"
import { categoryName } from "@/lib/categories"

export const metadata: Metadata = { title: "Search" }

export default async function SearchPage(props: PageProps<"/search">) {
  const { q, type, category } = await props.searchParams
  const query = typeof q === "string" ? q.trim() : ""
  const name = categoryName(type, category)

  const title = query ? `Results for "${query}"` : (name ?? "Search")

  return (
    <PlaceholderPage
      title={title}
      icon={SearchIcon}
      description="Search results will live here, with Items and Services tabs and filters for category, price and condition."
    />
  )
}
