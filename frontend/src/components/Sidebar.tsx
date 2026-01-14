"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect } from "react";

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
    const [isOpen, setIsOpen] = useState(false);
    const [user, setUser] = useState<User | null>(null);
    const pathname = usePathname();

    // Notifications State
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [showNotifications, setShowNotifications] = useState(false);
    const unreadCount = notifications.filter(n => !n.is_read).length;

    // Fetch user info & notifications on mount
    useEffect(() => {
        const fetchData = async () => {
            try {
                // Use Absolute URL for Cross-Domain Auth check
                const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

                const userRes = await fetch(`${API_URL}/auth/me`, {
                    credentials: "include"
                });

                if (userRes.ok) {
                    const userData = await userRes.json();
                    setUser(userData);

                    // Fetch notifications if logged in
                    const notifRes = await fetch(`${API_URL}/api/notifications`, {
                        credentials: "include"
                    });
                    if (notifRes.ok) {
                        setNotifications(await notifRes.json());
                    }
                } else {
                    setUser(null);
                }
            } catch (e) {
                console.error("Fetch error:", e);
                setUser(null);
            }
        };
        fetchData();

        // Poll notifications every 30s
        const interval = setInterval(async () => {
            try {
                const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
                const res = await fetch(`${API_URL}/api/notifications`, { credentials: "include" });
                if (res.ok) setNotifications(await res.json());
            } catch (e) { console.error("Poll error:", e); }
        }, 30000);

        return () => clearInterval(interval);
    }, []);

    const markAsRead = async (id: number) => {
        try {
            const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
            await fetch(`${API_URL}/api/notifications/${id}/read`, { method: "POST", credentials: "include" });
            setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: 1 } : n));
        } catch (e) { console.error("Mark read error:", e); }
    };

    const clearNotifications = () => {
        notifications.forEach(n => {
            if (!n.is_read) markAsRead(n.id);
        });
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
                className="md:hidden fixed top-4 right-4 z-[60] p-2 rounded-lg bg-zinc-900 border border-zinc-800 text-white shadow-lg"
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
                    className="md:hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
                />
            )}

            <aside className={`fixed left-0 top-0 h-screen w-64 bg-[var(--color-bg)]/90 backdrop-blur-xl border-r border-[var(--color-border)] flex flex-col z-50 transition-transform duration-300 ease-in-out md:translate-x-0 ${isOpen ? "translate-x-0" : "-translate-x-full"
                }`}>
                <div className="p-6">

                    <div className="flex items-center justify-between mb-8 px-2">
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-[var(--color-cta)] to-blue-500 shadow-lg shadow-cyan-500/20 flex items-center justify-center text-black font-bold text-lg">
                                M
                            </div>
                            <span className="bg-gradient-to-r from-white to-[var(--color-cta)] bg-clip-text text-transparent font-bold text-lg tracking-tight">
                                MARTIAN
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
                                            <button onClick={clearNotifications} className="text-xs text-blue-400 hover:text-blue-300">
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

                    <nav className="flex flex-col gap-2">
                        {/* Mars Strategy */}
                        <SidebarItem
                            href="/mars"
                            label="Mars Strategy"
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
                            label="Bar Chart Race"
                            icon={
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M3 3v18h18" />
                                    <rect x="7" y="10" width="3" height="8" rx="1" />
                                    <rect x="14" y="6" width="3" height="12" rx="1" />
                                </svg>
                            }
                        />
                        {/* CB Strategy */}
                        <SidebarItem
                            href="/cb"
                            label="CB Strategy"
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
                            label="Portfolio"
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
                            label="Trend"
                            icon={
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M3 3v18h18" />
                                    <path d="m19 9-5 5-4-4-3 3" />
                                </svg>
                            }
                        />
                        {/* Cash Ladder */}
                        <SidebarItem
                            href="/ladder"
                            label="Cash Ladder"
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
                        {/* My Race */}
                        <SidebarItem
                            href="/myrace"
                            label="My Race"
                            icon={
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <circle cx="12" cy="12" r="10" />
                                    <path d="M12 6v6l4 2" />
                                </svg>
                            }
                        />

                        {/* Separator */}
                        <div className="my-2 border-t border-[var(--color-border)]" />

                        {/* Admin-Only Link */}
                        {user?.is_admin && (
                            <SidebarItem
                                href="/admin"
                                label="GM Dashboard"
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

                {user ? (
                    <div className="mt-auto mb-4 p-4 rounded-xl bg-[var(--color-bg-secondary)]/30 border border-[var(--color-border)]">
                        <div className="flex items-center gap-3 mb-3">
                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[var(--color-cta)] to-blue-600 flex items-center justify-center text-white font-bold shadow-lg">
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
                        </div>
                        <a
                            href={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/auth/logout`}
                            className="block w-full py-2 text-center text-xs font-bold text-red-400 hover:text-red-300 hover:bg-white/5 rounded-lg transition"
                        >
                            Sign Out
                        </a>
                        <button
                            onClick={() => alert("Settings coming soon! Use the Profile API for now.")}
                            className="mt-2 block w-full py-2 text-center text-xs font-bold text-[var(--color-text-muted)] hover:text-white hover:bg-white/5 rounded-lg transition"
                        >
                            ⚙️ Settings
                        </button>
                    </div>
                ) : (
                    <div className="mt-auto mb-4 p-4">
                        <a
                            href={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/auth/login`}
                            className="flex items-center justify-center gap-2 w-full py-3 bg-white text-black font-bold rounded-xl hover:bg-[var(--color-cta)] transition-all shadow-lg shadow-white/10 hover:shadow-[var(--color-cta)]/20"
                        >
                            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12.545,10.239v3.821h5.445c-0.712,2.315-2.647,3.972-5.445,3.972c-3.332,0-6.033-2.701-6.033-6.032s2.701-6.032,6.033-6.032c1.498,0,2.866,0.549,3.921,1.453l2.814-2.814C17.503,2.988,15.139,2,12.545,2C7.021,2,2.543,6.477,2.543,12s4.478,10,10.002,10c8.396,0,10.249-7.85,9.426-11.748L12.545,10.239z" />
                            </svg>
                            Login
                        </a>
                    </div>
                )}

                <div className="p-2 text-xs text-zinc-600 text-center">
                    v0.2.0 • Martian System
                </div>
            </aside>
        </>
    );
}
