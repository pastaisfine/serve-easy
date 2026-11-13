import { describe, expect, test } from "vitest"

import {
  categoryHref,
  categoryName,
  homeCategories,
  itemCategoryNames,
  serviceCategoryNames,
} from "@/lib/categories"

describe("categoryHref", () => {
  test("puts the type and category in the search URL", () => {
    expect(categoryHref("item", "books")).toBe(
      "/search?type=item&category=books"
    )
    expect(categoryHref("service", "repair")).toBe(
      "/search?type=service&category=repair"
    )
  })
})

describe("categoryName", () => {
  test("names a known item category", () => {
    expect(categoryName("item", "books")).toBe("Textbooks")
  })

  test("names a known service category", () => {
    expect(categoryName("service", "grooming")).toBe("Haircuts & grooming")
  })

  test("tells the two `other` categories apart", () => {
    expect(categoryName("item", "other")).toBe("Other items")
    expect(categoryName("service", "other")).toBe("Other services")
  })

  test("returns undefined when the category belongs to the other type", () => {
    expect(categoryName("item", "grooming")).toBeUndefined()
    expect(categoryName("service", "books")).toBeUndefined()
  })

  test("returns undefined for missing or non-string input", () => {
    expect(categoryName(undefined, "books")).toBeUndefined()
    expect(categoryName("item", undefined)).toBeUndefined()
    expect(categoryName("item", ["books"])).toBeUndefined()
  })
})

describe("new categories", () => {
  test("names the new item and service categories", () => {
    expect(categoryName("item", "snacks")).toBe("Snacks & vouchers")
    expect(categoryName("item", "tickets")).toBe("Tickets & passes")
    expect(categoryName("service", "media")).toBe("Photo & video")
    expect(categoryName("service", "rentals")).toBe("Rentals")
  })

  test("furniture is gone", () => {
    expect(categoryName("item", "furniture")).toBeUndefined()
  })
})

describe("homeCategories", () => {
  test("has a unique key and href per tile", () => {
    const keys = homeCategories.map((c) => c.key)
    const hrefs = homeCategories.map((c) => c.href)
    expect(new Set(keys).size).toBe(keys.length)
    expect(new Set(hrefs).size).toBe(hrefs.length)
  })

  test("every tile points at a real category (or the cafeterias)", () => {
    for (const tile of homeCategories) {
      if (tile.key === "cafeterias") continue
      const [type, category] = tile.key.split(":")
      expect(categoryName(type, category), tile.key).toBeDefined()
    }
  })

  test("has a tile for every category added in the overhaul", () => {
    const keys = new Set(homeCategories.map((c) => c.key))
    for (const c of ["snacks", "daily_essentials", "hobbies", "tickets"]) {
      expect(keys.has(`item:${c}`), c).toBe(true)
      expect(c in itemCategoryNames).toBe(true)
    }
    for (const c of ["design", "media", "programming", "errands", "rentals"]) {
      expect(keys.has(`service:${c}`), c).toBe(true)
      expect(c in serviceCategoryNames).toBe(true)
    }
  })
})
