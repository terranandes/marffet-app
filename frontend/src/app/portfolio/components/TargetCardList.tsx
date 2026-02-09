import React, { useState } from "react";
import { Target } from "../../../services/portfolioService";

interface TargetCardListProps {
    targets: Target[];
    onAddTransaction: (id: string) => void;
    onShowHistory: (id: string) => void;
    onDelete: (id: string) => void;
    onShowDividends: (targetId: string, stockId: string, stockName: string) => void;
}

export function TargetCardList({
    targets,
    onAddTransaction,
    onShowHistory,
    onDelete,
    onShowDividends
}: TargetCardListProps) {
    const [expandedTargets, setExpandedTargets] = useState<Set<string>>(new Set());

    const toggleCard = (id: string) => {
        const newSet = new Set(expandedTargets);
        if (newSet.has(id)) {
            newSet.delete(id);
        } else {
            newSet.add(id);
        }
        setExpandedTargets(newSet);
    };

    const formatCurrency = (val: number) => {
        return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(val);
    };

    return (
        <div className="lg:hidden space-y-3">
            {targets.length === 0 ? (
                <div className="text-center text-[var(--color-text-muted)] py-8">
                    No stocks in this group yet. Add one above!
                </div>
            ) : (
                targets.map((target) => {
                    const isExpanded = expandedTargets.has(target.id);
                    return (
                        <div key={target.id} className="bg-white/5 border border-white/10 rounded-xl overflow-hidden transition">
                            {/* Collapsed Header (Always Visible) - Click to Expand */}
                            <div
                                onClick={() => toggleCard(target.id)}
                                className="p-4 cursor-pointer active:bg-white/10 transition"
                            >
                                {/* Row 1: Name + Market Value */}
                                <div className="flex justify-between items-start mb-2">
                                    <div className="flex items-center gap-2">
                                        <span className="font-bold text-base text-white">
                                            {target.stock_name || target.stock_id}
                                        </span>
                                        <span className="text-xs text-gray-400 bg-black/30 px-1.5 py-0.5 rounded">
                                            {target.stock_id}
                                        </span>
                                    </div>
                                    <div className="text-right">
                                        <div className="font-mono font-bold text-white">
                                            {formatCurrency(target.summary?.market_value || 0)}
                                        </div>
                                    </div>
                                </div>
                                {/* Row 2: Price + Unrealized P/L (Compact) */}
                                <div className="flex justify-between items-center text-sm">
                                    <div className="flex items-center gap-2">
                                        <div className="flex items-center gap-1.5 font-mono text-[var(--color-text-muted)]">
                                            {target.livePrice?.price ? (
                                                <>
                                                    <span className="relative flex h-1.5 w-1.5">
                                                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                                                        <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-green-500"></span>
                                                    </span>
                                                    <span className="text-white font-bold">{target.livePrice.price.toLocaleString()}</span>
                                                </>
                                            ) : (
                                                "-"
                                            )}
                                        </div>
                                        {target.livePrice && (
                                            <span className={`text-xs ${(target.livePrice.change || 0) >= 0 ? "text-red-400" : "text-green-400"}`}>
                                                {(target.livePrice.change || 0) >= 0 ? "▲" : "▼"}
                                                {Math.abs(target.livePrice.change_pct || 0).toFixed(2)}%
                                            </span>
                                        )}
                                    </div>
                                    <div
                                        className={`font-mono font-bold ${(target.summary?.unrealized_pnl || 0) >= 0 ? "text-red-400" : "text-green-400"}`}
                                    >
                                        {(target.summary?.unrealized_pnl || 0) >= 0 ? "+" : ""}
                                        {formatCurrency(target.summary?.unrealized_pnl || 0)}
                                    </div>
                                </div>
                                {/* Expand Indicator */}
                                <div className="text-center text-[var(--color-text-muted)] text-xs mt-2">
                                    {isExpanded ? '▲ Collapse' : '▼ Tap for Details'}
                                </div>
                            </div>

                            {/* Expanded Details (Conditionally Visible) */}
                            {isExpanded && (
                                <div className="border-t border-white/10 bg-black/20 p-4 space-y-3">
                                    {/* Detail Grid */}
                                    <div className="grid grid-cols-2 gap-3 text-sm">
                                        <div>
                                            <div className="text-xs text-[var(--color-text-muted)]">Shares</div>
                                            <div className="font-mono">{target.summary?.total_shares || 0}</div>
                                        </div>
                                        <div className="text-right">
                                            <div className="text-xs text-[var(--color-text-muted)]">Avg Cost</div>
                                            <div className="font-mono">${target.summary?.avg_cost?.toFixed(2) || '0.00'}</div>
                                        </div>
                                        <div>
                                            <div className="text-xs text-[var(--color-text-muted)]">Realized P/L</div>
                                            <div className={`font-mono ${(target.summary?.realized_pnl || 0) >= 0 ? "text-red-400" : "text-green-400"}`}>
                                                {(target.summary?.realized_pnl || 0) >= 0 ? "+" : ""}
                                                {formatCurrency(target.summary?.realized_pnl || 0)}
                                            </div>
                                        </div>
                                        <div className="text-right cursor-pointer" onClick={(e) => { e.stopPropagation(); onShowDividends(target.id, target.stock_id, target.stock_name || target.id); }}>
                                            <div className="text-xs text-[var(--color-warning)]">💰 Div. Receipt</div>
                                            <div className="font-mono text-[var(--color-warning)] font-bold hover:text-white transition">
                                                {formatCurrency(target.summary?.total_dividend_cash || 0)}
                                            </div>
                                        </div>
                                    </div>
                                    {/* Action Buttons */}
                                    <div className="flex gap-2 pt-2 border-t border-white/5">
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                onAddTransaction(target.id);
                                            }}
                                            className="flex-1 bg-[var(--color-cta)]/20 text-[var(--color-cta)] py-2 rounded-lg hover:bg-[var(--color-cta)] hover:text-black transition text-sm font-bold"
                                        >
                                            ➕ Add Tx
                                        </button>
                                        <button
                                            onClick={(e) => { e.stopPropagation(); onShowHistory(target.id); }}
                                            className="flex-1 bg-white/10 text-white py-2 rounded-lg hover:bg-white/20 transition text-sm font-bold"
                                        >
                                            📜 History
                                        </button>
                                        <button
                                            onClick={(e) => { e.stopPropagation(); onDelete(target.id); }}
                                            className="bg-[var(--color-danger)]/10 text-[var(--color-danger)] px-4 py-2 rounded-lg hover:bg-[var(--color-danger)] hover:text-white transition text-sm font-bold"
                                        >
                                            🗑️
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>
                    );
                })
            )}
        </div>
    );
}
