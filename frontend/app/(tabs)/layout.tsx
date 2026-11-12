import { AppNav } from "@/components/serve/app-nav"
import { unread } from "@/lib/data"

export default function TabsLayout({ children }: LayoutProps<"/">) {
  return (
    <>
      <AppNav inboxCount={unread.inbox} />
      {/* Bottom padding keeps content clear of the floating mobile nav. */}
      <main className="min-h-svh pb-32 md:pb-16">{children}</main>
    </>
  )
}
