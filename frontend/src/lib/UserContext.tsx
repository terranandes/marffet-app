"use client";

import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react";

interface User {
    id: string | null;
    email?: string;
    is_admin?: boolean;
    is_premium?: boolean;
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

    const unreadCount = notifications.filter(n => !n.is_read).length;

    const fetchUser = useCallback(async () => {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 8000);

            const res = await fetch("/auth/me", {
                credentials: "include",
                signal: controller.signal,
            });

            clearTimeout(timeoutId);

            if (res.ok) {
                const data = await res.json();
                if (data && data.id) {
                    setUser(data);

                    // Auto-sync premium status
                    if (data.is_premium) {
                        localStorage.setItem("marffet_premium", "true");
                    }

                    // Fetch notifications
                    try {
                        const notifRes = await fetch("/api/notifications", {
                            credentials: "include",
                        });
                        if (notifRes.ok) {
                            setNotifications(await notifRes.json());
                        }
                    } catch {
                        // Notifications are non-critical
                    }
                } else {
                    setUser(null);
                    setNotifications([]);
                }
            } else {
                setUser(null);
            }
        } catch (e) {
            console.error("Auth check failed:", e);
            setUser(null);
        } finally {
            setIsLoading(false);
        }
    }, []);

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

    // Fetch on mount
    useEffect(() => {
        fetchUser();

        // Poll notifications every 30s
        const interval = setInterval(async () => {
            try {
                const res = await fetch("/api/notifications", { credentials: "include" });
                if (res.ok) setNotifications(await res.json());
            } catch {
                // Silent fail for polling
            }
        }, 30000);

        return () => clearInterval(interval);
    }, [fetchUser]);

    return (
        <UserContext.Provider
            value={{
                user,
                isLoading,
                notifications,
                unreadCount,
                refreshUser: fetchUser,
                markAsRead,
                clearNotifications,
            }}
        >
            {children}
        </UserContext.Provider>
    );
}
