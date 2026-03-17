"use client";

import { useState } from "react";
import useSWR from "swr";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import { useUser } from "@/lib/UserContext";
import { SyncIndicator } from "@/app/components/SyncIndicator";

interface CBData {
    code: string;
    name: string;
    stock_price: number;
    cb_price: number;
    conv_price: number;
    premium: number;
    action: string;
    description: string;
}

interface CBResponse {
    action: string;
    description: string;
}

const fetcher = (url: string) => fetch(url, { credentials: "include" }).then(res => {
    if (!res.ok) throw new Error("Fetch failed");
    return res.json();
});

export default function CBPage() {
    const { t } = useLanguage();
    const { user } = useUser();

    const API_BASE = "";

    // SWR Data Fetching for Portfolio CBs
    const { data = [], isValidating: loadingPortfolio } = useSWR<CBData[]>(
        user ? "/api/cb/my_cbs" : null,
        fetcher,
        { keepPreviousData: true }
    );
    const portfolioCBs = Array.isArray(data) ? data : [];

    // Analyzer State
    const [cbInput, setCbInput] = useState("");
    const [cbResult, setCbResult] = useState<(CBData & { action: string, description: string }) | null>(null);
    const [loadingAnalyze, setLoadingAnalyze] = useState(false);

    // Analyze CB
    const analyzeCB = async () => {
        if (!cbInput.trim()) return;
        setLoadingAnalyze(true);
        setCbResult(null);
        try {
            const res = await fetch(`${API_BASE}/api/cb/analyze?code=${cbInput}`, { credentials: "include" });
            if (res.ok) {
                setCbResult(await res.json());
            } else {
                alert(t('CB.NotFound'));
            }
        } catch (err) {
            console.error("Analyze error:", err);
        }
        setLoadingAnalyze(false);
    };

    const getActionColor = (action: string) => {
        if (!action) return "text-[var(--color-text-muted)]";
        if (action.includes("BUY")) return "text-[var(--color-success)]";
        if (action.includes("SELL")) return "text-[var(--color-danger)]";
        return "text-[var(--color-warning)]";
    };

    const getBorderColor = (action: string) => {
        if (!action) return "border-[var(--color-border)]";
        if (action.includes("BUY")) return "border-[var(--color-success)] bg-gradient-to-r from-[var(--color-success)]/10 to-transparent";
        if (action.includes("SELL")) return "border-[var(--color-danger)] bg-gradient-to-r from-[var(--color-danger)]/10 to-transparent";
        return "border-[var(--color-warning)] bg-gradient-to-r from-[var(--color-warning)]/10 to-transparent";
    };

    return (
        <div className="max-w-4xl mx-auto space-y-8 pb-10">
            {/* Header */}
            <div className="text-center">
                <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-600 bg-clip-text text-transparent">
                    {t('CB.Title')}
                </h1>
                <p className="text-[var(--color-text-muted)]">
                    {t('CB.Subtitle')}
                </p>
            </div>

            {/* My Portfolio CBs */}
            <div className="glass-card rounded-xl p-6 border border-[var(--color-border)]">
                <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                    <span className="text-[var(--color-cta)]">💼</span> {t('CB.MyPortfolio')}
                </h2>

                {loadingPortfolio ? (
                    <div className="text-center py-10 animate-pulse text-[var(--color-text-muted)]">
                        {t('CB.Loading')}
                    </div>
                ) : portfolioCBs.length === 0 ? (
                    <div className="text-center py-10 text-[var(--color-text-muted)]">
                        {t('CB.NoCBs')}
                        <div className="mt-4">
                            <a href="/portfolio" className="text-[var(--color-cta)] hover:underline">{t('CB.GoToPortfolio')}</a>
                        </div>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {portfolioCBs.map((cb) => (
                            <div
                                key={cb.code}
                                className={`rounded-xl p-4 border-l-4 transition hover:bg-white/5 ${getBorderColor(cb.action)}`}
                            >
                                <div className="flex justify-between items-start mb-2">
                                    <div>
                                        <div className="font-bold text-lg text-white">
                                            {cb.code} {cb.name}
                                        </div>
                                        <div className="text-xs text-[var(--color-text-muted)] mt-1">
                                            {t('CB.Stock')}: <span className="text-white">{cb.stock_price}</span> |
                                            CB: <span className="text-white">{cb.cb_price}</span> |
                                            {t('CB.Conv')}: <span className="text-white">{cb.conv_price}</span>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <div className={`text-2xl font-bold ${getActionColor(cb.action)}`}>
                                            {cb.premium}%
                                        </div>
                                        <div className="text-[10px] uppercase tracking-wider text-[var(--color-text-muted)]">
                                            {t('CB.Premium')}
                                        </div>
                                    </div>
                                </div>
                                <div className="flex justify-between items-center mt-2 pt-2 border-t border-white/5">
                                    <div className={`inline-block px-2 py-1 rounded text-xs font-bold bg-black/30 ${getActionColor(cb.action)}`}>
                                        {cb.action}
                                    </div>
                                    <div className="text-xs text-[var(--color-text-muted)] italic truncate ml-2 max-w-[200px] lg:max-w-md">
                                        {cb.description}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* CB Analyzer */}
            <div className="glass-card rounded-xl p-8 border border-[var(--color-cta)]/30 shadow-[0_0_20px_rgba(0,242,234,0.1)]">
                <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                    <span className="text-[var(--color-cta)]">💰</span> {t('CB.Analyzer')}
                </h2>

                <div className="flex gap-4 mb-8">
                    <input
                        value={cbInput}
                        onChange={(e) => setCbInput(e.target.value)}
                        onKeyPress={(e) => e.key === "Enter" && analyzeCB()}
                        type="text"
                        placeholder={t('CB.Placeholder')}
                        className="flex-1 bg-black/50 border border-[var(--color-border)] rounded-lg px-4 py-3 focus:border-[var(--color-cta)] outline-none text-white transition"
                    />
                    <button
                        onClick={analyzeCB}
                        disabled={loadingAnalyze}
                        className="bg-[var(--color-cta)] text-black font-bold px-6 py-3 rounded-lg hover:bg-cyan-400 disabled:opacity-50 transition cursor-pointer"
                    >
                        {loadingAnalyze ? t('CB.Scanning') : t('CB.Analyze')}
                    </button>
                </div>

                {cbResult && (
                    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <div className="flex justify-between items-baseline mb-4">
                            <h3 className="text-3xl font-bold text-white">
                                {cbResult.code} {cbResult.name}
                            </h3>
                            <span className={`text-xl font-mono font-bold ${getActionColor(cbResult.action)}`}>
                                {cbResult.action}
                            </span>
                        </div>

                        <div className="grid grid-cols-3 gap-2 mb-6 text-sm text-[var(--color-text-muted)] bg-black/30 p-4 rounded-lg">
                            <div>{t('CB.Stock')}: <span className="text-white font-mono">{cbResult.stock_price}</span></div>
                            <div>CB: <span className="text-white font-mono">{cbResult.cb_price}</span></div>
                            <div>{t('CB.Conv')}: <span className="text-white font-mono">{cbResult.conv_price}</span></div>
                        </div>

                        <div className={`p-4 rounded-lg border-l-4 ${getBorderColor(cbResult.action)}`}>
                            <div className="text-xs uppercase tracking-wider text-[var(--color-text-muted)] mb-1">
                                {t('CB.PremiumRate')}
                            </div>
                            <div className={`text-4xl font-bold mb-2 ${getActionColor(cbResult.action)}`}>
                                {cbResult.premium}%
                            </div>
                            <p className="text-sm italic text-[var(--color-text-muted)]">
                                {cbResult.description}
                            </p>
                        </div>
                    </div>
                )}
            </div>
            <SyncIndicator isSyncing={loadingPortfolio || loadingAnalyze} />
        </div>
    );
}
