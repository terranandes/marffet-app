"use client";

import { useEffect, useState } from "react";
import AICopilot from "./AICopilot";

const API_BASE = "";

export default function ClientProviders({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<any>(null);

    const [context, setContext] = useState("");

    useEffect(() => {
        const checkAuth = async () => {
            try {
                const res = await fetch(`${API_BASE}/auth/me`, { credentials: "include" });
                if (res.ok) {
                    const data = await res.json();
                    setUser(data);

                    // Fetch Context if logged in
                    try {
                        const [pRes, cRes] = await Promise.all([
                            fetch(`${API_BASE}/api/portfolio/by-type`, { credentials: "include" }),
                            fetch(`${API_BASE}/api/portfolio/cash`, { credentials: "include" })
                        ]);

                        if (pRes.ok && cRes.ok) {
                            const pData = await pRes.json();
                            const cData = await cRes.json();

                            const summary = {
                                cash: cData,
                                holdings: pData
                            };
                            setContext(JSON.stringify(summary, null, 2));
                        }
                    } catch (e) {
                        console.error("Context fetch failed", e);
                    }
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
            <AICopilot user={user} portfolioContext={context} />
        </>
    );
}
