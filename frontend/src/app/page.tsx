"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import StrategyCard from "@/components/StrategyCard";
import { useLanguage } from "@/lib/i18n/LanguageContext";

export default function Home() {
  const router = useRouter();
  const { t } = useLanguage();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);

    // Pages that are NEVER allowed as the default landing page.
    // /mars is computation-heavy and forces a cold cache on every server restart.
    // All entries in this list are silently migrated to "/" (Home dashboard).
    const DISALLOWED_DEFAULT_PAGES = new Set(["/mars", "/race", "/ladder"]);

    let defaultPage = localStorage.getItem("marffet_default_page");

    if (defaultPage && DISALLOWED_DEFAULT_PAGES.has(defaultPage)) {
      // Migrate legacy values: clear the preference, fall back to Home
      localStorage.setItem("marffet_default_page", "/");
      defaultPage = "/";
    }

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
            {t('Home.Title')}
          </h1>
          <p className="text-gray-400 mt-1">{t('Home.SelectModule')}</p>
        </div>
        <div className="flex gap-2 text-sm text-gray-500 bg-black/20 px-3 py-1.5 rounded-lg border border-white/5">
          <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
          {t('Home.SystemOnline')}
        </div>
      </div>

      {/* Strategy Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <StrategyCard
          title={t('Home.MarsStrategy')}
          description={t('Home.MarsDesc')}
          icon="🚀"
          href="/mars"
          status="active"
          metrics={[
            { label: t('Home.WinRate'), value: "68%" },
            { label: t('Home.Active'), value: "12" },
          ]}
        />

        <StrategyCard
          title={t('Home.Portfolio')}
          description={t('Home.PortfolioDesc')}
          icon="📊"
          href="/portfolio"
          status="active"
          metrics={[
            { label: t('Home.AssetsLabel'), value: "8" },
            { label: t('Home.ValueLabel'), value: "$42.5k" },
          ]}
        />

        <StrategyCard
          title={t('Home.DataViz')}
          description={t('Home.DataVizDesc')}
          icon="📈"
          href="/viz"
          status="active"
          metrics={[
            { label: t('Home.DataPoints'), value: "1.2M" },
            { label: t('Home.Charts'), value: "4" },
          ]}
        />

        <StrategyCard
          title={t('Home.StockDiscovery')}
          description={t('Home.StockDiscoveryDesc')}
          icon="🔍"
          href="/discovery"
          status="dev"
        />

        <StrategyCard
          title={t('Home.ConvertibleBonds')}
          description={t('Home.CBDesc')}
          icon="💹"
          href="/cb"
          status="dev"
        />
      </div>

      {/* Quick Stats / System Info */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
        <div className="p-4 rounded-xl bg-white/5 border border-white/10">
          <div className="text-gray-400 text-sm mb-1">{t('Home.MarketStatus')}</div>
          <div className="text-xl font-bold text-green-400">{t('Home.Open')}</div>
        </div>
        <div className="p-4 rounded-xl bg-white/5 border border-white/10">
          <div className="text-gray-400 text-sm mb-1">{t('Home.DataFeed')}</div>
          <div className="text-xl font-bold text-blue-400">{t('Home.Live')}</div>
        </div>
        <div className="p-4 rounded-xl bg-white/5 border border-white/10">
          <div className="text-gray-400 text-sm mb-1">{t('Home.NextRebalance')}</div>
          <div className="text-xl font-bold text-white">04:30:00</div>
        </div>
      </div>
    </div>
  );
}
