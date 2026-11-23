import type { Metadata } from "next"
import { notFound } from "next/navigation"

import { ListingDetail } from "@/components/serve/listing-detail"
import { getService } from "@/lib/api"
import { auth } from "@/lib/auth/server"
import { serviceCategoryNames } from "@/lib/categories"

export async function generateMetadata(
  props: PageProps<"/services/[id]">
): Promise<Metadata> {
  const { id } = await props.params
  const service = await getService(id)
  return { title: service?.title ?? "Service" }
}

export default async function ServiceDetailPage(
  props: PageProps<"/services/[id]">
) {
  const { id } = await props.params
  const service = await getService(id)
  if (!service) notFound()
  const { data: session } = await auth.getSession()

  return (
    <ListingDetail
      recordId={service.id}
      kind="service"
      title={service.title}
      price={Number(service.price)}
      unit={service.unit ?? undefined}
      image={service.image}
      category={serviceCategoryNames[service.category]}
      description={service.description}
      spot={service.spot}
      owner={service.provider}
      ownerId={service.provider.id}
      viewerId={session?.user?.id ?? null}
      shop={service.shop}
      isSignedIn={Boolean(session?.user)}
    />
  )
}
