import Image from "next/image"
import Link from "next/link"
import { MapPinIcon } from "lucide-react"

import { StudentAvatar } from "@/components/serve/student"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { formatExpiry, formatPrice } from "@/lib/format"
import type { Offer } from "@/lib/types"

export function OfferCard({ offer }: { offer: Offer }) {
  const { listing, counterpart } = offer
  return (
    <Card className="w-[min(85vw,22rem)] shrink-0 snap-start gap-4 p-4 ring-foreground/5 md:w-auto">
      <div className="flex gap-4">
        <div className="relative size-24 shrink-0 overflow-hidden rounded-xl bg-muted ring-1 ring-foreground/5">
          <Image
            src={listing.image}
            alt=""
            fill
            sizes="96px"
            className="object-cover"
          />
        </div>
        <div className="flex min-w-0 flex-col gap-2">
          <div className="flex items-center gap-2.5">
            <StudentAvatar student={counterpart} />
            <span className="truncate text-base font-semibold">
              {counterpart.name}
            </span>
          </div>
          <p className="line-clamp-2 text-base leading-snug text-foreground/80">
            {listing.title}
          </p>
        </div>
      </div>

      <Separator />

      <div className="flex flex-col gap-1.5 text-sm text-muted-foreground">
        <p className="text-base text-foreground">
          <span className="font-semibold">{formatPrice(offer.offerPrice)}</span>
          <span className="text-muted-foreground">
            {" "}
            · asking {formatPrice(listing.price, listing.unit)}
          </span>
        </p>
        <p>{offer.summary}</p>
        <p className="flex items-start gap-1.5">
          <MapPinIcon aria-hidden className="mt-0.5 size-4 shrink-0" />
          <span>
            {offer.spot} · {offer.when}
          </span>
        </p>
        <p>Expires {formatExpiry(offer.expiresAt)}</p>
      </div>

      <div className="mt-auto grid grid-cols-2 gap-3">
        <Button
          variant="outline"
          className="h-11 rounded-xl border-foreground/30 bg-card text-base"
          nativeButton={false}
          render={<Link href={`/inbox?offer=${offer.id}`} />}
        >
          Open in Chat
        </Button>
        <Button
          className="h-11 rounded-xl text-base"
          nativeButton={false}
          render={<Link href={`/orders?offer=${offer.id}`} />}
        >
          Review
        </Button>
      </div>
    </Card>
  )
}
