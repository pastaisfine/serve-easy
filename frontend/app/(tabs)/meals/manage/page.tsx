import type { Metadata } from "next"
import Link from "next/link"
import { redirect } from "next/navigation"

import { ProviderMealWorkspace } from "@/components/serve/provider-meal-workspace"
import {
  getMe,
  getMyMealMenu,
  getMyMealProvider,
  getProviderMealOrders,
} from "@/lib/api-write"
import { auth } from "@/lib/auth/server"

export const metadata: Metadata = { title: "Provider workspace" }

export default async function ProviderMealPage() {
  const { data: session } = await auth.getSession()
  if (!session?.user) {
    redirect("/auth/sign-in?redirectTo=%2Fmeals%2Fmanage")
  }

  const user = await getMe()
  if (user.role !== "food_seller") {
    return (
      <div className="mx-auto flex max-w-2xl flex-col gap-4 px-4 pt-10 md:px-8 md:pt-14">
        <h1 className="text-3xl font-semibold tracking-tight">
          Provider workspace
        </h1>
        <p className="text-muted-foreground">
          This area is for registered food service staff accounts.
        </p>
        <Link href="/cafeterias" className="w-fit font-medium underline">
          Browse meal menus
        </Link>
      </div>
    )
  }

  const [provider, menu, batches] = await Promise.all([
    getMyMealProvider(),
    getMyMealMenu(),
    getProviderMealOrders(),
  ])

  return (
    <ProviderMealWorkspace
      provider={provider}
      menu={menu}
      batches={batches}
    />
  )
}
