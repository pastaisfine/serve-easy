"use client"

import type { ComponentProps, ReactNode } from "react"
import { useFormStatus } from "react-dom"

import { Button } from "@/components/ui/button"
import { LoadingRing } from "@/components/ui/loading-ring"

export function LoadingSubmitButton({
  children,
  disabled,
  pendingLabel,
  ...props
}: ComponentProps<typeof Button> & { pendingLabel: ReactNode }) {
  const { pending } = useFormStatus()

  return (
    <Button
      {...props}
      type={props.type ?? "submit"}
      disabled={disabled || pending}
      aria-busy={pending}
    >
      {pending && <LoadingRing className="size-4" />}
      {pending ? pendingLabel : children}
    </Button>
  )
}
