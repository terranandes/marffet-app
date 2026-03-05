"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useRef, useEffect } from "react";
import { useLanguage } from "../lib/i18n/LanguageContext";
import { useUser } from "../lib/UserContext";

export default function BottomTabBar() {
    const pathname = usePathname();
    const { t } = useLanguage();
    const { user } = useUser();
    const scrollRef = useRef<HTMLElement>(null);

    const tabs = [
        { key: "mars", href: "/mars", label: t('Sidebar.MarsStrategy') || "Mars", icon: "🪐" },
        { key: "race", href: "/race", label: t('Sidebar.BarChartRace') || "Race", icon: "🏎️" },
        { key: "compound", href: "/compound", label: t('Sidebar.CompoundInterest') || "Compound", icon: "📈" },
        { key: "portfolio", href: "/portfolio", label: t('Sidebar.Portfolio') || "Portfolio", icon: "💼" },
        { key: "cb", href: "/cb", label: t('Sidebar.ConvertibleBond') || "CB", icon: "💵" },
        { key: "trend", href: "/trend", label: t('Sidebar.TrendDashboard') || "Trend", icon: "📊" },
        { key: "myrace", href: "/myrace", label: t('Sidebar.MyPortfolioRace') || "My Race", icon: "⏱️" },
        { key: "ladder", href: "/ladder", label: t('Sidebar.CashLadder') || "Ladder", icon: "🪜" },
    ];

    if (user?.is_admin) {
        tabs.push({ key: "admin", href: "/admin", label: t('Sidebar.AdminDashboard') || "Admin", icon: "⚙️" });
    }

    // Auto-scroll to active tab on mount or route change
    useEffect(() => {
        if (!scrollRef.current) return;

        const activeItem = scrollRef.current.querySelector('[data-active="true"]');
        if (activeItem) {
            activeItem.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
        }
    }, [pathname]);

    // Global toggle for SettingsModal (to be caught by layout or another component)
    // For now we'll dispatch a custom event that SettingsModal can listen to, or we can just navigate to a hash
    const openSettings = () => {
        window.dispatchEvent(new CustomEvent('open-mobile-settings'));
    };

    return (
        <div className="lg:hidden fixed bottom-0 left-0 right-0 z-[60] bg-[#050510]/95 backdrop-blur-xl border-t border-zinc-800/80 flex h-16"
            style={{ paddingBottom: "env(safe-area-inset-bottom)", height: "calc(64px + env(safe-area-inset-bottom))" }}
        >
            {/* Zone 3: Scrollable Tabs */}
            <nav
                ref={scrollRef}
                className="flex-1 flex overflow-x-auto snap-x snap-mandatory"
                style={{
                    scrollbarWidth: 'none',
                    msOverflowStyle: 'none',
                    WebkitOverflowScrolling: 'touch'
                }}
            >
                {/* CSS to hide webkit scrollbar */}
                <style dangerouslySetInnerHTML={{
                    __html: `
                    nav::-webkit-scrollbar { display: none; }
                `}} />

                {tabs.map(tab => {
                    const isActive = pathname === tab.href || pathname.startsWith(tab.href + "/");

                    return (
                        <Link
                            key={tab.key}
                            href={tab.href}
                            data-active={isActive}
                            className={`flex flex-col items-center justify-center gap-1 min-w-[72px] h-16 shrink-0 snap-center transition-colors relative ${isActive
                                ? "text-[var(--color-cta)]"
                                : "text-zinc-500 hover:text-zinc-300"
                                }`}
                        >
                            <span className="text-2xl leading-none block mt-1">{tab.icon}</span>
                            <span className="text-[10px] font-bold tracking-tight px-1 text-center w-full truncate">{tab.label}</span>

                            {/* Active indicator line */}
                            {isActive && (
                                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-8 h-0.5 bg-[var(--color-cta)] rounded-full shadow-[0_0_8px_rgba(139,92,246,0.6)]" />
                            )}
                        </Link>
                    );
                })}

                {/* Padding at the end to allow the last item to be centered if needed */}
                <div className="w-4 shrink-0" />
            </nav>

            {/* Zone 4: Fixed Settings Button */}
            <div className="w-[72px] shrink-0 border-l border-zinc-800 bg-zinc-900/40">
                <button
                    onClick={openSettings}
                    className="w-full h-16 flex flex-col items-center justify-center gap-1 text-zinc-400 hover:text-white transition-colors"
                >
                    <span className="text-2xl leading-none block mt-1">⚙️</span>
                    <span className="text-[10px] font-bold tracking-tight">
                        {user ? (t('Settings.Title') || "Settings") : (t('Sidebar.SignInGoogle') || "Sign In")}
                    </span>
                </button>
            </div>
        </div>
    );
}

