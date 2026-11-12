import type { Metadata } from "next"
import { notFound } from "next/navigation"

import { PlaceholderPage } from "@/components/serve/placeholder-page"
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

export default async function CreatePage(props: PageProps<"/create/[kind]">) {
  const { kind } = await props.params
  const option = createOptions.find((o) => o.kind === kind)
  if (!option) notFound()

  return (
    <PlaceholderPage
      title={option.title}
      icon={option.icon}
      description={`The form for this goes here: ${option.description.toLowerCase()}, plus price, photos and campus meetup spots.`}
    />
  )
}
