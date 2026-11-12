import {
  HandHelpingIcon,
  PackageIcon,
  PackageSearchIcon,
  ScissorsIcon,
  type LucideIcon,
} from "lucide-react"

export type CreateKind =
  "sell-item" | "offer-service" | "request-item" | "request-service"

export interface CreateOption {
  kind: CreateKind
  title: string
  description: string
  icon: LucideIcon
}

export interface CreateGroup {
  label: string
  options: CreateOption[]
}

/** The two branches of the '+' button: put something up, or ask for something. */
export const createGroups: CreateGroup[] = [
  {
    label: "Sell or provide",
    options: [
      {
        kind: "sell-item",
        title: "Sell an item",
        description: "Textbooks, gadgets, preloved stuff",
        icon: PackageIcon,
      },
      {
        kind: "offer-service",
        title: "Offer a service",
        description: "Haircuts, tutoring, food made to order",
        icon: ScissorsIcon,
      },
    ],
  },
  {
    label: "Request",
    options: [
      {
        kind: "request-item",
        title: "Request an item",
        description: "Tell sellers what you're looking for",
        icon: PackageSearchIcon,
      },
      {
        kind: "request-service",
        title: "Request a service",
        description: "Find someone who can help",
        icon: HandHelpingIcon,
      },
    ],
  },
]

export const createOptions = createGroups.flatMap((group) => group.options)
