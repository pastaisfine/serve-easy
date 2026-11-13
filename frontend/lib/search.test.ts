import { describe, expect, test } from "vitest"

import { MAX_QUERY_LENGTH, parseSearchParams } from "@/lib/search"

describe("parseSearchParams", () => {
  test("returns no criteria for an empty URL", () => {
    expect(parseSearchParams({})).toEqual({})
  })

  test("keeps a valid item category", () => {
    expect(parseSearchParams({ type: "item", category: "books" })).toEqual({
      type: "item",
      category: "books",
    })
  })

  test("keeps a valid service category", () => {
    expect(
      parseSearchParams({ type: "service", category: "grooming" })
    ).toEqual({ type: "service", category: "grooming" })
  })

  test("drops a category that belongs to the other type", () => {
    expect(parseSearchParams({ type: "item", category: "grooming" })).toEqual({
      type: "item",
    })
  })

  test("drops a category without a type, since both have `other`", () => {
    expect(parseSearchParams({ category: "books" })).toEqual({})
    expect(parseSearchParams({ category: "other" })).toEqual({})
  })

  test("drops object prototype keys posing as categories", () => {
    expect(
      parseSearchParams({ type: "item", category: "constructor" })
    ).toEqual({ type: "item" })
  })

  test("drops an unknown type and its category", () => {
    expect(parseSearchParams({ type: "food", category: "books" })).toEqual({})
  })

  test("trims q and drops it when blank", () => {
    expect(parseSearchParams({ q: "  lamp  " })).toEqual({ q: "lamp" })
    expect(parseSearchParams({ q: "" })).toEqual({})
    expect(parseSearchParams({ q: "   " })).toEqual({})
  })

  test("ignores repeated params", () => {
    expect(
      parseSearchParams({ q: ["a", "b"], type: ["item", "service"] })
    ).toEqual({})
  })

  test("cuts an overlong q to the backend limit", () => {
    const { q } = parseSearchParams({ q: "x".repeat(150) })
    expect(q).toBe("x".repeat(MAX_QUERY_LENGTH))
  })

  test("counts code points when cutting, so emoji stay whole", () => {
    const { q } = parseSearchParams({ q: "😀".repeat(150) })
    expect(Array.from(q ?? "")).toHaveLength(MAX_QUERY_LENGTH)
    expect(q).toBe("😀".repeat(MAX_QUERY_LENGTH))
  })

  test("combines all three", () => {
    expect(
      parseSearchParams({ type: "service", category: "repair", q: "bike" })
    ).toEqual({ type: "service", category: "repair", q: "bike" })
  })
})
