"use client";

import { useState, useCallback, useMemo } from "react";
import useSWR from "swr";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { ChartSkeleton, TableSkeleton } from "@/components/Skeleton";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import { useUser } from "@/lib/UserContext";

interface TrendDataPoint {
    month: string;
    cost: number;
    value: number;
    realized: number;
    dividend: number;
    unrealized: number;
}

interface AssetGroups {
    [key: string]: {
        stock_id: string;
        stock_name: string;
        total_shares: number;
        avg_cost: number;
    }[];
}

interface LivePrices {
    [key: string]: {
        price: number;
        change: number;
        change_pct: number;
    };
}

const API_BASE = "";
const fetcher = (url: string) => fetch(url, { credentials: "include" }).then(res => {
    if (!res.ok) throw new Error('API return non-200');
    return res.json();
});

export default function TrendPage() {
    const { t } = useLanguage();
    const { user } = useUser();
    const [expandedGroup, setExpandedGroup] = useState<string | null>(null);

    // Chart Toggles
    const [showCost, setShowCost] = useState(true);
    const [showValue, setShowValue] = useState(true);
    const [showRealized, setShowRealized] = useState(true);
    const [showDividend, setShowDividend] = useState(true);
    const [showUnrealized, setShowUnrealized] = useState(true);

    // SWR Data Fetching (Only run if user is logged in)
    const { data: rawTrend, error: trendError, mutate: mutateTrend } = useSWR<TrendDataPoint[]>(
        user ? `${API_BASE}/api/portfolio/trend?months=0` : null,
        fetcher
    );
    const { data: assetGroups = { stock: [], etf: [], cb: [] }, error: groupError } = useSWR<AssetGroups>(
        user ? `${API_BASE}/api/portfolio/by-type` : null,
        fetcher
    );

    // Calculate if we have any active shares to determine if we should fetch live prices
    const hasActiveShares = useMemo(() => {
        if (!assetGroups) return false;
        return Object.values(assetGroups).some(group =>
            group.some(target => (target.total_shares || 0) > 0)
        );
    }, [assetGroups]);

    // Live Prices (Only fetch if logged in AND has active shares)
    const shouldFetchLivePrices = user && hasActiveShares;
    const { data: livePrices = {} } = useSWR<LivePrices>(
        shouldFetchLivePrices ? "/api/portfolio/live_prices" : null,
        fetcher,
        {
            refreshInterval: 60000, // Refresh live prices every 60s
            revalidateOnFocus: true
        }
    );

    // Process Trend Data to compute unrealized P/L
    const trendData = useMemo(() => {
        if (!rawTrend) return [];
        return rawTrend.map(d => ({
            ...d,
            unrealized: (d.value || 0) - (d.cost || 0)
        }));
    }, [rawTrend]);

    const loading = !rawTrend && !trendError;

    // Refresh function mapped to SWR mutate
    const fetchTrendData = useCallback(() => {
        mutateTrend();
    }, [mutateTrend]);

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
        { key: "stock" as const, label: t('Trend.Stocks'), color: "var(--color-cta)" },
        { key: "etf" as const, label: t('Trend.ETFs'), color: "var(--color-primary)" },
        { key: "cb" as const, label: t('Trend.CB'), color: "var(--color-success)" },
    ];

    return (
        <div className="max-w-6xl mx-auto space-y-6 pb-20">
            {/* Header */}
            <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-green-400 to-emerald-600 bg-clip-text text-transparent">
                        {t('Trend.Title')}
                    </h1>
                    <p className="text-[var(--color-text-muted)]">
                        {t('Trend.Subtitle')}
                    </p>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={async () => {
                            try {
                                const res = await fetch('/api/sync/my-dividends', { method: 'POST', credentials: 'include' });
                                const data = await res.json();
                                alert(data.message || t('Trend.SyncComplete'));
                                fetchTrendData(); // Refresh after sync
                            } catch (e) {
                                alert(t('Trend.SyncFailed'));
                            }
                        }}
                        className="bg-amber-500/20 border border-amber-500 text-amber-400 px-4 py-2 rounded hover:bg-amber-500 hover:text-black transition font-bold text-sm cursor-pointer"
                    >
                        {t('Trend.SyncDividends')}
                    </button>
                    <button
                        onClick={fetchTrendData}
                        className="bg-[var(--color-cta)]/20 border border-[var(--color-cta)] text-[var(--color-cta)] px-4 py-2 rounded hover:bg-[var(--color-cta)] hover:text-black transition font-bold text-sm cursor-pointer"
                    >
                        {t('Trend.Refresh')}
                    </button>
                </div>
            </div>

            {loading ? (
                <div className="space-y-6">
                    <ChartSkeleton height="h-[350px]" />
                    <TableSkeleton rows={5} cols={5} />
                </div>
            ) : trendData.length === 0 ? (
                <div className="glass-card p-8 text-center">
                    <p className="text-6xl mb-4">📊</p>
                    <h2 className="text-2xl font-bold mb-2">{t('Trend.NoTransactionHistory')}</h2>
                    <p className="text-[var(--color-text-muted)]">
                        {t('Trend.AddTransactions')}
                    </p>
                    <a href="/portfolio" className="inline-block mt-4 bg-[var(--color-cta)] text-black px-4 py-2 rounded font-bold">
                        {t('Trend.GoToPortfolio')}
                    </a>
                </div>
            ) : (
                <>
                    {/* Curve Chart Section */}
                    <div className="glass-card rounded-xl p-6">
                        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-4">
                            <h3 className="text-lg font-bold text-white">
                                {t('Trend.PortfolioMetrics')}
                            </h3>
                            {/* Toggle Controls */}
                            <div className="flex flex-wrap gap-3 text-xs">
                                <label className="flex items-center gap-1.5 cursor-pointer">
                                    <input type="checkbox" checked={showCost} onChange={() => setShowCost(!showCost)} className="accent-orange-400" />
                                    <span className="text-orange-400">{t('Trend.CostBasis')}</span>
                                </label>
                                <label className="flex items-center gap-1.5 cursor-pointer">
                                    <input type="checkbox" checked={showValue} onChange={() => setShowValue(!showValue)} className="accent-cyan-400" />
                                    <span className="text-cyan-400">{t('Trend.MarketValue')}</span>
                                </label>
                                <label className="flex items-center gap-1.5 cursor-pointer">
                                    <input type="checkbox" checked={showRealized} onChange={() => setShowRealized(!showRealized)} className="accent-green-400" />
                                    <span className="text-green-400">{t('Trend.RealizedPL')}</span>
                                </label>
                                <label className="flex items-center gap-1.5 cursor-pointer">
                                    <input type="checkbox" checked={showDividend} onChange={() => setShowDividend(!showDividend)} className="accent-amber-400" />
                                    <span className="text-amber-400">{t('Trend.Dividends')}</span>
                                </label>
                                <label className="flex items-center gap-1.5 cursor-pointer">
                                    <input type="checkbox" checked={showUnrealized} onChange={() => setShowUnrealized(!showUnrealized)} className="accent-yellow-400" />
                                    <span className="text-yellow-400">{t('Trend.UnrealizedPL')}</span>
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
                                            <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                                        </linearGradient>
                                        <linearGradient id="colorUnrealized" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#facc15" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#facc15" stopOpacity={0} />
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
                                                cost: t('Trend.CostBasis'),
                                                value: t('Trend.MarketValue'),
                                                realized: t('Trend.RealizedPL'),
                                                dividend: t('Trend.Dividends'),
                                                unrealized: t('Trend.UnrealizedPL')
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
                                            stroke="#f59e0b"
                                            strokeWidth={2}
                                            fillOpacity={1}
                                            fill="url(#colorDividend)"
                                            animationDuration={1500}
                                        />
                                    )}
                                    {showUnrealized && (
                                        <Area
                                            type="monotone"
                                            dataKey="unrealized"
                                            name="unrealized"
                                            stroke="#facc15"
                                            strokeWidth={2}
                                            fillOpacity={1}
                                            fill="url(#colorUnrealized)"
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
                            {t('Trend.ActiveHoldings')}
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
                                                    {t('Trend.HoldingsCount').replace('{count}', activeTargets.length.toString())}
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
                                                            <th className="text-left p-1">{t('Trend.Stock')}</th>
                                                            <th className="text-right p-1">{t('Trend.Shares')}</th>
                                                            <th className="text-right p-1">{t('Trend.AvgCost')}</th>
                                                            <th className="text-right p-1">{t('Trend.Price')}</th>
                                                            <th className="text-right p-1">{t('Trend.Value')}</th>
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
                                    {t('Trend.NoActiveHoldings')}
                                    <br />
                                    <span className="text-xs">{t('Trend.TargetsHidden')}</span>
                                </div>
                            )}
                        </div>
                    </div>
                </>
            )}

            {/* My Race CTA */}
            <div className="w-full p-4 rounded-xl border border-[var(--color-border)] bg-black/40 flex justify-center items-center gap-2 text-sm mt-8">
                <span className="text-[var(--color-text-muted)]">{t('Trend.SeeInvestmentsCompete')}</span>
                <a
                    href="/myrace"
                    className="font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent hover:opacity-80 transition"
                >
                    {t('Trend.OpenMyRaceTab')}
                </a>
            </div>
        </div>
    );
}
