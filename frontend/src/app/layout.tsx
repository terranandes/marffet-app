import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Sidebar from "../components/Sidebar";
import BottomTabBar from "../components/BottomTabBar";
import MobileTopBar from "../components/MobileTopBar";
import ClientProviders from "../components/ClientProviders";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Marffet Investment System",
  description: "Advanced Low-Volatility Stock Analysis",
  manifest: "/manifest.json",
  icons: {
    icon: "/icons/icon-192.png",
    apple: "/icons/apple-touch-icon.png",
  },
  other: {
    "viewport": "width=device-width, initial-scale=1, viewport-fit=cover",
    "apple-mobile-web-app-capable": "yes",
    "apple-mobile-web-app-status-bar-style": "black-translucent",
    "mobile-web-app-capable": "yes",
    "theme-color": "#050510",
  },
  openGraph: {
    title: "Marffet Investment System",
    description: "Advanced Low-Volatility Stock Analysis & Portfolio Tracking",
    url: "https://marffet-app.zeabur.app",
    siteName: "Marffet",
    images: [
      {
        url: "/martian_banner.png",
        width: 1200,
        height: 630,
        alt: "Marffet Investment System Dashboard",
      },
    ],
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Marffet Investment System",
    description: "Compare your portfolio against the Mars Strategy.",
    images: ["/martian_banner.png"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-[var(--color-bg)] text-[var(--color-text)] min-h-screen`}
        suppressHydrationWarning
      >
        <ClientProviders>
          <div className="flex min-h-screen">
            <Sidebar />
            <MobileTopBar />
            <main className="flex-1 lg:ml-64 pt-14 lg:pt-0 p-4 lg:p-8 pb-24 lg:pb-8 overflow-y-auto w-full max-w-full">
              {children}
            </main>
          </div>
          <BottomTabBar />
        </ClientProviders>
        <script
          dangerouslySetInnerHTML={{
            __html: `if('serviceWorker' in navigator){window.addEventListener('load',()=>navigator.serviceWorker.register('/sw.js'))}`,
          }}
        />
      </body>
    </html>
  );
}

