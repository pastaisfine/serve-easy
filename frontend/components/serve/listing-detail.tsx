import Link from "next/link"
import { ImageIcon, MapPinIcon, StoreIcon } from "lucide-react"

import { PageHeader } from "@/components/serve/page-header"
import { StudentAvatar } from "@/components/serve/student"
import { Badge } from "@/components/ui/badge"
import { LoadingImage } from "@/components/ui/loading-image"
import { formatPrice } from "@/lib/format"
import type { ShopRef } from "@/lib/types"

export interface ListingDetailProps {
  title: string
  kind: "item" | "service"
  price: number
  unit?: string
  image: string | null
  category: string
  /** Items only, already a display name. */
  condition?: string
  description: string
  spot: string
  owner: { name: string; faculty: string | null }
  shop: ShopRef | null
  sold?: boolean
}

/** Read-only detail view shared by items and services. */
export function ListingDetail(props: ListingDetailProps) {
  const isService = props.kind === "service"

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-8 px-4 pt-10 md:px-8 md:pt-14">
      <PageHeader
        title={props.title}
        backHref={`/search?type=${props.kind}`}
        backLabel={isService ? "All services" : "All items"}
      >
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="secondary">{props.category}</Badge>
          {props.condition && <Badge variant="outline">{props.condition}</Badge>}
          {props.sold && <Badge variant="destructive">Sold</Badge>}
        </div>
      </PageHeader>

      <div className="grid gap-8 md:grid-cols-2 md:items-start">
        <div className="relative aspect-square overflow-hidden rounded-2xl bg-muted ring-1 ring-foreground/5">
          {props.image ? (
            <LoadingImage
              src={props.image}
              alt=""
              fill
              sizes="(min-width: 768px) 560px, 100vw"
              loading="eager"
              className="object-cover"
            />
          ) : (
            <div className="flex size-full flex-col items-center justify-center gap-2 text-muted-foreground">
              <ImageIcon aria-hidden className="size-10" />
              <span className="text-sm">No photo</span>
            </div>
          )}
        </div>

        <div className="flex flex-col gap-6">
          <p className="text-3xl font-semibold">
            {formatPrice(props.price, props.unit)}
          </p>

          {props.description && (
            <section aria-labelledby="about" className="flex flex-col gap-1.5">
              <h2 id="about" className="text-sm font-medium text-muted-foreground">
                {isService ? "About this service" : "About this item"}
              </h2>
              <p className="text-base whitespace-pre-line text-foreground/80">
                {props.description}
              </p>
            </section>
          )}

          <section aria-labelledby="where" className="flex flex-col gap-1.5">
            <h2 id="where" className="text-sm font-medium text-muted-foreground">
              {isService ? "Where it happens" : "Meetup spot"}
            </h2>
            <p className="flex items-start gap-1.5 text-base">
              <MapPinIcon aria-hidden className="mt-1 size-4 shrink-0" />
              {props.spot}
            </p>
          </section>

          <section
            aria-labelledby="by"
            className="flex flex-col gap-3 rounded-2xl bg-card p-4 ring-1 ring-foreground/5"
          >
            <h2 id="by" className="text-sm font-medium text-muted-foreground">
              {isService ? "Offered by" : "Sold by"}
            </h2>
            <div className="flex items-center gap-3">
              <StudentAvatar student={props.owner} size="lg" />
              <div className="flex flex-col">
                <span className="font-medium">{props.owner.name}</span>
                {props.owner.faculty && (
                  <span className="text-sm text-muted-foreground">
                    {props.owner.faculty}
                  </span>
                )}
              </div>
            </div>
            {props.shop && (
              <Link
                href={`/shops/${props.shop.id}`}
                className="flex w-fit items-center gap-1.5 text-sm font-medium underline-offset-2 hover:underline focus-visible:underline focus-visible:outline-none"
              >
                <StoreIcon aria-hidden className="size-4" />
                {props.shop.name}
              </Link>
            )}
          </section>
        </div>
      </div>
    </div>
  )
}
