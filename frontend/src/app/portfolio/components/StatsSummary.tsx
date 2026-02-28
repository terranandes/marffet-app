import dynamic from 'next/dynamic';
import React, { useMemo } from "react";
import { Target } from "../../../services/portfolioService";

const ReactECharts = dynamic(() => import('echarts-for-react'), { ssr: false });

interface StatsSummaryProps {
    stats: {
        marketValue: number;
        realized: number;
        unrealized: number;
        unrealizedPct: number;
    };
    targets?: Target[];
}

export function StatsSummary({ stats, targets = [] }: StatsSummaryProps) {
    const formatCurrency = (val: number) => {
        return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(val);
    };

    const chartOptions = useMemo(() => {
        if (!targets || targets.length === 0) return {};

        // Sort targets by market value descending
        const sorted = [...targets].sort((a, b) =>
            (b.summary?.market_value || 0) - (a.summary?.market_value || 0)
        );

        // Take top 5, group rest into "Other"
        const top5 = sorted.slice(0, 5);
        const other = sorted.slice(5);

        const data = top5.map(t => ({
            name: t.stock_name || t.stock_id,
            value: t.summary?.market_value || 0
        })).filter(d => d.value > 0);

        if (other.length > 0) {
            const otherVal = other.reduce((sum, t) => sum + (t.summary?.market_value || 0), 0);
            if (otherVal > 0) {
                data.push({ name: "Other", value: otherVal });
            }
        }

        return {
            tooltip: {
                trigger: 'item',
                backgroundColor: 'rgba(0,0,0,0.8)',
                borderColor: '#333',
                textStyle: { color: '#fff', fontSize: 12 },
                valueFormatter: (val: number) => "$" + formatCurrency(val)
            },
            series: [
                {
                    name: 'Allocation',
                    type: 'pie',
                    radius: ['55%', '90%'],
                    center: ['50%', '50%'],
                    avoidLabelOverlap: false,
                    itemStyle: {
                        borderRadius: 3,
                        borderColor: '#18181b', // zinc-900 matching background
                        borderWidth: 2
                    },
                    label: { show: false },
                    labelLine: { show: false },
                    data: data,
                    // Cyberpunk / Premium Fintech Palette
                    color: ['#06b6d4', '#f59e0b', '#10b981', '#6366f1', '#ec4899', '#64748b']
                }
            ]
        };
    }, [targets]);

    return (
        <div className="mb-6 bg-black/40 rounded-xl p-4 lg:p-6 border border-white/5 relative overflow-hidden">
            {/* Ambient Background Glow */}
            <div className="absolute -top-32 -right-32 w-80 h-80 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />

            <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6 relative z-10 w-full">
                {/* Value Section */}
                <div className="flex flex-col flex-1">
                    <div className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mb-2 font-bold w-full">
                        Total Portfolio Value
                    </div>
                    <div className="font-mono font-bold text-4xl lg:text-5xl text-white mb-3 drop-shadow-[0_0_10px_rgba(255,255,255,0.1)] w-full">
                        {formatCurrency(stats.marketValue)}
                        <span className="text-base text-[var(--color-text-muted)] ml-2 opacity-50 font-sans">TWD</span>
                    </div>

                    <div className="flex flex-wrap gap-4 mt-2">
                        <div className="bg-white/5 rounded-lg px-4 py-3 border border-white/5 min-w-[140px]">
                            <div className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-wider mb-1 flex items-center gap-1">
                                <span>Realized P/L</span>
                            </div>
                            <div className={`font-mono font-bold text-sm lg:text-base ${stats.realized >= 0 ? "text-red-400 drop-shadow-[0_0_3px_rgba(248,113,113,0.3)]" : "text-green-400 drop-shadow-[0_0_3px_rgba(74,222,128,0.3)]"}`}>
                                {stats.realized >= 0 ? "+" : ""}{formatCurrency(stats.realized)}
                            </div>
                        </div>
                        <div className="bg-white/5 rounded-lg px-4 py-3 border border-white/5 min-w-[180px]">
                            <div className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-wider mb-1 flex items-center gap-1">
                                <span>Unrealized P/L</span>
                            </div>
                            <div className={`font-mono font-bold text-sm lg:text-base ${stats.unrealized >= 0 ? "text-red-400 drop-shadow-[0_0_3px_rgba(248,113,113,0.3)]" : "text-green-400 drop-shadow-[0_0_3px_rgba(74,222,128,0.3)]"}`}>
                                {stats.unrealized >= 0 ? "+" : ""}{formatCurrency(stats.unrealized)}
                                <span className="text-xs ml-1.5 opacity-80 font-normal">
                                    ({stats.unrealizedPct >= 0 ? "▲" : "▼"}{Math.abs(stats.unrealizedPct).toFixed(2)}%)
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Donut Chart Section */}
                {targets && targets.length > 0 && stats.marketValue > 0 && (
                    <div className="w-full lg:w-1/3 flex items-center lg:justify-end mt-4 lg:mt-0">
                        <div className="h-[120px] lg:h-[160px] w-full max-w-[200px]">
                            <ReactECharts
                                option={chartOptions}
                                notMerge={true}
                                style={{ height: '100%', width: '100%' }}
                                opts={{ renderer: 'svg' }}
                            />
                        </div>
                        <div className="flex flex-col gap-1 ml-4 justify-center">
                            <div className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Top Components</div>
                            {chartOptions.series?.[0].data?.slice(0, 3).map((item: any, idx: number) => (
                                <div key={idx} className="flex items-center gap-2 text-xs">
                                    <div className="w-2 h-2 rounded-full" style={{ backgroundColor: chartOptions.series?.[0].color[idx] }}></div>
                                    <span className="text-white w-14 truncate">{item.name}</span>
                                    <span className="text-[var(--color-text-muted)] font-mono ml-auto">
                                        {((item.value / stats.marketValue) * 100).toFixed(0)}%
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
