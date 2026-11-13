import { createNeonAuth } from "@neon/auth/next/server"

/**
 * Server-side Neon Auth (Managed Better Auth). Use it in Server Components,
 * Server Actions and Route Handlers only. Pages that call it render dynamically.
 */
export const auth = createNeonAuth({
  baseUrl: process.env.NEON_AUTH_BASE_URL!,
  cookies: { secret: process.env.NEON_AUTH_COOKIE_SECRET! },
})
