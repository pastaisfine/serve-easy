import type { Metadata } from "next"
import { redirect } from "next/navigation"

import { AuthForm } from "@/components/serve/auth-form"
import { safeRedirect } from "@/lib/auth/redirect"
import { auth } from "@/lib/auth/server"

export const metadata: Metadata = { title: "Sign in" }

export default async function SignInPage(props: PageProps<"/auth/sign-in">) {
  const { redirectTo } = await props.searchParams
  const target = safeRedirect(redirectTo)

  const { data: session } = await auth.getSession()
  if (session?.user) redirect(target)

  return <AuthForm mode="sign-in" redirectTo={target} />
}
