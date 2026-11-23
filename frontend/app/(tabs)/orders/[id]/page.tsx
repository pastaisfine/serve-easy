import type { Metadata } from "next"
import { notFound, redirect } from "next/navigation"

import { MarketplaceRequests } from "@/components/serve/marketplace-requests"
import { PageHeader } from "@/components/serve/page-header"
import {
  ApiError,
  getProductOrder,
  getServiceBooking,
} from "@/lib/api-write"
import { auth } from "@/lib/auth/server"

export const metadata: Metadata = { title: "Order details" }

export default async function OrderDetailPage(
  props: PageProps<"/orders/[id]">
) {
  const { id } = await props.params
  const { data: session } = await auth.getSession()
  if (!session?.user) {
    redirect(`/auth/sign-in?redirectTo=${encodeURIComponent(`/orders/${id}`)}`)
  }

  if (id.startsWith("item-")) {
    let order
    try {
      order = await getProductOrder(id.slice("item-".length))
    } catch (error) {
      if (error instanceof ApiError && error.status === 404) notFound()
      throw error
    }
    return (
      <div className="mx-auto flex max-w-4xl flex-col gap-6 px-4 pt-8 md:px-8 md:pt-12">
        <PageHeader title="Purchase request" backHref="/orders" backLabel="Orders" />
        <MarketplaceRequests productOrders={[order]} serviceBookings={[]} />
      </div>
    )
  }

  if (id.startsWith("booking-")) {
    let booking
    try {
      booking = await getServiceBooking(id.slice("booking-".length))
    } catch (error) {
      if (error instanceof ApiError && error.status === 404) notFound()
      throw error
    }
    return (
      <div className="mx-auto flex max-w-4xl flex-col gap-6 px-4 pt-8 md:px-8 md:pt-12">
        <PageHeader title="Service booking" backHref="/orders" backLabel="Orders" />
        <MarketplaceRequests productOrders={[]} serviceBookings={[booking]} />
      </div>
    )
  }

  notFound()
}
