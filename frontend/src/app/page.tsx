"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import StrategyCard from "@/components/StrategyCard";

export default function Home() {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    // Redirect to default page preference if set
    const defaultPage = localStorage.getItem("martian_default_page");
    if (defaultPage && defaultPage !== "/" && defaultPage !== "") {
      router.replace(defaultPage);
    }
  }, [router]);

  // Prevent flash of content if redirecting (optional, simple implementation)
  if (!mounted) return null;

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
            Mars Strategy System
          </h1>
          <p className="text-gray-400 mt-1">Select a module to begin</p>
        </div>
        <div className="flex gap-2 text-sm text-gray-500 bg-black/20 px-3 py-1.5 rounded-lg border border-white/5">
          <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
          System Online
        </div>
      </div>

      {/* Strategy Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <StrategyCard
          title="Mars Strategy"
          description="Core trend-following algorithmic trading system with real-time signals."
          icon="🚀"
          href="/mars"
          status="active"
          metrics={[
            { label: "Win Rate", value: "68%" },
            { label: "Active", value: "12" },
          ]}
        />

        <StrategyCard
          title="Portfolio"
          description="Track your assets, monitor performance and analyze allocation."
          icon="📊"
          href="/portfolio"
          status="active"
          metrics={[
            { label: "Assets", value: "8" },
            { label: "Value", value: "$42.5k" },
          ]}
        />

        <StrategyCard
          title="Data Visualization"
          description="Interactive bar chart races and historical performance visualization."
          icon="📈"
          href="/viz"
          status="active"
          metrics={[
            { label: "Data Points", value: "1.2M" },
            { label: "Charts", value: "4" },
          ]}
        />

        <StrategyCard
          title="Stock Discovery"
          description="AI-powered stock screener and market analysis tools."
          icon="🔍"
          href="/discovery"
          status="dev"
        />

        <StrategyCard
          title="Convertible Bonds"
          description="Advanced CB analysis and arbitrage opportunity finder."
          icon="💹"
          href="/cb"
          status="dev"
        />
      </div>

      {/* Quick Stats / System Info */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
        <div className="p-4 rounded-xl bg-white/5 border border-white/10">
          <div className="text-gray-400 text-sm mb-1">Market Status</div>
          <div className="text-xl font-bold text-green-400">Open</div>
        </div>
        <div className="p-4 rounded-xl bg-white/5 border border-white/10">
          <div className="text-gray-400 text-sm mb-1">Data Feed</div>
          <div className="text-xl font-bold text-blue-400">Live</div>
        </div>
        <div className="p-4 rounded-xl bg-white/5 border border-white/10">
          <div className="text-gray-400 text-sm mb-1">Next Rebalance</div>
          <div className="text-xl font-bold text-white">04:30:00</div>
        </div>
      </div>
    </div>
  );
}
