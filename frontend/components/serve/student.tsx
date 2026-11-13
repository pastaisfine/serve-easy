import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { initials } from "@/lib/format"
import type { Student } from "@/lib/types"

export function StudentAvatar({
  student,
  size = "default",
}: {
  student: Pick<Student, "name">
  size?: "default" | "sm" | "lg"
}) {
  return (
    <Avatar size={size}>
      <AvatarFallback className="bg-secondary font-medium text-foreground">
        {initials(student.name)}
      </AvatarFallback>
    </Avatar>
  )
}
