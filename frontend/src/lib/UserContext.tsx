"use client";

import { createContext, useContext, useState, useEffect, useCallback, useRef, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { useSWRConfig } from "swr";

interface User {
    id: string | null;
    email?: string;
    is_admin?: boolean;
    is_premium?: boolean;
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

interface UserContextType {
    user: User | null;
    isLoading: boolean;
    notifications: Notification[];
    unreadCount: number;
    refreshUser: () => Promise<void>;
    login: () => void;
    logout: () => Promise<void>;
    markAsRead: (id: number) => Promise<void>;
    clearNotifications: () => void;
}

const UserContext = createContext<UserContextType | null>(null);

export function useUser() {
    const ctx = useContext(UserContext);
    if (!ctx) throw new Error("useUser must be used within UserProvider");
    return ctx;
}

export function UserProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const router = useRouter();
    const { mutate: globalMutate } = useSWRConfig();

    // Ref to track the notification polling interval so we can kill it on logout
    const pollingIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
    // Ref to track in-flight AbortControllers so we can abort them all on logout
    const activeControllersRef = useRef<Set<AbortController>>(new Set());

    const unreadCount = notifications.filter(n => !n.is_read).length;

    // Register an AbortController so it can be terminated on logout
    const registerController = useCallback((controller: AbortController) => {
        activeControllersRef.current.add(controller);
        return () => { activeControllersRef.current.delete(controller); };
    }, []);

    const login = () => {
        window.location.href = "/auth/login";
    };

    const logout = useCallback(async () => {
        try {
            // 1. STOP all notification polling immediately
            if (pollingIntervalRef.current) {
                clearInterval(pollingIntervalRef.current);
                pollingIntervalRef.current = null;
            }

            // 2. ABORT all in-flight fetch requests (safe: AbortError is silently caught)
            activeControllersRef.current.forEach(controller => {
                try { controller.abort(); } catch { /* already aborted */ }
            });
            activeControllersRef.current.clear();

            // 3. CLEAR all SWR cached data globally (prevents stale renders)
            await globalMutate(() => true, undefined, { revalidate: false });

            // 4. RESET local state
            setUser(null);
            setNotifications([]);
            localStorage.removeItem('marffet_premium');

            // 5. Fire-and-forget server logout (non-blocking)
            fetch('/auth/logout', { method: 'GET' }).catch(() => { });

            // 6. Instant client-side redirect
            router.push('/');
        } catch (e) {
            console.error("Logout failed", e);
            window.location.href = '/auth/logout'; // Fallback
        }
    }, [router, globalMutate]);

    const fetchUser = useCallback(async () => {
        const controller = new AbortController();
        const unregister = registerController(controller);
        // Ensure we timeout the entire fetch process, not just the first request
        const timeoutId = setTimeout(() => controller.abort(new Error("Auth fetch timeout")), 10000);

        try {
            const res = await fetch("/auth/me", {
                credentials: "include",
                signal: controller.signal,
            });

            if (res.ok) {
                const data = await res.json();
                if (data && data.id) {
                    setUser(data);

                    // Auto-sync premium status
                    if (data.is_premium) {
                        localStorage.setItem("marffet_premium", "true");
                    }

                    // Fetch notifications - wrapped in its own try/catch so it doesn't fail the whole user fetch
                    try {
                        const notifRes = await fetch("/api/notifications", {
                            credentials: "include",
                            signal: controller.signal,
                        });
                        if (notifRes.ok) {
                            setNotifications(await notifRes.json());
                        }
                    } catch (notifErr) {
                        // Notifications are non-critical
                        console.warn("Notice: Notifications fetch failed or timed out", notifErr);
                    }
                } else {
                    setUser(null);
                    setNotifications([]);
                }
            } else {
                setUser(null);
            }
        } catch (e: any) {
            if (e.name !== 'AbortError' && e.message !== 'Auth fetch timeout') {
                console.error("Auth check failed:", e);
            }
            setUser(null);
        } finally {
            clearTimeout(timeoutId);
            setIsLoading(false);
            unregister();
        }
    }, [registerController]);

    const markAsRead = useCallback(async (id: number) => {
        try {
            await fetch(`/api/notifications/${id}/read`, {
                method: "POST",
                credentials: "include",
            });
            setNotifications(prev =>
                prev.map(n => (n.id === id ? { ...n, is_read: 1 } : n))
            );
        } catch (e) {
            console.error("Mark read error:", e);
        }
    }, []);

    const clearNotifications = useCallback(() => {
        notifications.forEach(n => {
            if (!n.is_read) markAsRead(n.id);
        });
    }, [notifications, markAsRead]);

    // Fetch on mount + notification polling
    useEffect(() => {
        fetchUser();

        // Poll notifications every 30s
        pollingIntervalRef.current = setInterval(async () => {
            try {
                const res = await fetch("/api/notifications", { credentials: "include" });
                if (res.ok) setNotifications(await res.json());
            } catch {
                // Silent fail for polling
            }
        }, 30000);

        return () => {
            if (pollingIntervalRef.current) {
                clearInterval(pollingIntervalRef.current);
                pollingIntervalRef.current = null;
            }
        };
    }, [fetchUser]);

    return (
        <UserContext.Provider
            value={{
                user,
                isLoading,
                notifications,
                unreadCount,
                refreshUser: fetchUser,
                login,
                logout,
                markAsRead,
                clearNotifications,
            }}
        >
            {children}
        </UserContext.Provider>
    );
}
