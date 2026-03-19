import React from "react";
import { useLanguage } from "@/lib/i18n/LanguageContext";

interface PortfolioHeaderProps {
    isGuest: boolean;
    dividendCash: { total_cash: number; dividend_count: number };
    syncing: boolean;
    onSync: () => void;
    showAddGroup: boolean;
    onToggleAddGroup: () => void;
    isValidating?: boolean;
}

export function PortfolioHeader({
    isGuest,
    dividendCash,
    syncing,
    onSync,
    showAddGroup,
    onToggleAddGroup,
    isValidating = false
}: PortfolioHeaderProps) {
    const { t } = useLanguage();
    const formatCurrency = (val: number) => {
        return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(val);
    };

    return (
        <div className="glass-card p-5 rounded-xl">
            <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center mb-4 gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-[var(--color-cta)] flex items-center gap-2">
                        📊 {t('Portfolio.Title') || "My Portfolio"}
                        {isGuest && (
                            <span className="text-xs bg-yellow-500/20 text-yellow-500 px-2 py-1 rounded border border-yellow-500/50">
                                {t('Portfolio.GuestMode') || "Guest Mode"}
                            </span>
                        )}
                        {isValidating && !syncing && (
                            <span className="text-[10px] animate-pulse bg-blue-500/10 text-blue-400 px-1.5 py-0.5 rounded border border-blue-500/30 font-normal ml-1">
                                📡 REVALIDATING
                            </span>
                        )}
                    </h1>
                    <div className="text-sm text-[var(--color-text-muted)] mt-1">
                        💰 {t('Portfolio.DividendCash') || "Dividend Cash"}:{" "}
                        <span className="text-[var(--color-success)] font-mono font-bold">
                            ${formatCurrency(dividendCash.total_cash)}
                        </span>
                        <span className="ml-2">({dividendCash.dividend_count} {t('Portfolio.Payments') || "payments"})</span>
                    </div>
                </div>
                <div className="flex gap-2 w-full lg:w-auto">
                    <button
                        onClick={onSync}
                        disabled={syncing}
                        className={`flex-1 lg:flex-none border px-4 py-2 rounded transition text-sm font-bold cursor-pointer flex items-center justify-center gap-2 ${syncing
                            ? "bg-[var(--color-success)]/10 border-[var(--color-success)]/30 text-[var(--color-success)] cursor-not-allowed"
                            : "bg-[var(--color-success)]/20 border-[var(--color-success)] text-[var(--color-success)] hover:bg-[var(--color-success)] hover:text-black"
                            }`}
                    >
                        <span className={syncing ? "animate-spin" : ""}>{syncing ? "⏳" : "🔄"}</span>
                        <span>{syncing ? (t('Portfolio.Syncing') || "Syncing...") : (t('Portfolio.SyncDividends') || "Sync Dividends")}</span>
                    </button>
                    <button
                        onClick={onToggleAddGroup}
                        className="flex-1 lg:flex-none bg-[var(--color-cta)]/20 border border-[var(--color-cta)] text-[var(--color-cta)] px-4 py-2 rounded hover:bg-[var(--color-cta)] hover:text-black transition text-sm font-bold cursor-pointer"
                    >
                        {showAddGroup ? (t('Portfolio.Cancel') || "Cancel") : (t('Portfolio.NewGroup') || "+ New Group")}
                    </button>
                </div>
            </div>
        </div>
    );
}
