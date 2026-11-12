import type { Category, Listing, Offer, Order, Student } from "@/lib/types"

/**
 * Mock data for the UI. Replace with backend calls once the API is ready.
 * Photos are Unsplash placeholders (allowed in next.config.ts).
 */

const photo = (id: string, w = 600) =>
  `https://images.unsplash.com/photo-${id}?w=${w}&q=75&auto=format&fit=crop`

export const currentUser: Student = {
  id: "me",
  name: "Alya Sofea",
  faculty: "Faculty of Computing",
  meetups: 9,
}

const students = {
  aiman: {
    id: "u1",
    name: "Aiman Hakim",
    faculty: "Faculty of Computing",
    meetups: 31,
    online: true,
  },
  aisyah: {
    id: "u2",
    name: "Nur Aisyah",
    faculty: "Faculty of Mechanical Engineering",
    meetups: 12,
  },
  daniel: {
    id: "u3",
    name: "Daniel Lim",
    faculty: "Faculty of Built Environment",
    meetups: 8,
  },
  kavitha: {
    id: "u4",
    name: "Kavitha Raj",
    faculty: "Faculty of Science",
    meetups: 19,
    online: true,
  },
  haziq: {
    id: "u5",
    name: "Haziq Firdaus",
    faculty: "Faculty of Electrical Engineering",
    meetups: 44,
    online: true,
  },
  farah: {
    id: "u6",
    name: "Farah Izzati",
    faculty: "Azman Hashim International Business School",
    meetups: 27,
  },
  weijie: {
    id: "u7",
    name: "Tan Wei Jie",
    faculty: "Faculty of Computing",
    meetups: 5,
  },
} satisfies Record<string, Student>

export const categories: Category[] = [
  {
    slug: "textbooks",
    name: "Textbooks",
    image: photo("1512820790803-83ca734da794"),
  },
  {
    slug: "preloved",
    name: "Preloved goods",
    image: photo("1523381210434-271e8be1f52b"),
  },
  {
    slug: "grooming",
    name: "Haircuts & grooming",
    image: photo("1599351431202-1e0f0137899a"),
  },
  {
    slug: "food",
    name: "Food & drinks",
    image: photo("1567620905732-2d1ec7ab7445"),
  },
  {
    slug: "tutoring",
    name: "Tutoring",
    image: photo("1434030216411-0b793f4b4173"),
  },
  {
    slug: "tech",
    name: "Tech & gadgets",
    image: photo("1588508065123-287b28e013da"),
  },
]

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

export const freshListings: Listing[] = [
  {
    id: "l1",
    title: "Engineering Mathematics, Stroud 7th ed.",
    kind: "item",
    category: "textbooks",
    price: 35,
    negotiable: true,
    image: photo("1495446815901-a7297e633e8d"),
    seller: students.kavitha,
    spot: "PSZ Library",
    postedAgo: "2h ago",
  },
  {
    id: "l2",
    title: "Haircut at your kolej",
    kind: "service",
    category: "grooming",
    price: 15,
    unit: "session",
    negotiable: false,
    image: photo("1585747860715-2ba37e788b70"),
    seller: students.haziq,
    spot: "Kolej Rahman Putra",
    postedAgo: "3h ago",
  },
  {
    id: "l3",
    title: 'MacBook Pro 13" M1, 2020',
    kind: "item",
    category: "tech",
    price: 2300,
    negotiable: true,
    image: photo("1517336714731-489689fd1ca8"),
    seller: students.aiman,
    spot: "Faculty of Computing, N28",
    postedAgo: "5h ago",
  },
  {
    id: "l4",
    title: "Iced latte, made to order",
    kind: "service",
    category: "food",
    price: 6.5,
    unit: "cup",
    negotiable: false,
    image: photo("1509042239860-f550ce710b93"),
    seller: students.farah,
    spot: "Arked Cengal",
    postedAgo: "6h ago",
  },
  {
    id: "l5",
    title: "Nike Free RN Flyknit, UK 8",
    kind: "item",
    category: "preloved",
    price: 90,
    negotiable: true,
    image: photo("1542291026-7eec264c27ff"),
    seller: students.daniel,
    spot: "Arked Lestari",
    postedAgo: "Yesterday",
  },
  {
    id: "l6",
    title: "Calculus & stats tutoring",
    kind: "service",
    category: "tutoring",
    price: 25,
    unit: "hour",
    negotiable: true,
    image: photo("1522202176988-66273c2fd55f"),
    seller: students.kavitha,
    spot: "PSZ discussion rooms",
    postedAgo: "Yesterday",
  },
  {
    id: "l7",
    title: "Succulent in ceramic pot",
    kind: "item",
    category: "preloved",
    price: 12,
    negotiable: false,
    image: photo("1485955900006-10f4d324d411"),
    seller: students.aisyah,
    spot: "KTDI",
    postedAgo: "2 days ago",
  },
  {
    id: "l8",
    title: "Nike SuperRep Go, UK 9",
    kind: "item",
    category: "preloved",
    price: 110,
    negotiable: true,
    image: photo("1606107557195-0e29a4b5b4aa"),
    seller: students.weijie,
    spot: "Arked Meranti",
    postedAgo: "2 days ago",
  },
]

/** Unread counts shown as badges in the nav. */
export const unread = { inbox: 2 }
