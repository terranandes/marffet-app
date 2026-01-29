"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface TrendDataPoint {
    month: string;
    cost: number;
    value: number;
    realized: number;
    dividend: number;
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
    const [expandedGroup, setExpandedGroup] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);

    // Chart visibility toggles
    const [showCost, setShowCost] = useState(true);
    const [showValue, setShowValue] = useState(true);
    const [showRealized, setShowRealized] = useState(false);
    const [showDividend, setShowDividend] = useState(false);

    // Using relative path for API
    const API_BASE = "";

    // Fetch user's portfolio trend data
    const fetchTrendData = useCallback(async () => {
        try {
            // Fetch trend history (matches "real transactions" timeline via months=0)
            const trendRes = await fetch(`${API_BASE}/api/portfolio/trend?months=0`, { credentials: "include" });
            if (!trendRes.ok) throw new Error("Failed to fetch trend");
            const trend = await trendRes.json();
            setTrendData(trend);

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
            // Only count active holdings
            if ((t.total_shares || 0) <= 0) return total;
            const price = livePrices[t.stock_id]?.price || 0;
            return total + t.total_shares * price;
        }, 0);
    };

    // Calculate group cost
    const getGroupCost = (type: keyof AssetGroups) => {
        const targets = assetGroups[type] || [];
        return targets.reduce((total, t) => {
            if ((t.total_shares || 0) <= 0) return total;
            return total + t.total_shares * (t.avg_cost || 0);
        }, 0);
    };

    const formatCurrency = (val: number) => {
        return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(val);
    };

    const assetTypes = [
        { key: "stock" as const, label: "📈 Stocks", color: "var(--color-cta)" },
        { key: "etf" as const, label: "📊 ETFs", color: "var(--color-primary)" },
        { key: "cb" as const, label: "💵 CB (Convertible Bonds)", color: "var(--color-success)" },
    ];

    return (
        <div className="max-w-6xl mx-auto space-y-6 pb-20">
            {/* Header */}
            <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-green-400 to-emerald-600 bg-clip-text text-transparent">
                        📈 Portfolio Trend
                    </h1>
                    <p className="text-[var(--color-text-muted)]">
                        Net investment curve aligned with your transaction history
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
                        Add transactions to begin tracking your investment curve.
                    </p>
                    <a href="/portfolio" className="inline-block mt-4 bg-[var(--color-cta)] text-black px-4 py-2 rounded font-bold">
                        Go to Portfolio →
                    </a>
                </div>
            ) : (
                <>
                    {/* Curve Chart Section */}
                    <div className="glass-card rounded-xl p-6">
                        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-4">
                            <h3 className="text-lg font-bold text-white">
                                📊 Portfolio Metrics Over Time
                            </h3>
                            {/* Toggle Controls */}
                            <div className="flex flex-wrap gap-3 text-xs">
                                <label className="flex items-center gap-1.5 cursor-pointer">
                                    <input type="checkbox" checked={showCost} onChange={() => setShowCost(!showCost)} className="accent-orange-400" />
                                    <span className="text-orange-400">💰 Cost Basis</span>
                                </label>
                                <label className="flex items-center gap-1.5 cursor-pointer">
                                    <input type="checkbox" checked={showValue} onChange={() => setShowValue(!showValue)} className="accent-cyan-400" />
                                    <span className="text-cyan-400">📈 Market Value</span>
                                </label>
                                <label className="flex items-center gap-1.5 cursor-pointer">
                                    <input type="checkbox" checked={showRealized} onChange={() => setShowRealized(!showRealized)} className="accent-green-400" />
                                    <span className="text-green-400">💵 Realized P/L</span>
                                </label>
                                <label className="flex items-center gap-1.5 cursor-pointer">
                                    <input type="checkbox" checked={showDividend} onChange={() => setShowDividend(!showDividend)} className="accent-purple-400" />
                                    <span className="text-purple-400">🎁 Dividends</span>
                                </label>
                            </div>
                        </div>
                        <div className="w-full h-[350px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={trendData}>
                                    <defs>
                                        <linearGradient id="colorCost" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#f97316" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
                                        </linearGradient>
                                        <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#22d3ee" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#22d3ee" stopOpacity={0} />
                                        </linearGradient>
                                        <linearGradient id="colorRealized" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#4ade80" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#4ade80" stopOpacity={0} />
                                        </linearGradient>
                                        <linearGradient id="colorDividend" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#c084fc" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#c084fc" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--color-border)" opacity={0.3} />
                                    <XAxis
                                        dataKey="month"
                                        tick={{ fill: 'var(--color-text-muted)', fontSize: 12 }}
                                        tickLine={false}
                                        axisLine={false}
                                        minTickGap={30}
                                    />
                                    <YAxis
                                        tick={{ fill: 'var(--color-text-muted)', fontSize: 12 }}
                                        tickLine={false}
                                        axisLine={false}
                                        tickFormatter={(val) => `$${val / 1000}k`}
                                    />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: 'rgba(0,0,0,0.9)', borderColor: 'var(--color-border)', borderRadius: '8px' }}
                                        formatter={(value: any, name?: string) => {
                                            const labels: Record<string, string> = {
                                                cost: '💰 Cost Basis',
                                                value: '📈 Market Value',
                                                realized: '💵 Realized P/L',
                                                dividend: '🎁 Dividends'
                                            };
                                            return [`$${formatCurrency(Number(value))}`, labels[name || ''] || name || 'Unknown'];
                                        }}
                                        labelStyle={{ color: 'var(--color-text-muted)' }}
                                    />
                                    {showCost && (
                                        <Area
                                            type="monotone"
                                            dataKey="cost"
                                            name="cost"
                                            stroke="#f97316"
                                            strokeWidth={2}
                                            fillOpacity={1}
                                            fill="url(#colorCost)"
                                            animationDuration={1500}
                                        />
                                    )}
                                    {showValue && (
                                        <Area
                                            type="monotone"
                                            dataKey="value"
                                            name="value"
                                            stroke="#22d3ee"
                                            strokeWidth={2}
                                            fillOpacity={1}
                                            fill="url(#colorValue)"
                                            animationDuration={1500}
                                        />
                                    )}
                                    {showRealized && (
                                        <Area
                                            type="monotone"
                                            dataKey="realized"
                                            name="realized"
                                            stroke="#4ade80"
                                            strokeWidth={2}
                                            fillOpacity={1}
                                            fill="url(#colorRealized)"
                                            animationDuration={1500}
                                        />
                                    )}
                                    {showDividend && (
                                        <Area
                                            type="monotone"
                                            dataKey="dividend"
                                            name="dividend"
                                            stroke="#c084fc"
                                            strokeWidth={2}
                                            fillOpacity={1}
                                            fill="url(#colorDividend)"
                                            animationDuration={1500}
                                        />
                                    )}
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Asset Groups (Filtered) */}
                    <div className="glass-card rounded-xl p-6">
                        <h3 className="text-lg font-bold text-white mb-4">
                            🗂️ Active Holdings
                        </h3>

                        <div className="space-y-3">
                            {assetTypes.map((type) => {
                                // Filter: Only show targets with active shares
                                // (If shares are 0, it's a watchlist item or sold out - excluded as requested)
                                const rawTargets = assetGroups[type.key] || [];
                                const activeTargets = rawTargets.filter(t => (t.total_shares || 0) > 0);

                                if (activeTargets.length === 0) return null;

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
                                                    ({activeTargets.length} holdings)
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

                                        {isExpanded && (
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
                                                        {activeTargets.map((t) => {
                                                            const price = livePrices[t.stock_id]?.price || 0;
                                                            const value = t.total_shares * price;
                                                            return (
                                                                <tr key={t.stock_id} className="border-t border-white/5 hover:bg-white/5">
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

                            {/* Fallback if all groups are empty */}
                            {assetTypes.every(t => (assetGroups[t.key] || []).filter(at => (at.total_shares || 0) > 0).length === 0) && (
                                <div className="text-[var(--color-text-muted)] text-center py-4">
                                    No active holdings found.
                                    <br />
                                    <span className="text-xs">Targets with 0 shares (watchlist) are hidden.</span>
                                </div>
                            )}
                        </div>
                    </div>
                </>
            )}

            {/* My Race CTA */}
            <div className="w-full p-4 rounded-xl border border-[var(--color-border)] bg-black/40 flex justify-center items-center gap-2 text-sm mt-8">
                <span className="text-[var(--color-text-muted)]">See your investments compete! →</span>
                <a
                    href="/myrace"
                    className="font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent hover:opacity-80 transition"
                >
                    🏎️ Open My Race Tab
                </a>
            </div>
        </div>
    );
}
