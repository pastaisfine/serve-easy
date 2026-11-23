import { AppNav } from "@/components/serve/app-nav"
import { getUnreadNotificationCount } from "@/lib/api-write"
import { auth } from "@/lib/auth/server"

export default async function TabsLayout({ children }: LayoutProps<"/">) {
  const { data: session, error } = await auth.getSession()
  if (error) throw new Error(error.message || "Could not verify your session.")
  const inboxCount = session?.user ? await getUnreadNotificationCount() : 0

  return (
    <>
      <AppNav inboxCount={inboxCount} />
      {/* Bottom padding keeps content clear of the floating mobile nav. */}
      <main className="min-h-svh pb-32 md:pb-16">{children}</main>
    </>
  )
}
