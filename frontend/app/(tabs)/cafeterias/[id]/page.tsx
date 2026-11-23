import type { Metadata } from "next"
import { notFound } from "next/navigation"

import { PageHeader } from "@/components/serve/page-header"
import { getMenu, type ApiFoodItem } from "@/lib/api"
import { formatPrice } from "@/lib/format"

export async function generateMetadata(
  props: PageProps<"/cafeterias/[id]">
): Promise<Metadata> {
  const { id } = await props.params
  const menu = await getMenu(id)
  return { title: menu?.cafeteria.name ?? "Cafeteria" }
}

const sessions = [
  { key: "lunch", label: "Lunch" },
  { key: "dinner", label: "Dinner" },
] as const

export default async function CafeteriaMenuPage(
  props: PageProps<"/cafeterias/[id]">
) {
  const { id } = await props.params
  const menu = await getMenu(id)
  if (!menu) notFound()

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-8 px-4 pt-10 md:px-8 md:pt-14">
      <PageHeader
        title={menu.cafeteria.name}
        backHref="/cafeterias"
        backLabel="All cafeterias"
      >
        <p className="text-base text-muted-foreground">
          Add items from multiple providers to one order from the Meals page.
        </p>
      </PageHeader>

      {sessions.map(({ key, label }) => (
        <MenuSection
          key={key}
          label={label}
          items={menu.items.filter((item) => item.meal_session === key)}
        />
      ))}
    </div>
  )
}

function MenuSection({ label, items }: { label: string; items: ApiFoodItem[] }) {
  const headingId = `menu-${label.toLowerCase()}`
  return (
    <section aria-labelledby={headingId} className="flex flex-col gap-3">
      <h2 id={headingId} className="text-xl font-semibold tracking-tight">
        {label}
      </h2>
      {items.length > 0 ? (
        <ul className="divide-y rounded-2xl bg-card ring-1 ring-foreground/5">
          {items.map((item) => (
            <li
              key={item.id}
              className="flex items-baseline justify-between gap-4 px-4 py-3"
            >
              <span className="text-base">{item.name}</span>
              <span className="text-base font-semibold whitespace-nowrap tabular-nums">
                {formatPrice(Number(item.price))}
              </span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-base text-muted-foreground">
          Nothing on the {label.toLowerCase()} menu.
        </p>
      )}
    </section>
  )
}
