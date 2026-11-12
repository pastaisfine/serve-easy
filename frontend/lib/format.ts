const whole = new Intl.NumberFormat("en-MY", { maximumFractionDigits: 0 })
const cents = new Intl.NumberFormat("en-MY", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
})

/** RM 1,250 / RM 6.50 / RM 25 / hour */
export function formatPrice(amount: number, unit?: string) {
  const number = Number.isInteger(amount) ? whole : cents
  const value = `RM ${number.format(amount)}`
  return unit ? `${value} / ${unit}` : value
}

const expiry = new Intl.DateTimeFormat("en-MY", {
  timeZone: "Asia/Kuala_Lumpur",
  weekday: "short",
  day: "numeric",
  month: "short",
  hour: "numeric",
  minute: "2-digit",
})

/** Fixed timezone so server and client always render the same string. */
export function formatExpiry(iso: string) {
  return expiry.format(new Date(iso))
}

export function initials(name: string) {
  return name
    .split(" ")
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase()
}
