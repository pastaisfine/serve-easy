import type { Metadata } from "next"

import { MealOrdering } from "@/components/serve/meal-ordering"
import { getCafeterias, getMealLocations, getMenu } from "@/lib/api"

export const metadata: Metadata = { title: "Meals" }

export default async function CafeteriasPage() {
  const [providers, locations] = await Promise.all([
    getCafeterias(),
    getMealLocations(),
  ])
  const menus = (
    await Promise.all(providers.map((provider) => getMenu(provider.id)))
  ).filter((menu) => menu !== null)

  return <MealOrdering menus={menus} locations={locations} />
}
