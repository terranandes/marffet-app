"use client";

import React, { useState } from "react";
import { Target } from "../../../services/portfolioService";
import { motion, AnimatePresence } from "framer-motion";
import { useLanguage } from "@/lib/i18n/LanguageContext";

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
    const { t } = useLanguage();
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

    const totalPortfolioValue = targets.reduce((sum, t) => sum + (t.summary?.market_value || 0), 0);

    const containerVariants = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: { staggerChildren: 0.05 }
        }
    };

    const itemVariants = {
        hidden: { opacity: 0, scale: 0.95, y: 10 },
        show: { opacity: 1, scale: 1, y: 0, transition: { type: "spring" as const, stiffness: 300, damping: 24 } }
    };

    return (
        <div className="md:hidden w-full">
            {targets.length === 0 ? (
                <div className="flex flex-col items-center justify-center text-[var(--color-text-muted)] py-12 bg-black/20 rounded-xl border border-white/5 border-dashed mt-4">
                    <span className="text-3xl mb-3">📈</span>
                    <span className="font-medium text-sm">{t('Portfolio.NoAssetsYet')}</span>
                    <span className="text-xs opacity-70 mt-1 max-w-[200px] text-center">{t('Portfolio.AddTickerToTrack')}</span>
                </div>
            ) : (
                <motion.div
                    className="space-y-3 mt-2"
                    variants={containerVariants}
                    initial="hidden"
                    animate="show"
                >
                    {targets.map((target) => {
                        const isExpanded = expandedTargets.has(target.id);
                        const weight = totalPortfolioValue > 0
                            ? ((target.summary?.market_value || 0) / totalPortfolioValue) * 100
                            : 0;

                        return (
                            <motion.div
                                key={target.id}
                                variants={itemVariants}
                                className="bg-black/40 border border-white/10 rounded-xl overflow-hidden transition-all duration-300 shadow-lg hover:border-cyan-500/20 group"
                            >
                                {/* Collapsed Header (Always Visible) - Click to Expand */}
                                <div
                                    onClick={() => toggleCard(target.id)}
                                    className="p-4 cursor-pointer active:bg-white/5 transition relative overflow-hidden"
                                >
                                    {/* Asset Weight Highlight Bar */}
                                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-cyan-400 to-blue-600 opacity-80" />

                                    {/* Row 1: Name + Market Value */}
                                    <div className="flex justify-between items-start mb-2.5">
                                        <div className="flex items-center gap-2 pl-2">
                                            <span className="font-bold text-base text-white">
                                                {target.stock_name || target.stock_id}
                                            </span>
                                            <span className="font-mono text-[10px] text-[var(--color-text-muted)] bg-white/5 px-1.5 py-[2px] rounded border border-white/10">
                                                {target.stock_id}
                                            </span>
                                        </div>
                                        <div className="text-right">
                                            <div className="font-mono font-bold text-white text-base drop-shadow-[0_0_5px_rgba(255,255,255,0.2)]">
                                                {formatCurrency(target.summary?.market_value || 0)}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Row 2: Price + Unrealized P/L (Compact) */}
                                    <div className="flex justify-between items-end text-sm pl-2">
                                        <div className="flex flex-col gap-0.5">
                                            <div className="flex items-center gap-1.5 font-mono text-white text-[13px]">
                                                {target.livePrice?.price ? (
                                                    <span className="font-bold">{target.livePrice.price.toLocaleString()}</span>
                                                ) : "---"}
                                                {target.livePrice && (
                                                    <span className={`text-[11px] font-semibold ${(target.livePrice.change || 0) >= 0 ? "text-red-400" : "text-green-400"}`}>
                                                        {(target.livePrice.change || 0) >= 0 ? "▲" : "▼"}
                                                        {Math.abs(target.livePrice.change_pct || 0).toFixed(2)}%
                                                    </span>
                                                )}
                                            </div>
                                            <div className="flex items-center gap-2 mt-1">
                                                <div className="h-1 w-16 bg-black/50 rounded-full overflow-hidden border border-white/5">
                                                    <div className="h-full bg-cyan-500 rounded-full" style={{ width: `${Math.min(weight, 100)}%` }} />
                                                </div>
                                                <div className="text-[10px] font-mono text-[var(--color-text-muted)] opacity-80">{weight.toFixed(1)}% weight</div>
                                            </div>
                                        </div>
                                        <div className="flex flex-col items-end">
                                            <div className={`font-mono font-bold text-[15px] ${(target.summary?.unrealized_pnl || 0) >= 0 ? "text-red-400 drop-shadow-[0_0_3px_rgba(248,113,113,0.3)]" : "text-green-400 drop-shadow-[0_0_3px_rgba(74,222,128,0.3)]"}`}>
                                                {(target.summary?.unrealized_pnl || 0) >= 0 ? "+" : ""}
                                                {formatCurrency(target.summary?.unrealized_pnl || 0)}
                                            </div>
                                            <div className={`text-[10px] font-mono mt-0.5 opacity-80 ${(target.summary?.unrealized_pnl_pct || 0) >= 0 ? "text-red-400" : "text-green-400"}`}>
                                                ({(target.summary?.unrealized_pnl_pct || 0) >= 0 ? "▲" : "▼"}
                                                {Math.abs(target.summary?.unrealized_pnl_pct || 0).toFixed(2)}%)
                                            </div>
                                        </div>
                                    </div>

                                    {/* Expand Indicator chevron */}
                                    <div className="absolute bottom-2 right-1/2 translate-x-1/2 opacity-30">
                                        <svg xmlns="http://www.w3.org/2000/svg" className={`h-4 w-4 transition-transform duration-300 ${isExpanded ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                        </svg>
                                    </div>
                                </div>

                                {/* Expanded Details (Animated) */}
                                <AnimatePresence>
                                    {isExpanded && (
                                        <motion.div
                                            initial={{ height: 0, opacity: 0 }}
                                            animate={{ height: "auto", opacity: 1 }}
                                            exit={{ height: 0, opacity: 0 }}
                                            className="overflow-hidden"
                                        >
                                            <div className="border-t border-white/10 bg-black/30 p-4 space-y-4">
                                                {/* Detail Grid */}
                                                <div className="grid grid-cols-2 gap-4 text-sm">
                                                    <div className="bg-white/5 rounded-lg p-2.5 border border-white/5">
                                                        <div className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-wider mb-1">{t('Portfolio.Position')}</div>
                                                        <div className="font-mono text-white font-medium">{target.summary?.total_shares || 0} <span className="text-[10px] opacity-60">{t('Portfolio.Shares')}</span></div>
                                                        <div className="font-mono text-[11px] text-[var(--color-text-muted)] mt-1">{t('Portfolio.Avg')}: ${target.summary?.avg_cost?.toFixed(2) || '0.00'}</div>
                                                    </div>
                                                    <div className="bg-white/5 rounded-lg p-2.5 border border-white/5 text-right">
                                                        <div className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-wider mb-1">{t('Portfolio.RealizedFlow')}</div>
                                                        <div className={`font-mono font-bold ${(target.summary?.realized_pnl || 0) >= 0 ? "text-red-400" : "text-green-400"}`}>
                                                            {(target.summary?.realized_pnl || 0) >= 0 ? "+" : ""}
                                                            {formatCurrency(target.summary?.realized_pnl || 0)} <span className="text-[10px] opacity-60 font-sans">P/L</span>
                                                        </div>
                                                        <div
                                                            className="font-mono text-amber-500 font-bold hover:text-amber-400 transition cursor-pointer mt-1 drop-shadow-[0_0_2px_rgba(245,158,11,0.2)]"
                                                            onClick={(e) => { e.stopPropagation(); onShowDividends(target.id, target.stock_id, target.stock_name || target.id); }}
                                                        >
                                                            {formatCurrency(target.summary?.total_dividend_cash || 0)} <span className="text-[10px] opacity-60 font-sans">{t('Portfolio.Div')} 📄</span>
                                                        </div>
                                                    </div>
                                                </div>
                                                {/* Action Buttons */}
                                                <div className="flex gap-2 pt-1">
                                                    <button
                                                        onClick={(e) => { e.stopPropagation(); onAddTransaction(target.id); }}
                                                        className="flex-1 bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 py-2.5 rounded-lg hover:bg-cyan-500/20 transition text-xs font-bold flex items-center justify-center gap-1.5"
                                                    >
                                                        <span className="text-sm">✚</span> Trade
                                                    </button>
                                                    <button
                                                        onClick={(e) => { e.stopPropagation(); onShowHistory(target.id); }}
                                                        className="flex-1 bg-white/5 text-white border border-white/10 py-2.5 rounded-lg hover:bg-white/10 transition text-xs font-bold flex items-center justify-center gap-1.5"
                                                    >
                                                        <span className="text-sm opacity-80">📜</span> History
                                                    </button>
                                                    <button
                                                        onClick={(e) => { e.stopPropagation(); onDelete(target.id); }}
                                                        className="bg-red-500/10 text-red-400 border border-red-500/20 px-4 py-2.5 rounded-lg hover:bg-red-500/20 transition flex items-center justify-center"
                                                    >
                                                        <span className="text-sm opacity-80">🗑️</span>
                                                    </button>
                                                </div>
                                            </div>
                                        </motion.div>
                                    )}
                                </AnimatePresence>
                            </motion.div>
                        );
                    })}
                </motion.div>
            )}
        </div>
    );
}
