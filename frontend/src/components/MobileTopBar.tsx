"use client";

import { useState } from "react";
import { usePathname } from "next/navigation";
import { useUser } from "../lib/UserContext";
import { useLanguage } from "../lib/i18n/LanguageContext";

export default function MobileTopBar() {
    const { t } = useLanguage();
    const { user, notifications, unreadCount, markAsRead, clearNotifications } = useUser();
    const [showNotifications, setShowNotifications] = useState(false);
    const [showTierInfo, setShowTierInfo] = useState(false);
    const pathname = usePathname();

    const handleClearNotifications = () => {
        clearNotifications();
        setShowNotifications(false);
    };

    // Determine tier display properties
    const tierConfig = {
        'FREE': { color: 'text-zinc-500', bg: 'bg-zinc-500/10', border: 'border-zinc-500/20', icon: '👤', label: 'FREE' },
        'PREMIUM': { color: 'text-yellow-400', bg: 'bg-yellow-500/10', border: 'border-yellow-500/30', icon: '⭐', label: 'PREM' },
        'VIP': { color: 'text-purple-400', bg: 'bg-purple-500/10', border: 'border-purple-500/30', icon: '💎', label: 'VIP' },
        'GM': { color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/30', icon: '👑', label: 'GM' }
    };

    const currentTier = user?.tier as keyof typeof tierConfig || 'FREE';
    const tier = tierConfig[currentTier];

    // Determine page title based on pathname
    let pageTitle = "MARFFET";
    if (pathname === '/mars') pageTitle = "Mars Strategy";
    else if (pathname === '/race') pageTitle = "Race Chart";
    else if (pathname === '/compound') pageTitle = "Compound";
    else if (pathname === '/cb') pageTitle = "Convertible Bond";
    else if (pathname === '/portfolio') pageTitle = "Portfolio";
    else if (pathname === '/trend') pageTitle = "Trend Dashboard";
    else if (pathname === '/myrace') pageTitle = "My Race";
    else if (pathname === '/ladder') pageTitle = "Cash Ladder";
    else if (pathname === '/admin') pageTitle = "Admin Dashboard";

    return (
        <div className="lg:hidden fixed top-0 left-0 right-0 z-[60] h-14 bg-[#050510]/95 backdrop-blur-xl border-b border-zinc-800/80 flex items-center justify-between px-4 pt-[env(safe-area-inset-top)]">

            {/* Left: Notification Bell */}
            <div className="flex-1">
                {user ? (
                    <div className="relative inline-block">
                        <button
                            onClick={() => setShowNotifications(!showNotifications)}
                            className="relative p-2 -ml-2 text-zinc-400 hover:text-white transition rounded-full hover:bg-white/10"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                            </svg>
                            {unreadCount > 0 && (
                                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(239,68,68,0.6)]" />
                            )}
                        </button>

                        {/* Notification Dropdown (Mobile Optimized) */}
                        {showNotifications && (
                            <>
                                <div className="fixed inset-0 z-[90]" onClick={() => setShowNotifications(false)} />
                                <div className="absolute left-0 top-full mt-2 w-[calc(100vw-32px)] max-w-sm bg-[#0e1117] border border-zinc-800 rounded-xl shadow-2xl z-[100] overflow-hidden">
                                    <div className="p-3 border-b border-zinc-800 flex justify-between items-center bg-zinc-900/50">
                                        <h3 className="font-bold text-sm text-white">Notifications</h3>
                                        <button onClick={handleClearNotifications} className="text-xs text-blue-400 hover:text-blue-300">
                                            Mark all read
                                        </button>
                                    </div>
                                    <div className="max-h-80 overflow-y-auto">
                                        {notifications.length === 0 ? (
                                            <div className="p-4 text-center text-zinc-500 text-sm">No notifications</div>
                                        ) : (
                                            notifications.map(n => (
                                                <div
                                                    key={n.id}
                                                    onClick={() => {
                                                        markAsRead(n.id);
                                                        setShowNotifications(false);
                                                    }}
                                                    className={`p-3 border-b border-zinc-800/50 text-sm active:bg-white/10 transition ${!n.is_read ? 'bg-blue-500/10' : ''}`}
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
                            </>
                        )}
                    </div>
                ) : (
                    <div className="w-9"></div>
                )}
            </div>

            {/* Center: Title */}
            <div className="flex-1 text-center truncate px-2">
                <span className="font-bold text-sm text-white tracking-wide">
                    {pageTitle}
                </span>
            </div>

            {/* Right: Tier Badge */}
            <div className="flex-1 flex justify-end">
                {user ? (
                    <div className="relative inline-block">
                        <button
                            onClick={() => setShowTierInfo(!showTierInfo)}
                            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold border ${tier.bg} ${tier.border} ${tier.color} transition-opacity active:opacity-50`}
                        >
                            <span>{tier.icon}</span>
                            <span>{tier.label}</span>
                        </button>

                        {/* Tier Info Popover */}
                        {showTierInfo && (
                            <>
                                <div className="fixed inset-0 z-[90]" onClick={() => setShowTierInfo(false)} />
                                <div className="absolute right-0 top-full mt-2 w-64 bg-[#0e1117] border border-zinc-800 rounded-xl shadow-2xl z-[100] overflow-hidden">
                                    <div className={`p-3 border-b border-zinc-800 flex items-center justify-center gap-2 ${tier.bg} ${tier.border}`}>
                                        <span className={tier.color}>{tier.icon}</span>
                                        <span className={`font-bold text-sm ${tier.color}`}>{tier.label} Tier</span>
                                    </div>
                                    <div className="p-3 text-xs space-y-2">
                                        <div className="flex justify-between text-zinc-400">
                                            <span>Portfolio Groups</span>
                                            <span className="text-white">{currentTier !== 'FREE' ? '30' : '11'}</span>
                                        </div>
                                        <div className="flex justify-between text-zinc-400">
                                            <span>Targets per Group</span>
                                            <span className="text-white">{currentTier !== 'FREE' ? '200' : '50'}</span>
                                        </div>
                                        <div className="flex justify-between text-zinc-400">
                                            <span>Transactions</span>
                                            <span className="text-white">{currentTier !== 'FREE' ? '1000' : '100'}</span>
                                        </div>
                                        <div className="flex justify-between text-zinc-400">
                                            <span>AI Personality</span>
                                            <span className={currentTier !== 'FREE' ? 'text-cyan-400' : 'text-zinc-500'}>
                                                {currentTier !== 'FREE' ? 'Ruthless Mode' : 'Standard'}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </>
                        )}
                    </div>
                ) : (
                    <div className="w-12"></div>
                )}
            </div>

        </div>
    );
}

