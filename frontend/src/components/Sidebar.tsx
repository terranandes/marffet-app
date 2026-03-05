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
    const [isOpen, setIsOpen] = useState(false);
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

    // Close sidebar on route change (mobile)
    useEffect(() => {
        setIsOpen(false);
    }, [pathname]);

    return (
        <>
            {/* Mobile Toggle Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="lg:hidden fixed top-4 right-4 z-[60] p-2 rounded-lg bg-zinc-900 border border-zinc-800 text-white shadow-lg"
            >
                {isOpen ? (
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                ) : (
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                    </svg>
                )}
            </button>

            {/* Backdrop for Mobile */}
            {isOpen && (
                <div
                    onClick={() => setIsOpen(false)}
                    className="lg:hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
                />
            )}

            <aside className={`fixed left-0 top-0 h-[100dvh] w-64 bg-[var(--color-bg)]/90 backdrop-blur-xl border-r border-[var(--color-border)] flex flex-col z-50 transition-transform duration-300 ease-in-out lg:translate-x-0 ${isOpen ? "translate-x-0" : "-translate-x-full"
                }`}>
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

                    {isLoading ? (
                        <div className="mb-4 p-4 space-y-3 animate-pulse">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-full bg-white/10" />
                                <div className="flex-1 space-y-2">
                                    <div className="h-3 w-20 bg-white/10 rounded" />
                                    <div className="h-2 w-16 bg-white/10 rounded" />
                                </div>
                            </div>
                        </div>
                    ) : user ? (
                        <div className="mb-4 mx-4 p-4 rounded-xl bg-[var(--color-bg-secondary)]/30 border border-[var(--color-border)]">
                            <div className="flex items-center gap-3 mb-3">
                                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[var(--color-cta)] to-blue-600 flex items-center justify-center text-white font-bold shadow-lg shrink-0">
                                    {user.picture ? (
                                        <img src={user.picture} alt={user.nickname || "User"} className="w-full h-full rounded-full" />
                                    ) : (
                                        (user.nickname?.[0] || user.email?.[0] || "U").toUpperCase()
                                    )}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="text-sm font-bold text-white truncate">
                                        {user.nickname || user.email?.split("@")[0] || "User"}
                                    </div>
                                    <div className="text-xs text-[var(--color-text-muted)] truncate">
                                        {user.email || "Guest"}
                                    </div>
                                </div>
                                {/* Settings Icon in User Card */}
                                <button
                                    onClick={() => {
                                        setSettingsActiveTab("profile");
                                        setShowSettings(true);
                                    }}
                                    className="p-2 text-zinc-400 hover:text-white hover:bg-white/10 rounded-lg transition shrink-0"
                                    title="Settings"
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                    </svg>
                                </button>
                            </div>
                            <button
                                onClick={() => {
                                    // Force hard navigation to ensure cookies are cleared properly by the browser
                                    // Use relative path to utilize Next.js Rewrite and keep user on the current host
                                    window.location.href = `/auth/logout`;
                                }}
                                className="block w-full py-2 text-center text-xs font-bold text-red-400 hover:text-red-300 hover:bg-white/5 rounded-lg transition cursor-pointer"
                            >
                                {t('Sidebar.SignOut')}
                            </button>
                        </div>
                    ) : (
                        <div className="mb-4 mx-4 space-y-2">
                            <a
                                href={`/auth/login`}
                                className="flex items-center justify-center gap-2 w-full py-3 bg-white text-black font-bold rounded-xl hover:bg-[var(--color-cta)] transition-all shadow-lg shadow-white/10 hover:shadow-[var(--color-cta)]/20"
                            >
                                <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M12.545,10.239v3.821h5.445c-0.712,2.315-2.647,3.972-5.445,3.972c-3.332,0-6.033-2.701-6.033-6.032s2.701-6.032,6.033-6.032c1.498,0,2.866,0.549,3.921,1.453l2.814-2.814C17.503,2.988,15.139,2,12.545,2C7.021,2,2.543,6.477,2.543,12s4.478,10,10.002,10c8.396,0,10.249-7.85,9.426-11.748L12.545,10.239z" />
                                </svg>
                                {t('Sidebar.SignInGoogle')}
                            </a>
                            <button
                                onClick={async () => {
                                    // Use relative path to leverage Next.js rewrites
                                    // Helper function to attempt guest login
                                    const attemptGuestLogin = async () => {
                                        const res = await fetch(`/auth/guest`, {
                                            method: "POST",
                                            credentials: "include"
                                        });
                                        return res;
                                    };

                                    try {
                                        // First attempt
                                        let res = await attemptGuestLogin();

                                        // If first attempt fails (common with cross-origin cookies), retry once
                                        if (!res.ok) {
                                            console.log("Guest login first attempt failed, retrying...");
                                            await new Promise(resolve => setTimeout(resolve, 100)); // Small delay
                                            res = await attemptGuestLogin();
                                        }

                                        if (res.ok) {
                                            refreshUser(); // Refresh user state
                                        } else {
                                            alert("Failed to enter guest mode");
                                        }
                                    } catch (e) {
                                        console.error("Guest mode error:", e);
                                        alert("Network error");
                                    }
                                }}
                                className="flex items-center justify-center gap-2 w-full py-3 bg-white/5 text-zinc-300 font-semibold rounded-xl hover:bg-white/10 transition-all border border-white/10"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                </svg>
                                {t('Sidebar.ExploreGuest')}
                            </button>
                            <p className="text-xs text-zinc-500 text-center">Data stored locally only</p>
                            <div className="flex justify-center mt-2">
                                <button
                                    onClick={() => {
                                        setSettingsActiveTab("profile");
                                        setShowSettings(true);
                                    }}
                                    className="p-2 bg-white/5 hover:bg-white/10 text-zinc-400 hover:text-white rounded-lg transition border border-white/5"
                                    title="Settings"
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                    </svg>
                                </button>
                            </div>
                        </div>
                    )}
                </div>

                <div className="p-4 border-t border-zinc-800/50">
                    <DataTimestamp />
                    <div className="text-[10px] text-zinc-600 text-center mt-2">
                        v0.2.1 • Marffet System
                    </div>
                </div>
            </aside >

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
