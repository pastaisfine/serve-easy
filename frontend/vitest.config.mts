import { defineConfig } from "vitest/config"

// Unit tests for plain modules. Async Server Components can't run under
// Vitest (see the Next.js testing guide), so pages are checked by hand.
export default defineConfig({
  resolve: {
    // Resolves the `@/` alias from tsconfig.json.
    tsconfigPaths: true,
  },
  test: {
    environment: "node",
  },
})
