import { cloneElement, isValidElement, useId } from "react"

/**
 * A label, optional hint and error around one control. The control gets its
 * id, `aria-describedby` and `aria-invalid` so screen readers announce both.
 */
export function FormField({
  label,
  hint,
  error,
  optional,
  children,
}: {
  label: string
  hint?: string
  error?: string
  optional?: boolean
  children: React.ReactElement<Record<string, unknown>>
}) {
  const id = useId()
  const hintId = `${id}-hint`
  const errorId = `${id}-error`
  const describedBy =
    [hint && hintId, error && errorId].filter(Boolean).join(" ") || undefined

  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={id} className="text-sm font-medium">
        {label}
        {optional && (
          <span className="font-normal text-muted-foreground"> (optional)</span>
        )}
      </label>
      {isValidElement(children) &&
        cloneElement(children, {
          id,
          "aria-describedby": describedBy,
          "aria-invalid": error ? true : undefined,
        })}
      {hint && (
        <p id={hintId} className="text-sm text-muted-foreground">
          {hint}
        </p>
      )}
      {error && (
        <p id={errorId} className="text-sm text-destructive">
          {error}
        </p>
      )}
    </div>
  )
}
