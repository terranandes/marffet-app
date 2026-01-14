import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://127.0.0.1:8000/api/:path*",
      },
      {
        source: "/auth/me",
        destination: "http://127.0.0.1:8000/auth/me",
      },
    ];
  },
  async redirects() {
    return [
      {
        source: "/auth/login",
        destination: "http://127.0.0.1:8000/auth/login",
        permanent: false,
      },
      {
        source: "/auth/logout",
        destination: "http://127.0.0.1:8000/auth/logout",
        permanent: false,
      },
    ];
  },
};

export default nextConfig;
