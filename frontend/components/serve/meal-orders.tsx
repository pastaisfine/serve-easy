import Link from "next/link"

import { PageHeader } from "@/components/serve/page-header"
import { ContactLinks } from "@/components/serve/contact-links"
import { LoadingImage } from "@/components/ui/loading-image"
import type { ApiMealDeliveryBatch, ApiMealOrder } from "@/lib/api"
import { formatPrice } from "@/lib/format"

const deliveryLabels = {
  preparing: "Preparing",
  on_the_way: "On the way",
  delivered: "Delivered",
} as const

export function MealOrders({
  orders,
  batches,
}: {
  orders: ApiMealOrder[]
  batches: ApiMealDeliveryBatch[]
}) {
  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-10 px-4 pt-8 md:px-8 md:pt-12">
      <PageHeader title="Meal orders" backHref="/cafeterias" backLabel="Meals">
        <p className="text-sm text-muted-foreground">
          Your orders and today’s campus delivery drop points.
        </p>
      </PageHeader>

      <section aria-labelledby="my-meal-orders" className="flex flex-col gap-4">
        <div className="flex items-baseline justify-between gap-4">
          <h2 id="my-meal-orders" className="text-lg font-semibold">
            Your orders
          </h2>
          <span className="text-sm text-muted-foreground">
            {orders.length} {orders.length === 1 ? "provider" : "providers"}
          </span>
        </div>
        {orders.length > 0 ? (
          <ul className="divide-y rounded-2xl bg-card px-4">
            {orders.map((order) => (
              <li key={order.id} className="flex flex-col gap-2 py-4">
                <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
                  <h3 className="font-medium">{order.provider.name}</h3>
                  <span className="font-medium tabular-nums">
                    {formatPrice(Number(order.total))}
                  </span>
                </div>
                <ContactLinks
                  whatsapp={order.provider.whatsapp}
                  telegramUsername={order.provider.telegram_username}
                />
                <p className="text-sm text-muted-foreground">
                  {order.meal_session === "lunch" ? "Lunch" : "Dinner"} ·{" "}
                  {order.pickup_location}
                </p>
                <ul className="text-sm">
                  {order.lines.map((line) => (
                    <li key={line.item_id}>
                      {line.quantity} × {line.name}
                    </li>
                  ))}
                </ul>
                <p className="text-sm">
                  Delivery:{" "}
                  <span className="font-medium">
                    {deliveryLabels[order.delivery_batch.status]}
                  </span>
                </p>
                {order.delivery_batch.proof_image && (
                  <a
                    href={order.delivery_batch.proof_image}
                    target="_blank"
                    rel="noreferrer"
                    className="relative mt-1 block aspect-[16/7] max-w-md overflow-hidden rounded-xl focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none"
                  >
                    <LoadingImage
                      src={order.delivery_batch.proof_image}
                      alt={`${order.provider.name} delivery proof at ${order.pickup_location}`}
                      fill
                      sizes="(min-width: 768px) 448px, 100vw"
                      className="object-cover"
                    />
                  </a>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <p className="rounded-2xl bg-card px-5 py-6 text-sm text-muted-foreground">
            You haven’t placed a meal order today.{" "}
            <Link
              href="/cafeterias"
              className="font-medium text-foreground underline"
            >
              Browse today’s menus
            </Link>
            .
          </p>
        )}
      </section>

      <section
        aria-labelledby="campus-deliveries"
        className="flex flex-col gap-4"
      >
        <div>
          <h2 id="campus-deliveries" className="text-lg font-semibold">
            Campus delivery points
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Shared progress and delivery photos from today’s meal drops.
          </p>
        </div>
        {batches.length > 0 ? (
          <ul className="grid gap-x-8 md:grid-cols-2">
            {batches.map((batch) => (
              <li key={batch.id} className="flex flex-col gap-2 border-b py-4">
                <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
                  <h3 className="font-medium">{batch.pickup_location}</h3>
                  <span className="text-sm font-medium">
                    {deliveryLabels[batch.status]}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground">
                  {batch.provider.name} ·{" "}
                  {batch.meal_session === "lunch" ? "Lunch" : "Dinner"}
                </p>
                {batch.proof_image && (
                  <a
                    href={batch.proof_image}
                    target="_blank"
                    rel="noreferrer"
                    className="relative mt-1 block aspect-[16/7] overflow-hidden rounded-xl focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none"
                  >
                    <LoadingImage
                      src={batch.proof_image}
                      alt={`${batch.provider.name} delivery proof at ${batch.pickup_location}`}
                      fill
                      sizes="(min-width: 768px) 50vw, 100vw"
                      className="object-cover"
                    />
                  </a>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <p className="rounded-2xl bg-card px-5 py-6 text-sm text-muted-foreground">
            No campus delivery points have been updated yet today.
          </p>
        )}
      </section>
    </div>
  )
}
