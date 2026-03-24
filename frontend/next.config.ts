import type { NextConfig } from "next";
import { withSentryConfig } from "@sentry/nextjs";

const nextConfig: NextConfig = {
  output: "standalone",
  async rewrites() {
    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
    return [
      {
        source: "/api/:path*",
        destination: `${API_URL}/api/:path*`,
      },
      {
        source: "/auth/:path*",
        destination: `${API_URL}/auth/:path*`,
      },
    ];
  },
  async redirects() {
    return [
      // Auth moved to rewrites to solve Cross-Domain Cookie issues
    ];
  },
};

export default withSentryConfig(nextConfig, {
  silent: true,
  org: "marffet",
  project: "frontend",
  widenClientFileUpload: true,
  tunnelRoute: "/monitoring",
  sourcemaps: {
    deleteSourcemapsAfterUpload: true,
  },
  disableLogger: true,
});
