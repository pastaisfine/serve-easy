import type { Metadata } from "next"
import Link from "next/link"

import { PageHeader } from "@/components/serve/page-header"
import { LoadingImage } from "@/components/ui/loading-image"
import { getCafeterias } from "@/lib/api"

export const metadata: Metadata = { title: "Food & drinks" }

export default async function CafeteriasPage() {
  const cafeterias = await getCafeterias()

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-8 px-4 pt-10 md:px-8 md:pt-14">
      <PageHeader title="Food & drinks" backHref="/" backLabel="Home">
        <p className="text-base text-muted-foreground">
          Cafeterias taking orders for lunch and dinner.
        </p>
      </PageHeader>

      {cafeterias.length > 0 ? (
        <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {cafeterias.map((cafeteria, index) => (
            <li key={cafeteria.id}>
              <Link
                href={`/cafeterias/${cafeteria.id}`}
                className="group flex flex-col overflow-hidden rounded-2xl bg-card ring-1 ring-foreground/5 transition hover:ring-foreground/15 focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none"
              >
                <div className="relative aspect-[4/3] overflow-hidden bg-muted">
                  {cafeteria.image && (
                    <LoadingImage
                      src={cafeteria.image}
                      alt=""
                      fill
                      sizes="(min-width: 1024px) 270px, (min-width: 640px) 50vw, 100vw"
                      loading={index < 2 ? "eager" : "lazy"}
                      className="object-cover transition-transform duration-300 group-hover:scale-105"
                    />
                  )}
                </div>
                <span className="px-4 py-3 text-base font-medium">
                  {cafeteria.name}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      ) : (
        <p className="rounded-2xl bg-card px-6 py-10 text-center text-base text-muted-foreground ring-1 ring-foreground/5">
          No cafeterias are taking orders yet.
        </p>
      )}
    </div>
  )
}
