"use client";

import { useEffect, useState } from "react";
import AICopilot from "./AICopilot";

const API_BASE = "";

export default function ClientProviders({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<any>(null);

    useEffect(() => {
        const checkAuth = async () => {
            try {
                const res = await fetch(`${API_BASE}/auth/me`, { credentials: "include" });
                if (res.ok) {
                    const data = await res.json();
                    setUser(data);
                }
            } catch (e) {
                console.error("Auth check failed", e);
            }
        };
        checkAuth();
    }, []);

    return (
        <>
            {children}
            <AICopilot user={user} />
        </>
    );
}
