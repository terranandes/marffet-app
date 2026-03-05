"use client";

import { useEffect, useState } from "react";
import AICopilot from "./AICopilot";
import ToasterProvider from "./ToasterProvider";
import { LanguageProvider } from "../lib/i18n/LanguageContext";
import { UserProvider, useUser } from "../lib/UserContext";

const API_BASE = "";

function AICopilotWithContext() {
    const { user } = useUser();
    const [context, setContext] = useState("");

    useEffect(() => {
        if (!user || !user.id) return;

        const fetchContext = async () => {
            try {
                const [pRes, cRes] = await Promise.all([
                    fetch(`${API_BASE}/api/portfolio/by-type`, { credentials: "include" }).catch(() => null),
                    fetch(`${API_BASE}/api/portfolio/dividends/total`, { credentials: "include" }).catch(() => null),
                ]);

                const pData = pRes && pRes.ok ? await pRes.json() : null;
                const cData = cRes && cRes.ok ? await cRes.json() : 0;

                if (pData || cData !== null) {
                    const summary = {
                        dividend_cash: cData?.total_dividends || cData || 0,
                        holdings: pData || "None",
                    };
                    setContext(JSON.stringify(summary, null, 2));
                }
            } catch (e) {
                console.error("Context fetch failed", e);
            }
        };
        fetchContext();
    }, [user]);

    return <AICopilot user={user} portfolioContext={context} />;
}

export default function ClientProviders({ children }: { children: React.ReactNode }) {
    return (
        <LanguageProvider>
            <UserProvider>
                {children}
                <AICopilotWithContext />
                <ToasterProvider />
            </UserProvider>
        </LanguageProvider>
    );
}
