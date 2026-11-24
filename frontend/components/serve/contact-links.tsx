export function ContactLinks({
  whatsapp,
  telegramUsername,
}: {
  whatsapp: string | null
  telegramUsername: string | null
}) {
  const phoneDigits = whatsapp?.replace(/\D/g, "") ?? ""
  const username = telegramUsername?.replace(/^@/, "") ?? ""
  const whatsappHref =
    phoneDigits.length >= 7 && phoneDigits.length <= 15
      ? `https://wa.me/${phoneDigits}`
      : null
  const telegramHref = username
    ? `https://t.me/${encodeURIComponent(username)}`
    : null

  if (!whatsappHref && !telegramHref) return null

  return (
    <div className="flex flex-wrap gap-2">
      {whatsappHref && (
        <a
          href={whatsappHref}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex min-h-10 items-center rounded-xl border px-3 text-sm font-medium underline-offset-4 hover:underline focus-visible:underline focus-visible:outline-none"
        >
          WhatsApp
        </a>
      )}
      {telegramHref && (
        <a
          href={telegramHref}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex min-h-10 items-center rounded-xl border px-3 text-sm font-medium underline-offset-4 hover:underline focus-visible:underline focus-visible:outline-none"
        >
          Telegram @{username}
        </a>
      )}
    </div>
  )
}
