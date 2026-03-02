import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Sidebar from "../components/Sidebar";
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
            <main className="flex-1 md:ml-64 p-4 md:p-8 overflow-y-auto">
              {children}
            </main>
          </div>
        </ClientProviders>
      </body>
    </html>
  );
}

