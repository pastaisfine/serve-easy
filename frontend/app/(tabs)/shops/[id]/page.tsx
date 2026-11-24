import type { Metadata } from "next"
import { notFound } from "next/navigation"
import { ClockIcon, MapPinIcon } from "lucide-react"

import { ListingCard } from "@/components/serve/listing-card"
import { ContactLinks } from "@/components/serve/contact-links"
import { PageHeader } from "@/components/serve/page-header"
import { LoadingImage } from "@/components/ui/loading-image"
import { fromApiListing, fromApiService, getShop } from "@/lib/api"

export async function generateMetadata(
  props: PageProps<"/shops/[id]">
): Promise<Metadata> {
  const { id } = await props.params
  const shop = await getShop(id)
  return { title: shop?.name ?? "Shop" }
}

export default async function ShopPage(props: PageProps<"/shops/[id]">) {
  const { id } = await props.params
  const shop = await getShop(id)
  if (!shop) notFound()

  const listings = [
    ...shop.listings.map(fromApiListing),
    ...shop.services.map(fromApiService),
  ]

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-10 px-4 pt-10 md:px-8 md:pt-14">
      <div className="flex flex-col gap-6 md:flex-row md:items-start">
        {shop.logo && (
          <div className="relative size-28 shrink-0 overflow-hidden rounded-2xl bg-muted ring-1 ring-foreground/5">
            <LoadingImage
              src={shop.logo}
              alt={`${shop.name} logo`}
              fill
              sizes="112px"
              loading="eager"
              className="object-cover"
            />
          </div>
        )}
        <PageHeader title={shop.name} backHref="/" backLabel="Home">
          <p className="max-w-2xl text-base text-foreground/80">
            {shop.description}
          </p>
          <dl className="flex flex-col gap-1.5 text-sm text-muted-foreground">
            <div className="flex items-start gap-1.5">
              <dt>
                <MapPinIcon aria-hidden className="mt-0.5 size-4 shrink-0" />
                <span className="sr-only">Location</span>
              </dt>
              <dd>{shop.location}</dd>
            </div>
            {shop.hours && (
              <div className="flex items-start gap-1.5">
                <dt>
                  <ClockIcon aria-hidden className="mt-0.5 size-4 shrink-0" />
                  <span className="sr-only">Hours</span>
                </dt>
                <dd>{shop.hours}</dd>
              </div>
            )}
          </dl>
          <p className="text-sm text-muted-foreground">
            Run by {shop.owner.name}
            {shop.owner.faculty ? `, ${shop.owner.faculty}` : ""}
          </p>
          <ContactLinks
            whatsapp={shop.owner.whatsapp}
            telegramUsername={shop.owner.telegram_username}
          />
        </PageHeader>
      </div>

      <section aria-labelledby="shop-listings" className="flex flex-col gap-4">
        <h2
          id="shop-listings"
          className="text-2xl font-semibold tracking-tight"
        >
          From this shop
        </h2>
        {listings.length > 0 ? (
          <div className="grid grid-cols-2 gap-3 md:grid-cols-3 md:gap-4 lg:grid-cols-4">
            {listings.map((listing) => (
              <ListingCard key={listing.id} listing={listing} />
            ))}
          </div>
        ) : (
          <p className="rounded-2xl bg-card px-6 py-10 text-center text-base text-muted-foreground ring-1 ring-foreground/5">
            This shop has nothing listed on Serve.
          </p>
        )}
      </section>
    </div>
  )
}
