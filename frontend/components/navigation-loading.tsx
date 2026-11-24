"use client"

import { useEffect, useState } from "react"
import { usePathname } from "next/navigation"

import { LoadingScreen } from "@/app/loading"

export function NavigationLoading({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const [targetPath, setTargetPath] = useState<string | null>(null)

  useEffect(() => {
    function showOnInternalNavigation(event: MouseEvent) {
      if (
        event.button !== 0 ||
        event.metaKey ||
        event.ctrlKey ||
        event.shiftKey ||
        event.altKey
      ) {
        return
      }

      const target = event.target
      if (!(target instanceof Element)) return

      const anchor = target.closest("a")
      if (!anchor) return
      if (anchor.target && anchor.target !== "_self") return

      const url = new URL(anchor.href, window.location.href)
      if (
        url.origin === window.location.origin &&
        url.pathname !== window.location.pathname
      ) {
        setTargetPath(url.pathname)
      }
    }

    document.addEventListener("click", showOnInternalNavigation, true)
    return () => {
      document.removeEventListener("click", showOnInternalNavigation, true)
    }
  }, [])

  return (
    <>
      {children}
      {targetPath !== null && targetPath !== pathname ? <LoadingScreen /> : null}
    </>
  )
}
