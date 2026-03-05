"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect } from "react";
import SettingsModal from "./SettingsModal";
import DataTimestamp from "./DataTimestamp";
import { useLanguage } from "../lib/i18n/LanguageContext";
import { useUser } from "../lib/UserContext";

interface User {
    id: string | null;
    email?: string;
    is_admin?: boolean;
    tier?: string;
    nickname?: string;
    picture?: string;
}

interface Notification {
    id: number;
    title: string;
    message: string;
    type: string;
    is_read: number;
    created_at: string;
}

const SidebarItem = ({
    href,
    label,
    icon,
}: {
    href: string;
    label: string;
    icon: React.ReactNode;
}) => {
    const pathname = usePathname();
    const active = pathname === href;

    return (
        <Link
            href={href}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 cursor-pointer group ${active
                ? "bg-[var(--color-cta)]/20 text-[var(--color-cta)] border border-[var(--color-cta)]/30 shadow-[0_0_15px_rgba(139,92,246,0.15)]"
                : "text-[var(--color-text-muted)] hover:text-[var(--color-text)] hover:bg-[var(--color-bg-secondary)]/50"
                }`}
        >
            <div className={`w-5 h-5 ${active ? "text-[var(--color-cta)]" : "text-[var(--color-text-muted)] group-hover:text-[var(--color-text)]"}`}>
                {icon}
            </div>
            <span className="font-medium text-sm tracking-wide">{label}</span>
            {active && (
                <div className="ml-auto w-1.5 h-1.5 rounded-full bg-[var(--color-cta)] shadow-[0_0_10px_rgba(139,92,246,0.8)]" />
            )}
        </Link>
    );
};

export default function Sidebar() {
    const { t } = useLanguage();
    const { user, isLoading, notifications, unreadCount, markAsRead, clearNotifications, refreshUser } = useUser();
    const pathname = usePathname();

    // Notifications UI State (local)
    const [showNotifications, setShowNotifications] = useState(false);

    // State for Settings Modal
    const [showSettings, setShowSettings] = useState(false);
    const [settingsActiveTab, setSettingsActiveTab] = useState("profile");

    const handleClearNotifications = () => {
        clearNotifications();
        setShowNotifications(false);
    };

    return (
        <>
            <aside className="hidden lg:flex fixed left-0 top-0 h-[100dvh] w-64 bg-[var(--color-bg)]/90 backdrop-blur-xl border-r border-[var(--color-border)] flex-col z-50">
                <div className="p-6 shrink-0">

                    <div className="flex items-center justify-between mb-8 px-2">
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-[var(--color-cta)] to-blue-500 shadow-lg shadow-cyan-500/20 flex items-center justify-center text-black font-bold text-lg">
                                M
                            </div>
                            <span className="bg-gradient-to-r from-white to-[var(--color-cta)] bg-clip-text text-transparent font-bold text-lg tracking-tight">
                                MARFFET
                            </span>
                        </div>

                        {/* Notification Bell */}
                        {user && (
                            <div className="relative">
                                <button
                                    onClick={() => setShowNotifications(!showNotifications)}
                                    className="relative p-2 text-zinc-400 hover:text-white transition rounded-full hover:bg-white/10"
                                >
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                                    </svg>
                                    {unreadCount > 0 && (
                                        <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(239,68,68,0.6)]" />
                                    )}
                                </button>

                                {/* Notification Dropdown */}
                                {showNotifications && (
                                    <div className="absolute left-full top-0 ml-2 w-80 bg-[#0e1117] border border-zinc-800 rounded-xl shadow-2xl z-[100] overflow-hidden">
                                        <div className="p-3 border-b border-zinc-800 flex justify-between items-center bg-zinc-900/50">
                                            <h3 className="font-bold text-sm text-white">Notifications</h3>
                                            <button onClick={handleClearNotifications} className="text-xs text-blue-400 hover:text-blue-300">
                                                Mark all read
                                            </button>
                                        </div>
                                        <div className="max-h-64 overflow-y-auto">
                                            {notifications.length === 0 ? (
                                                <div className="p-4 text-center text-zinc-500 text-sm">No notifications</div>
                                            ) : (
                                                notifications.map(n => (
                                                    <div
                                                        key={n.id}
                                                        onClick={() => markAsRead(n.id)}
                                                        className={`p-3 border-b border-zinc-800/50 text-sm hover:bg-white/5 cursor-pointer transition ${!n.is_read ? 'bg-blue-500/10' : ''}`}
                                                    >
                                                        <div className="flex justify-between mb-1">
                                                            <span className={`font-bold text-xs ${n.type === 'alert' ? 'text-red-400' : 'text-blue-400'}`}>
                                                                {n.title}
                                                            </span>
                                                            <span className="text-[10px] text-zinc-500">
                                                                {new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                                            </span>
                                                        </div>
                                                        <p className={`text-zinc-300 ${!n.is_read ? 'font-medium text-white' : ''}`}>
                                                            {n.message}
                                                        </p>
                                                    </div>
                                                ))
                                            )}
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>

                {/* Scrollable Nav Area */}
                <div className="flex-1 overflow-y-auto min-h-0 px-6">
                    <nav className="flex flex-col gap-2">
                        {/* Mars Strategy */}
                        <SidebarItem
                            href="/mars"
                            label={t('Sidebar.MarsStrategy')}
                            icon={
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M12 2a10 10 0 1 0 10 10 4 4 0 0 1-5-5 4 4 0 0 1-5-5" />
                                    <path d="M8.5 8.5C7 9.5 6 12 7 14s4 3 6 3 3-4 6-4" />
                                </svg>
                            }
                        />
                        {/* Bar Chart Race */}
                        <SidebarItem
                            href="/race"
                            label={t('Sidebar.BarChartRace')}
                            icon={
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M3 3v18h18" />
                                    <rect x="7" y="10" width="3" height="8" rx="1" />
                                    <rect x="14" y="6" width="3" height="12" rx="1" />
                                </svg>
                            }
                        />
                        {/* Compound Interest */}
                        <SidebarItem
                            href="/compound"
                            label={t('Sidebar.CompoundInterest')}
                            icon={
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M12 2v20" />
                                    <path d="M18 10h-4V7a4 4 0 0 0-8 0v3" />
                                    <path d="M14 22v-4a2 2 0 0 0-2-2h-4" />
                                </svg>
                            }
                        />
                        {/* CB Strategy */}
                        <SidebarItem
                            href="/cb"
                            label={t('Sidebar.ConvertibleBond')}
                            icon={
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M12 2v20" />
                                    <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
                                </svg>
                            }
                        />
                        {/* Portfolio */}
                        <SidebarItem
                            href="/portfolio"
                            label={t('Sidebar.Portfolio')}
                            icon={
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <rect x="2" y="7" width="20" height="14" rx="2" ry="2" />
                                    <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
                                </svg>
                            }
                        />
                        {/* Trend */}
                        <SidebarItem
                            href="/trend"
                            label={t('Sidebar.TrendDashboard')}
                            icon={
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M3 3v18h18" />
                                    <path d="m19 9-5 5-4-4-3 3" />
                                </svg>
                            }
                        />
                        {/* My Race */}
                        <SidebarItem
                            href="/myrace"
                            label={t('Sidebar.MyPortfolioRace')}
                            icon={
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <circle cx="12" cy="12" r="10" />
                                    <path d="M12 6v6l4 2" />
                                </svg>
                            }
                        />
                        {/* Cash Ladder */}
                        <SidebarItem
                            href="/ladder"
                            label={t('Sidebar.CashLadder')}
                            icon={
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M6 3v18" />
                                    <path d="M18 3v18" />
                                    <path d="M6 8h12" />
                                    <path d="M6 12h12" />
                                    <path d="M6 16h12" />
                                </svg>
                            }
                        />

                        {/* Separator */}
                        <div className="my-2 border-t border-[var(--color-border)]" />

                        {/* Admin-Only Link */}
                        {user?.is_admin && (
                            <SidebarItem
                                href="/admin"
                                label={t('Sidebar.AdminDashboard')}
                                icon={
                                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                        <path d="M12 2L2 7l10 5 10-5-10-5z" />
                                        <path d="M2 17l10 5 10-5" />
                                        <path d="M2 12l10 5 10-5" />
                                    </svg>
                                }
                            />
                        )}
                    </nav>
                </div>



                <div className="mt-auto flex flex-col w-full shrink-0">
                    {/* Sponsor Us Link */}
                    <div className="px-4 mb-4">
                        <button
                            onClick={() => {
                                setSettingsActiveTab("sponsor");
                                setShowSettings(true);
                            }}
                            className="w-full py-2.5 bg-gradient-to-r from-pink-500/10 via-purple-500/10 to-orange-500/10 border border-pink-500/20 rounded-xl text-pink-300 hover:text-white hover:border-pink-500/50 transition-all text-xs font-bold flex items-center justify-center gap-2 shadow-[0_0_10px_rgba(236,72,153,0.05)] hover:shadow-[0_0_15px_rgba(236,72,153,0.2)]"
                        >
                            <svg className="w-4 h-4 text-pink-500" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
                            </svg>
                            {t('Sidebar.SponsorUs')}
                        </button>
                    </div>

                    <div className="p-4 border-t border-zinc-800/50">
                        <DataTimestamp />
                        <div className="text-[10px] text-zinc-600 text-center mt-2">
                            v0.2.1 • Marffet System
                        </div>
                    </div>
                </div>
            </aside>

            <SettingsModal
                isOpen={showSettings}
                onClose={() => setShowSettings(false)}
                user={user}
                onUpdateUser={refreshUser}
                initialTab={settingsActiveTab}
            />
        </>
    );
}
