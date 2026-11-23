import type { Offer, Order, Student } from "@/lib/types"

/**
 * Remaining mock data. Listings, categories and cafeterias now come from the
 * backend (see lib/api.ts). Orders stay mocked until auth exists; offers are
 * not in the PRD and are not rendered.
 * Photos are Unsplash placeholders (allowed in next.config.ts).
 */

const photo = (id: string, w = 600) =>
  `https://images.unsplash.com/photo-${id}?w=${w}&q=75&auto=format&fit=crop`

const students = {
  aiman: {
    id: "u1",
    name: "Aiman Hakim",
    faculty: "Faculty of Computing",
  },
  aisyah: {
    id: "u2",
    name: "Nur Aisyah",
    faculty: "Faculty of Mechanical Engineering",
  },
  daniel: {
    id: "u3",
    name: "Daniel Lim",
    faculty: "Faculty of Built Environment",
  },
  kavitha: {
    id: "u4",
    name: "Kavitha Raj",
    faculty: "Faculty of Science",
  },
  haziq: {
    id: "u5",
    name: "Haziq Firdaus",
    faculty: "Faculty of Electrical Engineering",
  },
  farah: {
    id: "u6",
    name: "Farah Izzati",
    faculty: "Azman Hashim International Business School",
  },
  weijie: {
    id: "u7",
    name: "Tan Wei Jie",
    faculty: "Faculty of Computing",
  },
} satisfies Record<string, Student>

export const offers: Offer[] = [
  {
    id: "o1",
    listing: {
      title: "Calculus: Early Transcendentals, Stewart 8th ed.",
      image: photo("1544947950-fa07a98d237f", 300),
      kind: "item",
      price: 60,
    },
    counterpart: students.weijie,
    summary: "Countered your RM 40 offer",
    offerPrice: 48,
    spot: "PSZ Library, main entrance",
    when: "Mon, 2 Nov, 11:00 am",
    expiresAt: "2026-11-01T18:00:00+08:00",
  },
  {
    id: "o2",
    listing: {
      title: "Sony WH-1000XM4 headphones, barely used",
      image: photo("1505740420928-5e560c06d30e", 300),
      kind: "item",
      price: 520,
    },
    counterpart: students.aisyah,
    summary: "Made an offer on your listing",
    offerPrice: 450,
    spot: "Arked Meranti",
    when: "Sun, 1 Nov, 4:00 pm",
    expiresAt: "2026-11-02T12:00:00+08:00",
  },
  {
    id: "o3",
    listing: {
      title: "Skin fade + beard trim, group booking for 4",
      image: photo("1621605815971-fbc98d665033", 300),
      kind: "service",
      price: 18,
      unit: "person",
    },
    counterpart: students.haziq,
    summary: "Sent you a custom group offer",
    offerPrice: 60,
    spot: "Kolej Tun Dr Ismail (KTDI)",
    when: "Sat, 31 Oct, 2:00 pm slot",
    expiresAt: "2026-10-31T10:00:00+08:00",
  },
]

export const orders: Order[] = [
  {
    id: "r1",
    role: "buying",
    listing: {
      title: "Banana pancake stack ×2",
      image: photo("1567620905732-2d1ec7ab7445", 300),
      kind: "item",
    },
    counterpart: students.farah,
    price: 16,
    status: "meetup_today",
    spot: "Arked Cengal",
    when: "Today, 5:30 pm",
    handoverCode: "4821",
  },
  {
    id: "r2",
    role: "selling",
    listing: {
      title: "Green 3-seater sofa",
      image: photo("1555041469-a586c61ea9bc", 300),
      kind: "item",
    },
    counterpart: students.daniel,
    price: 150,
    status: "meetup_scheduled",
    spot: "KTDI, Block M lobby",
    when: "Sat, 31 Oct, 10:00 am",
  },
  {
    id: "r3",
    role: "buying",
    listing: {
      title: "Skin fade haircut",
      image: photo("1599351431202-1e0f0137899a", 300),
      kind: "service",
    },
    counterpart: students.haziq,
    price: 15,
    status: "slot_booked",
    spot: "Kolej Rahman Putra (KRP)",
    when: "Sun, 1 Nov, 3:00 pm",
    handoverCode: "1907",
  },
]
