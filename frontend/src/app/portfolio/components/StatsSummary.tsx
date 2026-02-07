import React from "react";

interface StatsSummaryProps {
    stats: {
        marketValue: number;
        realized: number;
        unrealized: number;
        unrealizedPct: number;
    };
}

export function StatsSummary({ stats }: StatsSummaryProps) {
    const formatCurrency = (val: number) => {
        return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(val);
    };

    return (
        <div className="mb-6 bg-black/40 rounded-xl p-4 lg:p-6 border border-white/5">
            <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6">
                <div>
                    <div className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mb-1">
                        Market Value
                    </div>
                    <div className="font-mono font-bold text-3xl lg:text-4xl text-white">
                        {formatCurrency(stats.marketValue)}
                        <span className="text-base text-[var(--color-text-muted)] ml-2">TWD</span>
                    </div>
                </div>
                <div className="flex w-full lg:w-auto gap-4 lg:gap-12">
                    <div className="flex-1">
                        <div className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mb-1">
                            Realized P/L
                        </div>
                        <div
                            className={`font-mono font-bold text-lg lg:text-xl ${stats.realized >= 0 ? "text-red-400" : "text-green-400"
                                }`}
                        >
                            {stats.realized >= 0 ? "+" : ""}
                            {formatCurrency(stats.realized)}
                        </div>
                    </div>
                    <div className="flex-1 text-right lg:text-left">
                        <div className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mb-1">
                            Unrealized P/L
                        </div>
                        <div
                            className={`font-mono font-bold text-lg ${stats.unrealized >= 0 ? "text-red-400" : "text-green-400"
                                }`}
                        >
                            {stats.unrealized >= 0 ? "+" : ""}
                            {formatCurrency(stats.unrealized)}
                            <span className="text-sm ml-1">
                                ({stats.unrealizedPct >= 0 ? "▲" : "▼"}
                                {Math.abs(stats.unrealizedPct).toFixed(2)}%)
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
