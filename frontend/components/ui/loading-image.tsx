"use client"

import Image, { type ImageProps } from "next/image"
import { useState } from "react"

import { LoadingRing } from "@/components/ui/loading-ring"

export function LoadingImage(props: ImageProps) {
  const [loadedSrc, setLoadedSrc] = useState<ImageProps["src"] | null>(null)
  const loaded = loadedSrc === props.src

  return (
    <>
      <Image
        {...props}
        alt={props.alt}
        onLoad={() => setLoadedSrc(props.src)}
        onError={() => setLoadedSrc(props.src)}
      />
      {!loaded && (
        <span
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 flex items-center justify-center bg-muted/50"
        >
          <LoadingRing className="size-6 text-muted-foreground" />
        </span>
      )}
    </>
  )
}
