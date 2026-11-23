"use client"

import Link from "next/link"
import { useState, useTransition } from "react"

import { placeMealOrder } from "@/app/(tabs)/meals/actions"
import { PageHeader } from "@/components/serve/page-header"
import { Button } from "@/components/ui/button"
import { NativeSelect } from "@/components/ui/native-select"
import type { ApiMenu, MealOrderPayload } from "@/lib/api"
import { formatPrice } from "@/lib/format"

type MealSession = MealOrderPayload["meal_session"]

const sessions: { id: MealSession; label: string; cutoff: string }[] = [
  { id: "lunch", label: "Lunch", cutoff: "10:30 AM" },
  { id: "dinner", label: "Dinner", cutoff: "4:30 PM" },
]

export function MealOrdering({
  menus,
  locations,
}: {
  menus: ApiMenu[]
  locations: string[]
}) {
  const [session, setSession] = useState<MealSession>("lunch")
  const [location, setLocation] = useState("")
  const [quantities, setQuantities] = useState<Record<string, number>>({})
  const [message, setMessage] = useState("")
  const [placedProviders, setPlacedProviders] = useState<string[]>([])
  const [needsSignIn, setNeedsSignIn] = useState(false)
  const [isPending, startTransition] = useTransition()

  const availableMenus = menus
    .map((menu) => ({
      ...menu,
      items: menu.items.filter(
        (item) => item.available && item.meal_session === session
      ),
    }))
    .filter((menu) => menu.items.length > 0)
  const cartItems = availableMenus.flatMap((menu) =>
    menu.items
      .filter((item) => (quantities[item.id] ?? 0) > 0)
      .map((item) => ({
        item,
        provider: menu.cafeteria.name,
        quantity: quantities[item.id],
      }))
  )
  const total = cartItems.reduce(
    (sum, line) => sum + Number(line.item.price) * line.quantity,
    0
  )

  function changeQuantity(itemId: string, delta: number) {
    setQuantities((current) => {
      const quantity = Math.max(0, Math.min(20, (current[itemId] ?? 0) + delta))
      const next = { ...current }
      if (quantity === 0) delete next[itemId]
      else next[itemId] = quantity
      return next
    })
    setMessage("")
    setPlacedProviders([])
  }

  function changeSession(next: MealSession) {
    setSession(next)
    setQuantities({})
    setMessage("")
    setPlacedProviders([])
  }

  function submitOrder() {
    if (!location || cartItems.length === 0) return

    const payload: MealOrderPayload = {
      meal_session: session,
      pickup_location: location,
      items: cartItems.map(({ item, quantity }) => ({
        item_id: item.id,
        quantity,
      })),
    }

    startTransition(async () => {
      const result = await placeMealOrder(payload)
      if (result.error) {
        setMessage(result.error)
        setNeedsSignIn(result.needsSignIn ?? false)
        return
      }
      setMessage("Order placed. Each provider has received its own order.")
      setNeedsSignIn(false)
      setPlacedProviders(
        [...new Set((result.data ?? []).map((order) => order.provider.name))]
      )
      setQuantities({})
    })
  }

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-8 px-4 pt-8 md:px-8 md:pt-12">
      <PageHeader title="Meals" backHref="/" backLabel="Home">
        <p className="text-sm text-muted-foreground">
          Order from campus food providers in one checkout. Choose a pickup
          point, then track the shared delivery updates.
        </p>
        <div className="flex flex-wrap gap-x-5 gap-y-2 pt-1 text-sm">
          <Link className="font-medium underline underline-offset-4" href="/meals/orders">
            My meal orders
          </Link>
          <Link className="font-medium underline underline-offset-4" href="/meals/manage">
            Provider workspace
          </Link>
        </div>
      </PageHeader>

      <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_20rem] lg:items-start">
        <section aria-labelledby="menu-heading" className="flex flex-col gap-6">
          <div className="flex flex-col gap-4 rounded-2xl bg-card p-4 sm:flex-row sm:items-end sm:justify-between sm:p-5">
            <fieldset className="flex flex-col gap-2">
              <legend className="mb-2 text-sm font-medium">Meal</legend>
              <div className="flex gap-2">
                {sessions.map((meal) => (
                  <Button
                    key={meal.id}
                    type="button"
                    variant={session === meal.id ? "secondary" : "outline"}
                    aria-pressed={session === meal.id}
                    onClick={() => changeSession(meal.id)}
                  >
                    {meal.label}
                  </Button>
                ))}
              </div>
            </fieldset>
            <p className="text-sm text-muted-foreground">
              Same-day orders close at{" "}
              {sessions.find((meal) => meal.id === session)?.cutoff}.
            </p>
          </div>

          <div>
            <h2 id="menu-heading" className="text-xl font-semibold">
              {session === "lunch" ? "Lunch" : "Dinner"} menus
            </h2>
            <p className="mt-1 text-sm text-muted-foreground">
              Sample menus for JojoeKopitiam, 芬姐, and 吉宝.
            </p>
          </div>

          {availableMenus.length > 0 ? (
            <div className="flex flex-col gap-8">
              {availableMenus.map((menu) => (
                <section key={menu.cafeteria.id} aria-label={menu.cafeteria.name}>
                  <div className="mb-3 flex items-baseline justify-between gap-4">
                    <h3 className="text-lg font-semibold">{menu.cafeteria.name}</h3>
                    <span className="text-xs uppercase tracking-wide text-muted-foreground">
                      Sample menu
                    </span>
                  </div>
                  <ul className="divide-y rounded-2xl bg-card px-4">
                    {menu.items.map((item) => (
                      <li
                        key={item.id}
                        className="flex items-center justify-between gap-4 py-4"
                      >
                        <div className="min-w-0">
                          <p className="font-medium">{item.name}</p>
                          <p className="mt-1 text-sm text-muted-foreground">
                            {formatPrice(Number(item.price))}
                          </p>
                        </div>
                        <div className="flex shrink-0 items-center gap-2">
                          <Button
                            type="button"
                            size="icon-sm"
                            variant="outline"
                            aria-label={`Remove one ${item.name}`}
                            disabled={!quantities[item.id]}
                            onClick={() => changeQuantity(item.id, -1)}
                          >
                            −
                          </Button>
                          <span
                            aria-live="polite"
                            className="w-5 text-center text-sm tabular-nums"
                          >
                            {quantities[item.id] ?? 0}
                          </span>
                          <Button
                            type="button"
                            size="icon-sm"
                            variant="outline"
                            aria-label={`Add one ${item.name}`}
                            disabled={(quantities[item.id] ?? 0) >= 20}
                            onClick={() => changeQuantity(item.id, 1)}
                          >
                            +
                          </Button>
                        </div>
                      </li>
                    ))}
                  </ul>
                </section>
              ))}
            </div>
          ) : (
            <p className="rounded-2xl bg-card px-5 py-8 text-sm text-muted-foreground">
              No {session} menu items are available right now.
            </p>
          )}
        </section>

        <aside className="lg:sticky lg:top-24">
          <section aria-labelledby="cart-heading" className="rounded-2xl bg-card p-5">
            <h2 id="cart-heading" className="text-lg font-semibold">
              Your order
            </h2>
            <div className="mt-4">
              <label htmlFor="meal-location" className="mb-2 block text-sm font-medium">
                Pickup point
              </label>
              <NativeSelect
                id="meal-location"
                value={location}
                onChange={(event) => setLocation(event.currentTarget.value)}
              >
                <option value="">Choose a campus location</option>
                {locations.map((place) => (
                  <option key={place} value={place}>
                    {place}
                  </option>
                ))}
              </NativeSelect>
            </div>
            {cartItems.length > 0 ? (
              <ul className="mt-4 divide-y text-sm">
                {cartItems.map(({ item, provider, quantity }) => (
                  <li
                    key={item.id}
                    className="flex justify-between gap-3 py-3 first:pt-0"
                  >
                    <span className="min-w-0">
                      <span className="block font-medium">{item.name}</span>
                      <span className="text-muted-foreground">
                        {provider} · {quantity} × {formatPrice(Number(item.price))}
                      </span>
                    </span>
                    <span className="shrink-0 tabular-nums">
                      {formatPrice(Number(item.price) * quantity)}
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="mt-4 text-sm text-muted-foreground">
                Add items from any provider to get started.
              </p>
            )}
            <div className="mt-4 flex justify-between border-t pt-4 font-semibold">
              <span>Estimated total</span>
              <span className="tabular-nums">{formatPrice(total)}</span>
            </div>
            <Button
              type="button"
              className="mt-4 w-full"
              disabled={isPending || !location || cartItems.length === 0}
              onClick={submitOrder}
            >
              {isPending ? "Placing order…" : "Place order"}
            </Button>
            <p className="mt-3 text-xs leading-relaxed text-muted-foreground">
              No payment is collected in this prototype. Your order is split
              automatically by provider.
            </p>
            {message && (
              <div role="status" className="mt-4 text-sm">
                <p>{message}</p>
                {needsSignIn && (
                  <Link
                    href="/auth/sign-in?redirectTo=%2Fcafeterias"
                    className="mt-1 inline-block font-medium underline"
                  >
                    Sign in to continue
                  </Link>
                )}
                {placedProviders.length > 0 && (
                  <Link
                    href="/meals/orders"
                    className="mt-1 inline-block font-medium underline"
                  >
                    Track {placedProviders.length} provider{" "}
                    {placedProviders.length === 1 ? "order" : "orders"}
                  </Link>
                )}
              </div>
            )}
          </section>
        </aside>
      </div>
    </div>
  )
}
