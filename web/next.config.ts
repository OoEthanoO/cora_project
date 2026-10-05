import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",
  trailingSlash: true,
  // Caddy serves the original assets; there is no Next.js image server.
  images: { unoptimized: true },
};

export default nextConfig;
