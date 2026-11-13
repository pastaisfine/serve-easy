import Form from "next/form"
import { SearchIcon } from "lucide-react"

import { Input } from "@/components/ui/input"

export function SearchBar({ defaultValue }: { defaultValue?: string }) {
  return (
    <Form action="/search" role="search" className="relative">
      <label htmlFor="home-search" className="sr-only">
        Search Serve
      </label>
      <SearchIcon
        aria-hidden
        className="pointer-events-none absolute top-1/2 left-4 size-5 -translate-y-1/2 text-muted-foreground"
      />
      <Input
        // Remount when the query changes so the field shows the new value.
        key={defaultValue}
        id="home-search"
        name="q"
        type="search"
        defaultValue={defaultValue}
        placeholder="Search textbooks, goods, services"
        className="h-14 rounded-2xl border-transparent bg-card pl-12 text-base shadow-[0_2px_12px_rgb(0_0_0/0.06)] md:text-base"
      />
    </Form>
  )
}
