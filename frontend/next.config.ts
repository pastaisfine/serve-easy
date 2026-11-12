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
    ],
  },
}

export default nextConfig
