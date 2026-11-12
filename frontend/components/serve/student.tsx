import { HandshakeIcon } from "lucide-react"

import { Avatar, AvatarBadge, AvatarFallback } from "@/components/ui/avatar"
import { initials } from "@/lib/format"
import type { Student } from "@/lib/types"
import { cn } from "@/lib/utils"

export function StudentAvatar({
  student,
  size = "default",
}: {
  student: Student
  size?: "default" | "sm" | "lg"
}) {
  return (
    <Avatar size={size}>
      <AvatarFallback className="bg-secondary font-medium text-foreground">
        {initials(student.name)}
      </AvatarFallback>
      {student.online && (
        <AvatarBadge className="bg-brand">
          <span className="sr-only">Online</span>
        </AvatarBadge>
      )}
    </Avatar>
  )
}

/**
 * Count of completed in-person handovers. This is the trust signal Serve
 * shows in place of star ratings.
 */
export function MeetupCount({
  count,
  className,
}: {
  count: number
  className?: string
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 text-muted-foreground",
        className
      )}
    >
      <HandshakeIcon className="size-3.5" aria-hidden />
      {count} meetups
    </span>
  )
}
