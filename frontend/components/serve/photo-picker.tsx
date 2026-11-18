"use client"

import { useEffect, useState } from "react"

import { FormField } from "@/components/serve/form-field"
import { Input } from "@/components/ui/input"
import { LoadingRing } from "@/components/ui/loading-ring"

const MAX_BYTES = 4 * 1024 * 1024
const TYPES = ["image/jpeg", "image/png", "image/webp"]

/**
 * File input with a preview. If a photo already uploaded in an earlier
 * attempt is passed in, it is kept (via hidden fields) unless a new file is chosen.
 */
export function PhotoPicker({
  uploaded,
  error,
}: {
  uploaded?: { key: string; url: string }
  error?: string
}) {
  const [preview, setPreview] = useState<string | null>(null)
  const [localError, setLocalError] = useState<string>()
  const [imageLoaded, setImageLoaded] = useState(false)

  // Blob URLs hold memory until revoked.
  useEffect(() => {
    return () => {
      if (preview) URL.revokeObjectURL(preview)
    }
  }, [preview])

  function onChange(event: React.ChangeEvent<HTMLInputElement>) {
    const input = event.currentTarget
    const file = input.files?.[0]
    setPreview(file ? URL.createObjectURL(file) : null)
    setImageLoaded(false)

    let problem = ""
    if (file && !TYPES.includes(file.type)) {
      problem = "Use a JPEG, PNG or WebP photo."
    } else if (file && file.size > MAX_BYTES) {
      problem = "That photo is over 4 MB. Choose a smaller one."
    }
    // A custom validity message also blocks form submission natively.
    input.setCustomValidity(problem)
    setLocalError(problem || undefined)
  }

  const shown = preview ?? uploaded?.url ?? null

  return (
    <div className="flex flex-col gap-3">
      <FormField
        label="Photo"
        optional
        hint="JPEG, PNG or WebP, up to 4 MB. Listings with a photo get noticed."
        error={localError ?? error}
      >
        <Input
          name="photo"
          type="file"
          accept={TYPES.join(",")}
          onChange={onChange}
          className="h-11 rounded-xl py-2"
        />
      </FormField>
      {shown && (
        <div className="relative aspect-square w-40 overflow-hidden rounded-2xl bg-muted ring-1 ring-foreground/5">
          {/* eslint-disable-next-line @next/next/no-img-element -- blob: previews can't go through next/image */}
          <img
            src={shown}
            alt="Preview of the selected photo"
            onLoad={() => setImageLoaded(true)}
            onError={() => setImageLoaded(true)}
            className="size-full object-cover"
          />
          {!imageLoaded && (
            <span
              aria-hidden="true"
              className="pointer-events-none absolute inset-0 flex items-center justify-center bg-muted/50"
            >
              <LoadingRing className="size-6 text-muted-foreground" />
            </span>
          )}
        </div>
      )}
      {uploaded && !preview && (
        <>
          <input type="hidden" name="photoKey" value={uploaded.key} />
          <input type="hidden" name="photoUrl" value={uploaded.url} />
        </>
      )}
    </div>
  )
}
