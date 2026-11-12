"use client"

import Link from "next/link"
import { PlusIcon } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet"
import { createGroups } from "@/lib/create-options"

/** Mobile: the centre '+' tab opens a bottom sheet. */
export function CreateSheet() {
  return (
    <Sheet>
      <SheetTrigger
        aria-label="Create a listing or request"
        className="flex size-12 items-center justify-center rounded-full bg-primary text-primary-foreground transition focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none active:scale-95"
      >
        <PlusIcon className="size-6" strokeWidth={2.5} />
      </SheetTrigger>
      <SheetContent
        side="bottom"
        className="rounded-t-3xl pb-[max(1.5rem,env(safe-area-inset-bottom))]"
      >
        <SheetHeader className="pb-2">
          <SheetTitle className="text-xl font-semibold">
            What would you like to do?
          </SheetTitle>
          <SheetDescription>
            Every deal on Serve ends with a meetup on campus.
          </SheetDescription>
        </SheetHeader>
        <div className="flex flex-col gap-5 px-6">
          {createGroups.map((group) => (
            <section key={group.label} aria-label={group.label}>
              <h3 className="mb-2 text-sm font-medium text-muted-foreground">
                {group.label}
              </h3>
              <ul className="flex flex-col gap-2">
                {group.options.map(
                  ({ kind, title, description, icon: Icon }) => (
                    <li key={kind}>
                      <SheetClose
                        render={<Link href={`/create/${kind}`} />}
                        nativeButton={false}
                        className="flex w-full items-center gap-4 rounded-2xl bg-muted p-4 text-left transition hover:bg-accent focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none active:scale-[0.99]"
                      >
                        <span className="flex size-11 shrink-0 items-center justify-center rounded-full bg-card">
                          <Icon className="size-5" />
                        </span>
                        <span className="flex flex-col">
                          <span className="text-base font-medium">{title}</span>
                          <span className="text-sm text-muted-foreground">
                            {description}
                          </span>
                        </span>
                      </SheetClose>
                    </li>
                  )
                )}
              </ul>
            </section>
          ))}
        </div>
      </SheetContent>
    </Sheet>
  )
}

/** Desktop: the same choices from a dropdown in the top bar. */
export function CreateDropdown() {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger render={<Button className="h-10 rounded-xl px-4" />}>
        <PlusIcon data-icon="inline-start" />
        Create
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-72">
        {createGroups.map((group, index) => (
          <DropdownMenuGroup key={group.label}>
            {index > 0 && <DropdownMenuSeparator />}
            <DropdownMenuLabel>{group.label}</DropdownMenuLabel>
            {group.options.map(({ kind, title, description, icon: Icon }) => (
              <DropdownMenuItem
                key={kind}
                render={<Link href={`/create/${kind}`} />}
                className="items-start py-2.5"
              >
                <Icon className="mt-0.5" />
                <span className="flex flex-col">
                  <span className="font-medium">{title}</span>
                  <span className="text-xs text-muted-foreground">
                    {description}
                  </span>
                </span>
              </DropdownMenuItem>
            ))}
          </DropdownMenuGroup>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
