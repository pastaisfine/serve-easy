import type { Metadata } from "next"
import { redirect } from "next/navigation"

import { AuthForm } from "@/components/serve/auth-form"
import { getCafeterias } from "@/lib/api"
import { safeRedirect } from "@/lib/auth/redirect"
import { auth } from "@/lib/auth/server"

export const metadata: Metadata = { title: "Create account" }

export default async function SignUpPage(props: PageProps<"/auth/sign-up">) {
  const { redirectTo } = await props.searchParams
  const target = safeRedirect(redirectTo)

  const { data: session } = await auth.getSession()
  if (session?.user) redirect(target)

  const providers = await getCafeterias()
  return <AuthForm mode="sign-up" redirectTo={target} providers={providers} />
}
