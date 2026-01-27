"use client";

import { useEffect, useState, useCallback, useRef } from "react";

interface TrendDataPoint {
    month: string;
    cost: number;
}

interface AssetTarget {
    stock_id: string;
    stock_name: string;
    total_shares: number;
    avg_cost: number;
}

interface AssetGroups {
    stock: AssetTarget[];
    etf: AssetTarget[];
    cb: AssetTarget[];
}

interface LivePrices {
    [key: string]: { price: number; change: number; change_pct: number };
}

export default function TrendPage() {
    const [trendData, setTrendData] = useState<TrendDataPoint[]>([]);
    const [assetGroups, setAssetGroups] = useState<AssetGroups>({ stock: [], etf: [], cb: [] });
    const [livePrices, setLivePrices] = useState<LivePrices>({});
    const [selectedMonth, setSelectedMonth] = useState<string | null>(null);
    const [expandedGroup, setExpandedGroup] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);
    const chartRef = useRef<HTMLDivElement>(null);

    const API_BASE = "";

    // Fetch user's portfolio trend data
    const fetchTrendData = useCallback(async () => {
        try {
            // Fetch trend history (all months)
            const trendRes = await fetch(`${API_BASE}/api/portfolio/trend?months=0`, { credentials: "include" });
            if (!trendRes.ok) throw new Error("Failed to fetch trend");
            const trend = await trendRes.json();
            setTrendData(trend);

            if (trend.length > 0) {
                setSelectedMonth(trend[trend.length - 1]?.month);
            }

            // Fetch asset groups (by type)
            const groupRes = await fetch(`${API_BASE}/api/portfolio/by-type`, { credentials: "include" });
            if (groupRes.ok) {
                const groups = await groupRes.json();
                setAssetGroups(groups);

                // Collect stock IDs for live prices
                const allTargets = [...(groups.stock || []), ...(groups.etf || []), ...(groups.cb || [])];
                const ids = allTargets.map((t: AssetTarget) => t.stock_id).filter(Boolean).join(",");

                if (ids) {
                    const priceRes = await fetch(`${API_BASE}/api/portfolio/prices?stock_ids=${ids}`, { credentials: "include" });
                    if (priceRes.ok) {
                        setLivePrices(await priceRes.json());
                    }
                }
            }
        } catch (err) {
            console.error("Trend fetch error:", err);
        }
        setLoading(false);
    }, []);

    useEffect(() => {
        fetchTrendData();
    }, [fetchTrendData]);

    // Calculate group total market value
    const getGroupTotal = (type: keyof AssetGroups) => {
        const targets = assetGroups[type] || [];
        return targets.reduce((total, t) => {
            const price = livePrices[t.stock_id]?.price || 0;
            return total + (t.total_shares || 0) * price;
        }, 0);
    };

    // Calculate group cost
    const getGroupCost = (type: keyof AssetGroups) => {
        const targets = assetGroups[type] || [];
        return targets.reduce((total, t) => {
            return total + (t.total_shares || 0) * (t.avg_cost || 0);
        }, 0);
    };

    const formatCurrency = (val: number) => {
        return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(val);
    };

    const maxCost = Math.max(...trendData.map((t) => t.cost), 1);

    const assetTypes = [
        { key: "stock" as const, label: "📈 Stocks", color: "var(--color-cta)" },
        { key: "etf" as const, label: "📊 ETFs", color: "var(--color-primary)" },
        { key: "cb" as const, label: "💵 CB (Convertible Bonds)", color: "var(--color-success)" },
    ];

    return (
        <div className="max-w-6xl mx-auto space-y-6">
            {/* Header */}
            <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-green-400 to-emerald-600 bg-clip-text text-transparent">
                        📈 Portfolio Trend
                    </h1>
                    <p className="text-[var(--color-text-muted)]">
                        Track your net investment and asset allocation over time
                    </p>
                </div>
                <button
                    onClick={fetchTrendData}
                    className="bg-[var(--color-cta)]/20 border border-[var(--color-cta)] text-[var(--color-cta)] px-4 py-2 rounded hover:bg-[var(--color-cta)] hover:text-black transition font-bold text-sm cursor-pointer"
                >
                    🔄 Refresh
                </button>
            </div>

            {loading ? (
                <div className="text-center py-20 animate-pulse text-[var(--color-text-muted)]">
                    Loading portfolio trend...
                </div>
            ) : trendData.length === 0 ? (
                <div className="glass-card p-8 text-center">
                    <p className="text-6xl mb-4">📊</p>
                    <h2 className="text-2xl font-bold mb-2">No Transaction History</h2>
                    <p className="text-[var(--color-text-muted)]">
                        Add transactions to your portfolio to see your investment trend over time.
                    </p>
                    <a
                        href="/portfolio"
                        className="inline-block mt-4 bg-[var(--color-cta)] text-black px-4 py-2 rounded font-bold"
                    >
                        Go to Portfolio →
                    </a>
                </div>
            ) : (
                <>
                    {/* Chart Section */}
                    <div className="glass-card rounded-xl p-6" ref={chartRef}>
                        <h3 className="text-lg font-bold text-white mb-4">
                            💰 Net Investment Over Time
                        </h3>

                        {/* Simple bar chart visualization */}
                        <div className="space-y-1 max-h-80 overflow-y-auto">
                            {trendData.map((point) => (
                                <div
                                    key={point.month}
                                    onClick={() => setSelectedMonth(point.month)}
                                    className={`flex items-center gap-3 py-1 cursor-pointer transition rounded ${selectedMonth === point.month
                                        ? "bg-[var(--color-cta)]/20"
                                        : "hover:bg-white/5"
                                        }`}
                                >
                                    <span className="w-20 text-xs font-mono text-[var(--color-text-muted)]">
                                        {point.month}
                                    </span>
                                    <div className="flex-1 h-6 bg-black/30 rounded overflow-hidden">
                                        <div
                                            className="h-full bg-gradient-to-r from-[var(--color-cta)] to-[var(--color-primary)] transition-all duration-300"
                                            style={{ width: `${(point.cost / maxCost) * 100}%` }}
                                        />
                                    </div>
                                    <span className="w-28 text-right font-mono font-bold text-white">
                                        ${formatCurrency(point.cost)}
                                    </span>
                                </div>
                            ))}
                        </div>

                        {/* Summary */}
                        <div className="mt-4 pt-4 border-t border-[var(--color-border)] flex justify-between text-sm">
                            <span className="text-[var(--color-text-muted)]">
                                {trendData.length} months tracked
                            </span>
                            <span className="font-mono font-bold text-[var(--color-primary)]">
                                Current: ${formatCurrency(trendData[trendData.length - 1]?.cost || 0)}
                            </span>
                        </div>
                    </div>

                    {/* Asset Groups */}
                    <div className="glass-card rounded-xl p-6">
                        <h3 className="text-lg font-bold text-white mb-4">
                            🗂️ Asset Groups
                        </h3>

                        <div className="space-y-3">
                            {assetTypes.map((type) => {
                                const targets = assetGroups[type.key] || [];
                                const marketValue = getGroupTotal(type.key);
                                const cost = getGroupCost(type.key);
                                const pnl = marketValue - cost;
                                const isExpanded = expandedGroup === type.key;

                                return (
                                    <div key={type.key} className="border border-[var(--color-border)] rounded-lg overflow-hidden">
                                        <div
                                            onClick={() => setExpandedGroup(isExpanded ? null : type.key)}
                                            className="flex items-center justify-between p-4 cursor-pointer hover:bg-white/5 transition"
                                        >
                                            <div className="flex items-center gap-3">
                                                <span className="text-lg">{type.label}</span>
                                                <span className="text-xs text-[var(--color-text-muted)]">
                                                    ({targets.length} holdings)
                                                </span>
                                            </div>
                                            <div className="text-right">
                                                <div className="font-mono font-bold text-white">
                                                    ${formatCurrency(marketValue)}
                                                </div>
                                                <div className={`text-xs font-mono ${pnl >= 0 ? "text-[var(--color-success)]" : "text-[var(--color-danger)]"}`}>
                                                    {pnl >= 0 ? "+" : ""}{formatCurrency(pnl)} P/L
                                                </div>
                                            </div>
                                        </div>

                                        {isExpanded && targets.length > 0 && (
                                            <div className="border-t border-[var(--color-border)] bg-black/20 p-3">
                                                <table className="w-full text-sm">
                                                    <thead className="text-xs text-[var(--color-text-muted)]">
                                                        <tr>
                                                            <th className="text-left p-1">Stock</th>
                                                            <th className="text-right p-1">Shares</th>
                                                            <th className="text-right p-1">Avg Cost</th>
                                                            <th className="text-right p-1">Price</th>
                                                            <th className="text-right p-1">Value</th>
                                                        </tr>
                                                    </thead>
                                                    <tbody>
                                                        {targets.map((t) => {
                                                            const price = livePrices[t.stock_id]?.price || 0;
                                                            const value = t.total_shares * price;
                                                            return (
                                                                <tr key={t.stock_id} className="border-t border-white/5">
                                                                    <td className="p-1 font-medium">{t.stock_name || t.stock_id}</td>
                                                                    <td className="p-1 text-right font-mono">{t.total_shares}</td>
                                                                    <td className="p-1 text-right font-mono">${t.avg_cost?.toFixed(2)}</td>
                                                                    <td className="p-1 text-right font-mono text-[var(--color-cta)]">
                                                                        ${price?.toFixed(2) || "—"}
                                                                    </td>
                                                                    <td className="p-1 text-right font-mono font-bold">
                                                                        ${formatCurrency(value)}
                                                                    </td>
                                                                </tr>
                                                            );
                                                        })}
                                                    </tbody>
                                                </table>
                                            </div>
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}
