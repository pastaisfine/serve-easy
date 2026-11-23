import type { Metadata } from "next"
import { redirect } from "next/navigation"

import { MealOrders } from "@/components/serve/meal-orders"
import {
  getMealDeliveryBatches,
  getMyMealOrders,
} from "@/lib/api-write"
import { auth } from "@/lib/auth/server"

export const metadata: Metadata = { title: "Meal orders" }

export default async function MealOrdersPage() {
  const { data: session } = await auth.getSession()
  if (!session?.user) {
    redirect("/auth/sign-in?redirectTo=%2Fmeals%2Forders")
  }

  const [orders, lunchBatches, dinnerBatches] = await Promise.all([
    getMyMealOrders(),
    getMealDeliveryBatches("lunch"),
    getMealDeliveryBatches("dinner"),
  ])
  const batches = [...lunchBatches, ...dinnerBatches]

  return <MealOrders orders={orders.orders} batches={batches} />
}
