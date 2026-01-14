import type { NextConfig } from "next";

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
        source: "/auth/me",
        destination: `${API_URL}/auth/me`,
      },
    ];
  },
  async redirects() {
    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
    return [
      {
        source: "/auth/login",
        destination: `${API_URL}/auth/login`,
        permanent: false,
      },
      {
        source: "/auth/logout",
        destination: `${API_URL}/auth/logout`,
        permanent: false,
      },
    ];
  },
};

export default nextConfig;
