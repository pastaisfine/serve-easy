import type { NextConfig } from "next"

// Hostname of the Neon Object Storage endpoint that serves listing photos, e.g.
// br-xxx.storage.c-3.ap-southeast-1.aws.neon.tech. It differs per Neon branch.
const storageHost = process.env.STORAGE_PUBLIC_HOST

const nextConfig: NextConfig = {
  devIndicators: false,
  experimental: {
    agentUpgrade: "security",
    // Listing forms post the photo with the fields. The backend caps photos at
    // 4 MB; the rest is room for multipart overhead.
    serverActions: { bodySizeLimit: "5mb" },
  },
  images: {
    remotePatterns: [
      // Photos uploaded through the app (public-read bucket).
      ...(storageHost
        ? [
            {
              protocol: "https" as const,
              hostname: storageHost,
              pathname: "/uploads/**",
            },
          ]
        : []),
      // Placeholder photography used by the seed data.
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
