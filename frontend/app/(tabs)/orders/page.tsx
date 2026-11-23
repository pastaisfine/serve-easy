import type { Metadata } from "next"
import { redirect } from "next/navigation"

import { MarketplaceRequests } from "@/components/serve/marketplace-requests"
import { PageHeader } from "@/components/serve/page-header"
import { getMyProductOrders, getMyServiceBookings } from "@/lib/api-write"
import { auth } from "@/lib/auth/server"

export const metadata: Metadata = { title: "Orders" }

export default async function OrdersPage() {
  const { data: session } = await auth.getSession()
  if (!session?.user) {
    redirect("/auth/sign-in?redirectTo=%2Forders")
  }
  const [productOrders, serviceBookings] = await Promise.all([
    getMyProductOrders(),
    getMyServiceBookings(),
  ])

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-6 px-4 pt-8 md:px-8 md:pt-12">
      <PageHeader title="Orders and requests" backHref="/" backLabel="Home">
        <p className="text-sm text-muted-foreground">
          Follow item requests and service bookings, and respond when someone
          contacts you.
        </p>
      </PageHeader>
      <section aria-labelledby="requests-heading">
        <div className="mb-3 flex items-baseline justify-between gap-4">
          <h2 id="requests-heading" className="text-lg font-semibold">
            Your marketplace activity
          </h2>
          <span className="text-sm text-muted-foreground">
            {productOrders.length + serviceBookings.length} requests
          </span>
        </div>
        <MarketplaceRequests
          productOrders={productOrders}
          serviceBookings={serviceBookings}
        />
      </section>
    </div>
  )
}
