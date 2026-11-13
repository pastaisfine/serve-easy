import { afterEach, describe, expect, test, vi } from "vitest"

import { getFreshListings, searchCatalog } from "@/lib/api"
import type { ApiListing, ApiService } from "@/lib/api"

const person = { id: "u1", name: "Aisyah", image: null, faculty: null }

function apiListing(id: string, createdAt: string): ApiListing {
  return {
    id,
    title: `Listing ${id}`,
    description: "",
    price: "10.00",
    condition: "good",
    category: "books",
    image: null,
    spot: "PSZ",
    status: "active",
    created_at: createdAt,
    seller: person,
    shop: null,
  }
}

function apiService(id: string, createdAt: string): ApiService {
  return {
    id,
    title: `Service ${id}`,
    description: "",
    price: "5.00",
    unit: "hour",
    category: "repair",
    image: null,
    spot: "KTDI",
    created_at: createdAt,
    provider: person,
    shop: null,
  }
}

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  })
}

/** Answers /listings and /services with the given bodies; records each URL. */
function stubBackend(
  listings: ApiListing[] | Response = [],
  services: ApiService[] | Response = []
) {
  const fetchMock = vi.fn(async (input: string | URL | Request) => {
    const { pathname } = new URL(String(input))
    const body = pathname === "/listings" ? listings : services
    return body instanceof Response ? body : json(body)
  })
  vi.stubGlobal("fetch", fetchMock)
  return fetchMock
}

/** Path and query of every URL fetched, e.g. "/listings?limit=20". */
function calledPaths(fetchMock: ReturnType<typeof stubBackend>) {
  return fetchMock.mock.calls.map(([input]) => {
    const url = new URL(String(input))
    return url.pathname + url.search
  })
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe("searchCatalog", () => {
  test("queries both endpoints when no type is given", async () => {
    const fetchMock = stubBackend()
    await searchCatalog({})
    expect(calledPaths(fetchMock).sort()).toEqual([
      "/listings?limit=20",
      "/services?limit=20",
    ])
  })

  test("queries only /listings for items", async () => {
    const fetchMock = stubBackend()
    await searchCatalog({ type: "item", category: "books", q: "math" })
    expect(calledPaths(fetchMock)).toEqual([
      "/listings?limit=20&category=books&q=math",
    ])
  })

  test("queries only /services for services", async () => {
    const fetchMock = stubBackend()
    await searchCatalog({ type: "service", category: "repair" })
    expect(calledPaths(fetchMock)).toEqual([
      "/services?limit=20&category=repair",
    ])
  })

  test("sends q to both endpoints and encodes it", async () => {
    const fetchMock = stubBackend()
    await searchCatalog({ q: "a&b c" })
    expect(calledPaths(fetchMock).sort()).toEqual([
      "/listings?limit=20&q=a%26b+c",
      "/services?limit=20&q=a%26b+c",
    ])
  })

  test("merges items and services newest first", async () => {
    stubBackend(
      [
        apiListing("l-new", "2026-11-12T10:00:00Z"),
        apiListing("l-old", "2026-11-10T10:00:00Z"),
      ],
      [apiService("s-mid", "2026-11-11T10:00:00Z")]
    )
    const results = await searchCatalog({})
    expect(results.map((r) => [r.id, r.kind])).toEqual([
      ["l-new", "item"],
      ["s-mid", "service"],
      ["l-old", "item"],
    ])
  })

  test("caps the merged list at the limit", async () => {
    const day = (n: number) => `2026-11-${String(n).padStart(2, "0")}T00:00:00Z`
    stubBackend(
      [apiListing("l1", day(1)), apiListing("l3", day(3))],
      [apiService("s2", day(2)), apiService("s4", day(4))]
    )
    const results = await searchCatalog({}, 3)
    expect(results.map((r) => r.id)).toEqual(["s4", "l3", "s2"])
  })

  test("treats a 404 as an empty list", async () => {
    stubBackend(json({ detail: "Not Found" }, 404), [
      apiService("s1", "2026-11-12T00:00:00Z"),
    ])
    const results = await searchCatalog({})
    expect(results.map((r) => r.id)).toEqual(["s1"])
  })

  test("throws on a server error", async () => {
    stubBackend(json({ detail: "boom" }, 500))
    await expect(searchCatalog({ type: "item" })).rejects.toThrow(/500/)
  })
})

describe("getFreshListings", () => {
  test("asks both endpoints for the rail size, unfiltered", async () => {
    const fetchMock = stubBackend()
    await getFreshListings(8)
    expect(calledPaths(fetchMock).sort()).toEqual([
      "/listings?limit=8",
      "/services?limit=8",
    ])
  })
})
