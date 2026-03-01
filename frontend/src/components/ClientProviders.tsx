"use client";

import { useEffect, useState } from "react";
import AICopilot from "./AICopilot";
import ToasterProvider from "./ToasterProvider";
import { LanguageProvider } from "../lib/i18n/LanguageContext";

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
                            fetch(`${API_BASE}/api/portfolio/by-type`, { credentials: "include" }).catch(() => null),
                            fetch(`${API_BASE}/api/portfolio/dividends/total`, { credentials: "include" }).catch(() => null)
                        ]);

                        const pData = pRes && pRes.ok ? await pRes.json() : null;
                        const cData = cRes && cRes.ok ? await cRes.json() : 0;

                        if (pData || cData !== null) {
                            const summary = {
                                dividend_cash: cData?.total_dividends || cData || 0,
                                holdings: pData || "None"
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
        <LanguageProvider>
            {children}
            <AICopilot user={user} portfolioContext={context} />
            <ToasterProvider />
        </LanguageProvider>
    );
}
