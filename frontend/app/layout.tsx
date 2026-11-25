import type { Metadata, Viewport } from "next"
import { Inter } from "next/font/google"

import "./globals.css"
import { cn } from "@/lib/utils"

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" })

export const metadata: Metadata = {
  title: {
    default: "Serve · UTM student marketplace",
    template: "%s · Serve",
  },
  description:
    "Buy, sell and book from fellow UTM students. Textbooks, preloved goods, haircuts, food and more, handed over in person on campus.",
}

export const viewport: Viewport = {
  themeColor: "#f5f5f5",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    // suppressHydrationWarning: browser extensions (e.g. Locator) inject attributes
    // into <html>/<body> before React hydrates. It only silences attribute
    // mismatches on these two elements, not in their children.
    <html
      lang="en"
      className={cn("antialiased", inter.variable)}
      suppressHydrationWarning
    >
      <body suppressHydrationWarning>{children}</body>
    </html>
  )
}
