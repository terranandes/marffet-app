"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { useLanguage } from "../lib/i18n/LanguageContext";

const tabs = [
    { key: "mars", href: "/mars", label: "Mars", icon: "🪐" },
    { key: "portfolio", href: "/portfolio", label: "Portfolio", icon: "💼" },
    { key: "race", href: "/race", label: "Race", icon: "🏎️" },
    { key: "trend", href: "/trend", label: "Trend", icon: "📈" },
    { key: "more", href: "#more", label: "More", icon: "⋯" },
];

const moreItems = [
    { href: "/compound", label: "Compound Interest", icon: "📊" },
    { href: "/cb", label: "Convertible Bond", icon: "💵" },
    { href: "/ladder", label: "Cash Ladder", icon: "🪜" },
    { href: "/myrace", label: "My Race", icon: "⏱️" },
    { href: "/admin", label: "Admin", icon: "⚙️", adminOnly: true },
];

export default function BottomTabBar() {
    const pathname = usePathname();
    const { t } = useLanguage();
    const [showMore, setShowMore] = useState(false);

    // Check if any "more" page is active
    const moreActive = moreItems.some(item => pathname === item.href);

    return (
        <>
            {/* More Popup Overlay */}
            {showMore && (
                <div className="fixed inset-0 z-[70]" onClick={() => setShowMore(false)}>
                    <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />
                    <div
                        className="absolute bottom-20 left-4 right-4 bg-[#0e1117]/95 backdrop-blur-xl border border-zinc-800 rounded-2xl shadow-2xl overflow-hidden"
                        onClick={e => e.stopPropagation()}
                    >
                        <div className="p-3 border-b border-zinc-800">
                            <h3 className="text-sm font-semibold text-white/70 px-1">More Features</h3>
                        </div>
                        <div className="p-2 grid grid-cols-3 gap-1">
                            {moreItems
                                .filter(item => !item.adminOnly)
                                .map(item => (
                                    <Link
                                        key={item.href}
                                        href={item.href}
                                        onClick={() => setShowMore(false)}
                                        className={`flex flex-col items-center gap-1.5 p-3 rounded-xl transition-colors ${pathname === item.href
                                                ? "bg-[var(--color-cta)]/10 text-[var(--color-cta)]"
                                                : "text-zinc-400 hover:bg-white/5 hover:text-white"
                                            }`}
                                    >
                                        <span className="text-2xl">{item.icon}</span>
                                        <span className="text-xs font-medium text-center leading-tight">
                                            {item.label}
                                        </span>
                                    </Link>
                                ))}
                        </div>
                    </div>
                </div>
            )}

            {/* Bottom Tab Bar */}
            <nav className="lg:hidden fixed bottom-0 left-0 right-0 z-[60] bg-[#050510]/95 backdrop-blur-xl border-t border-zinc-800/80"
                style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
            >
                <div className="flex items-center justify-around h-16 px-1">
                    {tabs.map(tab => {
                        const isMore = tab.key === "more";
                        const isActive = isMore
                            ? moreActive || showMore
                            : pathname === tab.href || pathname.startsWith(tab.href + "/");

                        if (isMore) {
                            return (
                                <button
                                    key={tab.key}
                                    onClick={() => setShowMore(!showMore)}
                                    className={`flex flex-col items-center justify-center gap-0.5 flex-1 h-full transition-colors ${isActive
                                            ? "text-[var(--color-cta)]"
                                            : "text-zinc-500"
                                        }`}
                                >
                                    <span className="text-xl leading-none">{tab.icon}</span>
                                    <span className="text-[10px] font-medium">{tab.label}</span>
                                </button>
                            );
                        }

                        return (
                            <Link
                                key={tab.key}
                                href={tab.href}
                                onClick={() => setShowMore(false)}
                                className={`flex flex-col items-center justify-center gap-0.5 flex-1 h-full transition-colors ${isActive
                                        ? "text-[var(--color-cta)]"
                                        : "text-zinc-500 hover:text-zinc-300"
                                    }`}
                            >
                                <span className="text-xl leading-none">{tab.icon}</span>
                                <span className="text-[10px] font-medium">{tab.label}</span>
                                {isActive && (
                                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-8 h-0.5 bg-[var(--color-cta)] rounded-full" />
                                )}
                            </Link>
                        );
                    })}
                </div>
            </nav>
        </>
    );
}
