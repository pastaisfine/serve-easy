import Image from "next/image"
import Link from "next/link"
import { MapPinIcon } from "lucide-react"

import { MeetupCount, StudentAvatar } from "@/components/serve/student"
import { Badge } from "@/components/ui/badge"
import { formatPrice } from "@/lib/format"
import type { Listing } from "@/lib/types"

export function ListingCard({ listing }: { listing: Listing }) {
  return (
    <Link
      href={`/listings/${listing.id}`}
      className="group flex flex-col overflow-hidden rounded-2xl bg-card ring-1 ring-foreground/5 transition hover:ring-foreground/15 focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none"
    >
      <div className="relative aspect-square overflow-hidden bg-muted">
        <Image
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
        <p className="line-clamp-2 text-sm leading-snug text-foreground/80">
          {listing.title}
        </p>
        <p className="mt-auto flex flex-wrap items-baseline gap-x-1.5 pt-1">
          <span className="text-base font-semibold whitespace-nowrap">
            {formatPrice(listing.price, listing.unit)}
          </span>
          {listing.negotiable && (
            <span className="text-xs text-muted-foreground">Negotiable</span>
          )}
        </p>
        <div className="flex flex-col gap-0.5 text-xs">
          <span className="flex items-center gap-1 text-muted-foreground">
            <MapPinIcon aria-hidden className="size-3.5 shrink-0" />
            <span className="truncate">{listing.spot}</span>
          </span>
          <MeetupCount count={listing.seller.meetups} />
        </div>
      </div>
    </Link>
  )
}
