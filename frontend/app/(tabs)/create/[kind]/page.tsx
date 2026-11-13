import type { Metadata } from "next"
import { notFound, redirect } from "next/navigation"

import { ListingForm } from "@/components/serve/listing-form"
import { PageHeader } from "@/components/serve/page-header"
import { PlaceholderPage } from "@/components/serve/placeholder-page"
import { getMe } from "@/lib/api-write"
import { auth } from "@/lib/auth/server"
import { createOptions } from "@/lib/create-options"

export function generateStaticParams() {
  return createOptions.map(({ kind }) => ({ kind }))
}

export const dynamicParams = false

export async function generateMetadata(
  props: PageProps<"/create/[kind]">
): Promise<Metadata> {
  const { kind } = await props.params
  return { title: createOptions.find((o) => o.kind === kind)?.title }
}

const intro = {
  "sell-item": "Add a photo and a few details. Your listing goes live right away.",
  "offer-service":
    "Tell students what you offer. Your service goes live right away.",
} as const

export default async function CreatePage(props: PageProps<"/create/[kind]">) {
  const { kind } = await props.params
  const option = createOptions.find((o) => o.kind === kind)
  if (!option) notFound()

  // Requests aren't built yet.
  if (kind !== "sell-item" && kind !== "offer-service") {
    return (
      <PlaceholderPage
        title={option.title}
        icon={option.icon}
        description={`The form for this goes here: ${option.description.toLowerCase()}, plus price, photos and campus meetup spots.`}
      />
    )
  }

  const { data: session } = await auth.getSession()
  if (!session?.user) redirect(`/auth/sign-in?redirectTo=/create/${kind}`)

  // The signed-in student's shop, if any, offers "List under my shop".
  const { shop } = await getMe()

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-6 px-4 pt-10 md:px-8 md:pt-14">
      <PageHeader title={option.title} backHref="/" backLabel="Home">
        <p className="max-w-2xl text-base text-muted-foreground">
          {intro[kind]}
        </p>
      </PageHeader>
      <ListingForm kind={kind} shop={shop} />
    </div>
  )
}
