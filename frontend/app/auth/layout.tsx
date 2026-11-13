import { Logo } from "@/components/serve/logo"

export default function AuthLayout({ children }: LayoutProps<"/auth">) {
  return (
    <main className="mx-auto flex min-h-svh w-full max-w-md flex-col justify-center gap-8 px-4 py-10">
      <Logo className="self-center" />
      {children}
    </main>
  )
}
