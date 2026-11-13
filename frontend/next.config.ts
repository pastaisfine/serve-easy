import type { NextConfig } from "next"

const nextConfig: NextConfig = {
  images: {
    // Placeholder photography until real listing uploads exist.
    remotePatterns: [
      {
        protocol: "https",
        hostname: "images.unsplash.com",
        pathname: "/**",
      },
      // Text placeholders from the backend seed (PNG only; SVG stays blocked).
      {
        protocol: "https",
        hostname: "placehold.co",
        pathname: "/**",
      },
    ],
  },
}

export default nextConfig
