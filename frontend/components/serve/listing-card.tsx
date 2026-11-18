import Link from "next/link"
import { MapPinIcon, StoreIcon } from "lucide-react"

import { StudentAvatar } from "@/components/serve/student"
import { Badge } from "@/components/ui/badge"
import { LoadingImage } from "@/components/ui/loading-image"
import { formatPrice } from "@/lib/format"
import type { Listing } from "@/lib/types"

/**
 * The whole card is clickable through a stretched link on the title. The shop
 * link sits above it (z-10) so it stays a separate, valid link.
 */
export function ListingCard({ listing }: { listing: Listing }) {
  return (
    <article className="group relative flex flex-col overflow-hidden rounded-2xl bg-card ring-1 ring-foreground/5 transition focus-within:ring-[3px] focus-within:ring-ring/50 hover:ring-foreground/15">
      <div className="relative aspect-square overflow-hidden bg-muted">
        <LoadingImage
          src={listing.image}
          alt=""
          fill
          sizes="(min-width: 1024px) 270px, (min-width: 768px) 33vw, 50vw"
          className="object-cover transition-transform duration-300 group-hover:scale-105"
        />
        <Badge className="absolute top-2 left-2 h-6 bg-card/95 px-2.5 text-foreground">
          {listing.kind === "service" ? "Service" : "Item"}
        </Badge>
      </div>
      <div className="flex flex-1 flex-col gap-1.5 p-3">
        <div className="flex items-center gap-2">
          <StudentAvatar student={listing.seller} size="sm" />
          <span className="truncate text-sm font-medium">
            {listing.seller.name}
          </span>
        </div>
        <h3 className="line-clamp-2 text-sm leading-snug font-normal text-foreground/80">
          <Link
            href={listing.href}
            className="after:absolute after:inset-0 focus-visible:outline-none"
          >
            {listing.title}
          </Link>
        </h3>
        <p className="mt-auto pt-1 text-base font-semibold whitespace-nowrap">
          {formatPrice(listing.price, listing.unit)}
        </p>
        <div className="flex flex-col gap-0.5 text-xs">
          <span className="flex items-center gap-1 text-muted-foreground">
            <MapPinIcon aria-hidden className="size-3.5 shrink-0" />
            <span className="truncate">{listing.spot}</span>
          </span>
          {listing.shop && (
            <Link
              href={`/shops/${listing.shop.id}`}
              className="relative z-10 flex items-center gap-1 font-medium underline-offset-2 hover:underline focus-visible:underline focus-visible:outline-none"
            >
              <StoreIcon aria-hidden className="size-3.5 shrink-0" />
              <span className="truncate">{listing.shop.name}</span>
            </Link>
          )}
        </div>
      </div>
    </article>
  )
}
