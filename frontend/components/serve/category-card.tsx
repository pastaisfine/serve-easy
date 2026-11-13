import Image from "next/image"
import Link from "next/link"

import type { Category } from "@/lib/types"

export function CategoryCard({
  category,
  eager,
}: {
  category: Category
  eager?: boolean
}) {
  return (
    <Link
      href={category.href}
      className="group flex w-40 shrink-0 snap-start flex-col overflow-hidden rounded-2xl bg-card ring-1 ring-foreground/5 transition focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none md:w-auto"
    >
      <div className="relative aspect-[4/3] overflow-hidden bg-muted">
        <Image
          src={category.image}
          alt=""
          fill
          sizes="(min-width: 1024px) 180px, 176px"
          loading={eager ? "eager" : "lazy"}
          className="object-cover transition-transform duration-300 group-hover:scale-105"
        />
      </div>
      <span className="flex min-h-16 items-center px-4 py-3 text-base leading-snug font-medium">
        {category.name}
      </span>
    </Link>
  )
}
