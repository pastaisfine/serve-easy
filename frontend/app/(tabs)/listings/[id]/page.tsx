import type { Metadata } from "next"
import { notFound } from "next/navigation"

import { ListingDetail } from "@/components/serve/listing-detail"
import { auth } from "@/lib/auth/server"
import { getListing } from "@/lib/api"
import { conditionNames, itemCategoryNames } from "@/lib/categories"

export async function generateMetadata(
  props: PageProps<"/listings/[id]">
): Promise<Metadata> {
  const { id } = await props.params
  const listing = await getListing(id)
  return { title: listing?.title ?? "Listing" }
}

export default async function ListingDetailPage(
  props: PageProps<"/listings/[id]">
) {
  const { id } = await props.params
  const listing = await getListing(id)
  if (!listing) notFound()
  const { data: session } = await auth.getSession()

  return (
    <ListingDetail
      recordId={listing.id}
      kind="item"
      title={listing.title}
      price={Number(listing.price)}
      image={listing.image}
      category={itemCategoryNames[listing.category]}
      condition={conditionNames[listing.condition]}
      description={listing.description}
      spot={listing.spot}
      owner={listing.seller}
      ownerId={listing.seller.id}
      viewerId={session?.user?.id ?? null}
      shop={listing.shop}
      sold={listing.status === "sold"}
      reserved={listing.status === "reserved"}
      isSignedIn={Boolean(session?.user)}
    />
  )
}
