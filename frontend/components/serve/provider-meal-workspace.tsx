"use client"

import { useRouter } from "next/navigation"
import { useState, useTransition } from "react"

import {
  addMealMenuItem,
  setMealItemAvailability,
  updateMealBatch,
  uploadMealDeliveryPhoto,
} from "@/app/(tabs)/meals/actions"
import { PageHeader } from "@/components/serve/page-header"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import type {
  ApiCafeteria,
  ApiFoodItem,
  ApiProviderDeliveryBatch,
  MealMenuItemPayload,
} from "@/lib/api"
import { formatPrice } from "@/lib/format"

type MealSession = MealMenuItemPayload["meal_session"]

const sessionLabels: Record<MealSession, string> = {
  lunch: "Lunch",
  dinner: "Dinner",
}

function DeliveryBatchCard({
  batch,
  refresh,
}: {
  batch: ApiProviderDeliveryBatch
  refresh: () => void
}) {
  const [message, setMessage] = useState("")
  const [isPending, startTransition] = useTransition()

  function markOnTheWay() {
    startTransition(async () => {
      const result = await updateMealBatch(batch.id, "on_the_way")
      if (result.error) {
        setMessage(result.error)
        return
      }
      setMessage("")
      refresh()
    })
  }

  function markDelivered(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = event.currentTarget
    const formData = new FormData(form)
    startTransition(async () => {
      const upload = await uploadMealDeliveryPhoto(formData)
      if (upload.error || !upload.data) {
        setMessage(upload.error ?? "The delivery photo could not be uploaded.")
        return
      }
      const result = await updateMealBatch(batch.id, "delivered", upload.data.key)
      if (result.error) {
        setMessage(result.error)
        return
      }
      setMessage("")
      refresh()
    })
  }

  return (
    <li className="flex flex-col gap-4 border-b py-5 last:border-0">
      <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
        <div>
          <h3 className="font-semibold">{batch.pickup_location}</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            {sessionLabels[batch.meal_session]} · {batch.orders.length}{" "}
            {batch.orders.length === 1 ? "student order" : "student orders"}
          </p>
        </div>
        <span className="text-sm font-medium">
          {batch.status === "preparing"
            ? "Preparing"
            : batch.status === "on_the_way"
              ? "On the way"
              : "Delivered"}
        </span>
      </div>

      <ul className="flex flex-col gap-3 text-sm">
        {batch.orders.map((order) => (
          <li key={order.id} className="rounded-xl bg-background px-3 py-3">
            <div className="flex justify-between gap-3">
              <span className="font-medium">{order.student_name}</span>
              <span className="shrink-0 tabular-nums">
                {formatPrice(Number(order.total))}
              </span>
            </div>
            <ul className="mt-1 text-muted-foreground">
              {order.lines.map((line, index) => (
                <li key={`${line.name}-${index}`}>
                  {line.quantity} × {line.name}
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ul>

      {batch.status === "preparing" && (
        <Button
          type="button"
          variant="outline"
          className="w-fit"
          disabled={isPending}
          onClick={markOnTheWay}
        >
          {isPending ? "Updating…" : "Mark on the way"}
        </Button>
      )}
      {batch.status === "on_the_way" && (
        <form onSubmit={markDelivered} className="flex flex-col gap-3">
          <label htmlFor={`proof-${batch.id}`} className="text-sm font-medium">
            Delivery proof photo
          </label>
          <Input
            id={`proof-${batch.id}`}
            name="photo"
            type="file"
            accept="image/jpeg,image/png,image/webp"
            required
            className="h-auto min-h-11 rounded-xl py-2"
          />
          <Button type="submit" className="w-fit" disabled={isPending}>
            {isPending ? "Saving delivery…" : "Mark delivered"}
          </Button>
        </form>
      )}
      {message && (
        <p role="alert" className="text-sm text-destructive">
          {message}
        </p>
      )}
    </li>
  )
}

export function ProviderMealWorkspace({
  provider,
  menu,
  batches,
}: {
  provider: ApiCafeteria
  menu: ApiFoodItem[]
  batches: ApiProviderDeliveryBatch[]
}) {
  const router = useRouter()
  const [session, setSession] = useState<MealSession>("lunch")
  const [message, setMessage] = useState("")
  const [isPending, startTransition] = useTransition()
  const visibleMenu = menu.filter((item) => item.meal_session === session)
  const visibleBatches = batches.filter((batch) => batch.meal_session === session)

  function addItem(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = event.currentTarget
    const values = new FormData(form)
    const name = values.get("name")
    const price = values.get("price")
    const meal = values.get("meal_session")
    if (
      typeof name !== "string" ||
      typeof price !== "string" ||
      (meal !== "lunch" && meal !== "dinner")
    ) {
      setMessage("Enter a name, price, and meal session.")
      return
    }

    const payload: MealMenuItemPayload = {
      name,
      price,
      meal_session: meal,
    }
    startTransition(async () => {
      const result = await addMealMenuItem(payload)
      if (result.error) {
        setMessage(result.error)
        return
      }
      setMessage("Menu item added.")
      form.reset()
      router.refresh()
    })
  }

  function toggleAvailability(item: ApiFoodItem) {
    startTransition(async () => {
      const result = await setMealItemAvailability(item.id, !item.available)
      if (result.error) {
        setMessage(result.error)
        return
      }
      setMessage("")
      router.refresh()
    })
  }

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-8 px-4 pt-8 md:px-8 md:pt-12">
      <PageHeader title="Provider workspace" backHref="/cafeterias" backLabel="Meals">
        <p className="text-sm text-muted-foreground">
          {provider.name} · manage sample menu availability and campus drops.
        </p>
      </PageHeader>

      <div className="flex gap-2" aria-label="Meal session">
        {(["lunch", "dinner"] as const).map((value) => (
          <Button
            key={value}
            type="button"
            variant={session === value ? "secondary" : "outline"}
            aria-pressed={session === value}
            onClick={() => setSession(value)}
          >
            {sessionLabels[value]}
          </Button>
        ))}
      </div>

      <section aria-labelledby="provider-menu-heading" className="flex flex-col gap-4">
        <div>
          <h2 id="provider-menu-heading" className="text-xl font-semibold">
            {sessionLabels[session]} menu
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Change availability or add a menu item for this session.
          </p>
        </div>

        <ul className="divide-y rounded-2xl bg-card px-4">
          {visibleMenu.length > 0 ? (
            visibleMenu.map((item) => (
              <li
                key={item.id}
                className="flex flex-wrap items-center justify-between gap-3 py-4"
              >
                <div>
                  <p className="font-medium">{item.name}</p>
                  <p className="mt-1 text-sm text-muted-foreground">
                    {formatPrice(Number(item.price))}
                    {item.is_demo && " · Sample"}
                  </p>
                </div>
                <Button
                  type="button"
                  size="sm"
                  variant={item.available ? "outline" : "secondary"}
                  disabled={isPending}
                  onClick={() => toggleAvailability(item)}
                >
                  {item.available ? "Available" : "Unavailable"}
                </Button>
              </li>
            ))
          ) : (
            <li className="py-5 text-sm text-muted-foreground">
              No menu items for this meal yet.
            </li>
          )}
        </ul>

        <form
          onSubmit={addItem}
          className="grid gap-3 rounded-2xl bg-card p-4 sm:grid-cols-[1fr_9rem_auto] sm:items-end"
        >
          <div>
            <label htmlFor="menu-item-name" className="mb-2 block text-sm font-medium">
              Item name
            </label>
            <Input
              id="menu-item-name"
              name="name"
              required
              maxLength={120}
              placeholder="e.g. Chicken rice"
              className="h-11 rounded-xl"
            />
          </div>
          <div>
            <label htmlFor="menu-item-price" className="mb-2 block text-sm font-medium">
              Price (RM)
            </label>
            <Input
              id="menu-item-price"
              name="price"
              type="number"
              min="0.01"
              max="99999.99"
              step="0.01"
              required
              placeholder="8.50"
              className="h-11 rounded-xl"
            />
          </div>
          <input type="hidden" name="meal_session" value={session} />
          <Button type="submit" disabled={isPending}>
            {isPending ? "Saving…" : "Add item"}
          </Button>
        </form>
        {message && (
          <p role="status" className="text-sm text-muted-foreground">
            {message}
          </p>
        )}
      </section>

      <section aria-labelledby="provider-deliveries-heading" className="flex flex-col gap-4">
        <div>
          <h2 id="provider-deliveries-heading" className="text-xl font-semibold">
            Today’s {sessionLabels[session].toLowerCase()} delivery drops
          </h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Orders are grouped by pickup point. Post a photo when the drop is delivered.
          </p>
        </div>
        {visibleBatches.length > 0 ? (
          <ul className="divide-y rounded-2xl bg-card px-4">
            {visibleBatches.map((batch) => (
              <DeliveryBatchCard
                key={batch.id}
                batch={batch}
                refresh={() => router.refresh()}
              />
            ))}
          </ul>
        ) : (
          <p className="rounded-2xl bg-card px-5 py-6 text-sm text-muted-foreground">
            No orders for this meal session today.
          </p>
        )}
      </section>
    </div>
  )
}
