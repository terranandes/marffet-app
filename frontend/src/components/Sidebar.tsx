"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect } from "react";

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
            className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group ${active
                ? "bg-purple-600/20 text-purple-400 border border-purple-500/30 shadow-[0_0_15px_rgba(168,85,247,0.15)]"
                : "text-zinc-500 hover:text-zinc-200 hover:bg-zinc-900/50"
                }`}
        >
            <div className={`w-5 h-5 ${active ? "text-purple-400" : "text-zinc-600 group-hover:text-zinc-400"}`}>
                {icon}
            </div>
            <span className="font-medium text-sm tracking-wide">{label}</span>
            {active && (
                <div className="ml-auto w-1.5 h-1.5 rounded-full bg-purple-400 shadow-[0_0_10px_rgba(168,85,247,0.8)]" />
            )}
        </Link>
    );
};

export default function Sidebar() {
    const [isOpen, setIsOpen] = useState(false);
    const pathname = usePathname();

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

            <aside className={`fixed left-0 top-0 h-screen w-64 bg-zinc-950/80 backdrop-blur-xl border-r border-zinc-900 flex flex-col z-50 transition-transform duration-300 ease-in-out md:translate-x-0 ${isOpen ? "translate-x-0" : "-translate-x-full"
                }`}>
                <div className="p-6">
                    <div className="flex items-center gap-3 mb-8 px-2">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-purple-500 to-pink-600 shadow-lg shadow-purple-900/20 flex items-center justify-center text-white font-bold text-lg">
                            M
                        </div>
                        <span className="bg-gradient-to-r from-white to-zinc-400 bg-clip-text text-transparent font-bold text-lg tracking-tight">
                            MARTIAN
                        </span>
                    </div>

                    <nav className="flex flex-col gap-2">
                        <SidebarItem
                            href="/"
                            label="Overview"
                            icon={
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    strokeWidth="2"
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                >
                                    <rect width="7" height="9" x="3" y="3" rx="1" />
                                    <rect width="7" height="5" x="14" y="3" rx="1" />
                                    <rect width="7" height="9" x="14" y="12" rx="1" />
                                    <rect width="7" height="5" x="3" y="16" rx="1" />
                                </svg>
                            }
                        />
                        <SidebarItem
                            href="/mars"
                            label="Mars Strategy"
                            icon={
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    strokeWidth="2"
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                >
                                    <path d="M12 2a10 10 0 1 0 10 10 4 4 0 0 1-5-5 4 4 0 0 1-5-5" />
                                    <path d="M8.5 8.5C7 9.5 6 12 7 14s4 3 6 3 3-4 6-4" />
                                    <path d="M9 10a1 1 0 1 1 0-2 1 1 0 0 1 0 2" />
                                </svg>
                            }
                        />
                        <SidebarItem
                            href="/viz"
                            label="Visualization"
                            icon={
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    strokeWidth="2"
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                >
                                    <path d="M3 3v18h18" />
                                    <path d="m19 9-5 5-4-4-3 3" />
                                </svg>
                            }
                        />
                        <SidebarItem
                            href="/cb"
                            label="CB Strategy"
                            icon={
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    strokeWidth="2"
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                >
                                    <path d="M12 2v20" />
                                    <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
                                </svg>
                            }
                        />
                    </nav>
                </div>

                <div className="mt-auto p-6 text-xs text-zinc-600 text-center">
                    v0.2.0 • Martian System
                </div>
            </aside>
        </>
    );
}
