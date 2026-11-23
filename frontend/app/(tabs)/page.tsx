import Link from "next/link"
import { BellIcon } from "lucide-react"

import { CategoryCard } from "@/components/serve/category-card"
import { ListingCard } from "@/components/serve/listing-card"
import { Logo } from "@/components/serve/logo"
import { MarketplaceRequests } from "@/components/serve/marketplace-requests"
import { SearchBar } from "@/components/serve/search-bar"
import { Rail, Section } from "@/components/serve/section"
import { getFreshListings } from "@/lib/api"
import { getMyProductOrders, getMyServiceBookings } from "@/lib/api-write"
import { auth } from "@/lib/auth/server"
import { homeCategories } from "@/lib/categories"

export default async function HomePage() {
  const [{ data: session }, freshListings] = await Promise.all([
    auth.getSession(),
    getFreshListings(8),
  ])
  const [productOrders, serviceBookings] = session?.user
    ? await Promise.all([getMyProductOrders(), getMyServiceBookings()])
    : [[], []]

  return (
    <>
      <div className="bg-surface pb-6 md:pt-10 md:pb-10">
        <div className="mx-auto flex max-w-6xl flex-col gap-5 px-4 md:px-8">
          {/* Mobile header: centred wordmark, like Fiverr. The desktop top bar replaces it. */}
          <div className="relative flex items-center justify-center pt-6 md:hidden">
            <Logo />
            <Link
              href="/inbox"
              aria-label="Notifications"
              className="absolute right-0 flex size-10 items-center justify-center rounded-full hover:bg-muted focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none"
            >
              <BellIcon className="size-6" />
            </Link>
          </div>
          <h1 className="sr-only md:not-sr-only md:text-3xl md:font-semibold md:tracking-tight">
            Buy, sell and book around UTM
          </h1>
          <SearchBar />
        </div>
      </div>

      <div className="mx-auto flex max-w-6xl flex-col gap-10 px-4 pt-6 md:gap-14 md:px-8 md:pt-10">
        <Section id="categories" title="Categories" seeAllHref="/search">
          <Rail className="lg:mx-0 lg:grid lg:grid-cols-5 lg:overflow-visible lg:px-0">
            {homeCategories.map((category, index) => (
              <CategoryCard
                key={category.key}
                category={category}
                eager={index < 3}
              />
            ))}
          </Rail>
        </Section>

        {/* "Offers for you" is hidden: offers are not part of the PRD. */}

        <Section id="orders" title="My active requests" seeAllHref="/orders">
          {session?.user ? (
            <MarketplaceRequests
              productOrders={productOrders}
              serviceBookings={serviceBookings}
              compact
              activeOnly
            />
          ) : (
            <p className="rounded-2xl bg-card px-5 py-6 text-sm text-muted-foreground">
              <Link
                href="/auth/sign-in?redirectTo=%2Forders"
                className="font-medium text-foreground underline"
              >
                Sign in
              </Link>{" "}
              to see your item requests and service bookings.
            </p>
          )}
        </Section>

        <Section id="fresh" title="Fresh on campus" seeAllHref="/search">
          {freshListings.length > 0 ? (
            <div className="grid grid-cols-2 gap-3 md:grid-cols-3 md:gap-4 lg:grid-cols-4">
              {freshListings.map((listing) => (
                <ListingCard key={listing.id} listing={listing} />
              ))}
            </div>
          ) : (
            <p className="rounded-2xl bg-card px-6 py-10 text-center text-base text-muted-foreground ring-1 ring-foreground/5">
              Nothing listed yet. Check back soon.
            </p>
          )}
        </Section>
      </div>
    </>
  )
}
