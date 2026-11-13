import { describe, expect, test } from "vitest"

import { categoryHref, categoryName } from "@/lib/categories"

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
