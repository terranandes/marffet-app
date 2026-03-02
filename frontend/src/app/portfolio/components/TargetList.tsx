"use client";

import React, { useState } from "react";
import { Target } from "../../../services/portfolioService";
import { motion, AnimatePresence } from "framer-motion";
import { useLanguage } from "@/lib/i18n/LanguageContext";

interface TargetListProps {
    targets: Target[];
    onAddTransaction: (id: string) => void;
    onShowHistory: (id: string) => void;
    onDelete: (id: string) => void;
    onShowDividends: (targetId: string, stockId: string, stockName: string) => void;
    onAddTarget: (id: string, name: string) => void;
}

export function TargetList({
    targets,
    onAddTransaction,
    onShowHistory,
    onDelete,
    onShowDividends,
    onAddTarget
}: TargetListProps) {
    const { t } = useLanguage();
    const [newTargetId, setNewTargetId] = useState("");
    const [newTargetName, setNewTargetName] = useState("");
    const [activeDropdown, setActiveDropdown] = useState<string | null>(null);

    const formatCurrency = (val: number) => {
        return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(val);
    };

    const handleAdd = () => {
        if (!newTargetId.trim()) return;
        onAddTarget(newTargetId, newTargetName);
        setNewTargetId("");
        setNewTargetName("");
    };

    // Calculate total portfolio value to determine weights
    const totalPortfolioValue = targets.reduce((sum, t) => sum + (t.summary?.market_value || 0), 0);

    const containerVariants = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: { staggerChildren: 0.05 }
        }
    };

    const itemVariants = {
        hidden: { opacity: 0, y: 10 },
        show: { opacity: 1, y: 0, transition: { type: "spring" as const, stiffness: 300, damping: 24 } }
    };

    return (
        <div>
            {/* Add Target Form */}
            <div className="flex gap-2 mb-6 mt-4">
                <input
                    type="text"
                    value={newTargetId}
                    onChange={(e) => setNewTargetId(e.target.value)}
                    placeholder="Ticker (e.g. 2330)"
                    className="bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm w-36 focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 outline-none transition"
                />
                <input
                    type="text"
                    value={newTargetName}
                    onChange={(e) => setNewTargetName(e.target.value)}
                    placeholder="Name (e.g. 台積電)"
                    className="bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm flex-1 focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 outline-none transition"
                    onKeyDown={(e) => e.key === "Enter" && handleAdd()}
                />
                <button
                    onClick={handleAdd}
                    className="bg-cyan-500/10 text-cyan-400 hover:bg-cyan-500/20 hover:text-cyan-300 border border-cyan-500/20 px-4 py-2 rounded-lg text-sm font-bold cursor-pointer transition flex items-center gap-1"
                >
                    <span className="text-lg leading-none">+</span> Add Asset
                </button>
            </div>

            {targets.length === 0 && (
                <div className="hidden lg:flex flex-col items-center justify-center text-[var(--color-text-muted)] py-16 bg-black/20 rounded-xl border border-white/5 border-dashed">
                    <span className="text-3xl mb-3">📈</span>
                    <span className="font-medium">{t('Portfolio.NoAssetsYet')}</span>
                    <span className="text-xs opacity-70 mt-1">{t('Portfolio.AddTickerToTrack')}</span>
                </div>
            )}

            {targets.length > 0 && (
                <div className="hidden lg:block overflow-visible pb-12">
                    <table className="w-full text-sm border-collapse">
                        <thead>
                            <tr className="border-b border-white/10 text-[var(--color-text-muted)] text-[10px] uppercase tracking-wider bg-black/20">
                                <th className="text-left py-3 px-4 font-medium rounded-tl-lg">{t('Portfolio.Asset')}</th>
                                <th className="text-right py-3 px-4 font-medium">{t('Portfolio.Position')}</th>
                                <th className="text-right py-3 px-4 font-medium">{t('Portfolio.MarketPrice')}</th>
                                <th className="text-right py-3 px-4 font-medium w-48">{t('Portfolio.ValueWeight')}</th>
                                <th className="text-right py-3 px-4 font-medium">{t('Portfolio.UnrealizedPL')}</th>
                                <th className="text-right py-3 px-4 font-medium">{t('Portfolio.YieldFlow')}</th>
                                <th className="text-right py-3 px-4 font-medium rounded-tr-lg"></th>
                            </tr>
                        </thead>
                        <motion.tbody
                            className="divide-y divide-white/5 relative bg-black/20"
                            variants={containerVariants}
                            initial="hidden"
                            animate="show"
                        >
                            {targets.map((target) => {
                                const weight = totalPortfolioValue > 0
                                    ? ((target.summary?.market_value || 0) / totalPortfolioValue) * 100
                                    : 0;

                                return (
                                    <motion.tr
                                        key={target.id}
                                        variants={itemVariants}
                                        className="hover:bg-cyan-900/10 group transition duration-200"
                                        onMouseLeave={() => setActiveDropdown(null)}
                                    >
                                        <td className="py-3 px-4">
                                            <div className="font-bold text-white text-[15px]">{target.stock_name}</div>
                                            <div className="text-[10px] font-mono text-[var(--color-text-muted)] bg-white/5 inline-block px-1.5 py-[1px] rounded mt-1 border border-white/10">{target.stock_id}</div>
                                        </td>
                                        <td className="py-3 px-4 text-right">
                                            <div className="font-mono font-bold text-white">{target.summary?.total_shares || 0}</div>
                                            <div className="text-[11px] font-mono text-[var(--color-text-muted)] mt-0.5">@ {target.summary?.avg_cost?.toFixed(2) || "0.00"}</div>
                                        </td>
                                        <td className="py-3 px-4 text-right">
                                            <div className="flex items-center justify-end gap-1.5 font-mono font-bold">
                                                {target.livePrice?.price ? (
                                                    <span className="text-white drop-shadow-[0_0_5px_rgba(255,255,255,0.2)]">
                                                        {target.livePrice.price.toLocaleString()}
                                                    </span>
                                                ) : "---"}
                                            </div>
                                            {target.livePrice && (
                                                <div className={`text-[11px] font-mono mt-0.5 ${(target.livePrice.change || 0) >= 0 ? "text-red-400 drop-shadow-[0_0_2px_rgba(248,113,113,0.3)]" : "text-green-400 drop-shadow-[0_0_2px_rgba(74,222,128,0.3)]"}`}>
                                                    {(target.livePrice.change || 0) >= 0 ? "▲" : "▼"}
                                                    {Math.abs(target.livePrice.change || 0).toFixed(1)}
                                                    <span className="ml-1 opacity-80">({Math.abs(target.livePrice.change_pct || 0).toFixed(2)}%)</span>
                                                </div>
                                            )}
                                        </td>
                                        <td className="py-3 px-4 text-right">
                                            <div className="font-mono font-bold text-white tracking-tight">
                                                {formatCurrency(target.summary?.market_value || 0)}
                                            </div>
                                            <div className="flex items-center justify-end gap-2 mt-1.5">
                                                <div className="h-1.5 w-[84px] bg-black/40 rounded-full overflow-hidden border border-white/10">
                                                    <div
                                                        className="h-full bg-gradient-to-r from-cyan-600 to-cyan-400 rounded-full"
                                                        style={{ width: `${Math.min(weight, 100)}%` }}
                                                    />
                                                </div>
                                                <div className="text-[10px] font-mono text-[var(--color-text-muted)] w-8 text-right opacity-80">
                                                    {weight.toFixed(1)}%
                                                </div>
                                            </div>
                                        </td>
                                        <td className="py-3 px-4 text-right">
                                            <div className={`font-mono font-bold ${(target.summary?.unrealized_pnl || 0) >= 0 ? "text-red-400" : "text-green-400"}`}>
                                                {(target.summary?.unrealized_pnl || 0) >= 0 ? "+" : ""}
                                                {formatCurrency(target.summary?.unrealized_pnl || 0)}
                                            </div>
                                            <div className={`text-[11px] font-mono mt-0.5 opacity-80 ${(target.summary?.unrealized_pnl_pct || 0) >= 0 ? "text-red-400" : "text-green-400"}`}>
                                                ({(target.summary?.unrealized_pnl_pct || 0) >= 0 ? "▲" : "▼"}
                                                {Math.abs(target.summary?.unrealized_pnl_pct || 0).toFixed(2)}%)
                                            </div>
                                        </td>
                                        <td className="py-3 px-4 text-right">
                                            <div className={`font-mono font-semibold ${(target.summary?.realized_pnl || 0) >= 0 ? "text-red-400" : "text-green-400"}`}>
                                                {(target.summary?.realized_pnl || 0) >= 0 ? "+" : ""}
                                                {formatCurrency(target.summary?.realized_pnl || 0)} <span className="text-[10px] text-[var(--color-text-muted)] font-sans ml-0.5 opacity-60">P/L</span>
                                            </div>
                                            <div
                                                className="mt-0.5 font-mono text-amber-500 font-bold hover:text-amber-400 transition cursor-pointer flex items-center justify-end gap-1 drop-shadow-[0_0_2px_rgba(245,158,11,0.2)] group/div"
                                                onClick={() => onShowDividends(target.id, target.stock_id, target.stock_name || target.stock_id)}
                                            >
                                                {formatCurrency(target.summary?.total_dividend_cash || 0)}
                                                <span className="text-[10px] text-[var(--color-text-muted)] font-sans group-hover/div:text-amber-400 transition ml-0.5 opacity-60">{t('Portfolio.Div')}</span>
                                            </div>
                                        </td>
                                        <td className="py-3 px-4 text-right">
                                            <div className="flex items-center justify-end relative">
                                                <button
                                                    onClick={() => setActiveDropdown(activeDropdown === target.id ? null : target.id)}
                                                    className={`p-1.5 rounded-lg transition-all duration-200 ${activeDropdown === target.id
                                                        ? "bg-white/10 text-white"
                                                        : "text-white/30 hover:text-white/80 hover:bg-white/5 opacity-0 group-hover:opacity-100"
                                                        }`}
                                                >
                                                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h.01M12 12h.01M19 12h.01M6 12a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0z" />
                                                    </svg>
                                                </button>

                                                {/* Dropdown Menu */}
                                                <AnimatePresence>
                                                    {activeDropdown === target.id && (
                                                        <motion.div
                                                            initial={{ opacity: 0, scale: 0.95, y: -10 }}
                                                            animate={{ opacity: 1, scale: 1, y: 0 }}
                                                            exit={{ opacity: 0, scale: 0.95, y: -10 }}
                                                            transition={{ duration: 0.15 }}
                                                            className="absolute right-0 top-10 z-[100] w-48 bg-[#18181b] border border-white/10 rounded-xl shadow-2xl overflow-hidden py-1"
                                                        >
                                                            <button
                                                                onClick={(e) => { e.stopPropagation(); setActiveDropdown(null); onAddTransaction(target.id); }}
                                                                className="w-full text-left px-4 py-2.5 text-sm text-[var(--color-cta)] hover:bg-white/5 transition flex items-center gap-3 font-medium"
                                                            >
                                                                <span className="text-lg">✚</span> Add Transaction
                                                            </button>
                                                            <button
                                                                onClick={(e) => { e.stopPropagation(); setActiveDropdown(null); onShowHistory(target.id); }}
                                                                className="w-full text-left px-4 py-2.5 text-sm text-white hover:bg-white/5 transition flex items-center gap-3"
                                                            >
                                                                <span className="text-lg opacity-80">📜</span> Trade History
                                                            </button>
                                                            <div className="h-px bg-white/10 my-1 w-full" />
                                                            <button
                                                                onClick={(e) => { e.stopPropagation(); setActiveDropdown(null); onDelete(target.id); }}
                                                                className="w-full text-left px-4 py-2.5 text-sm text-red-400 hover:bg-red-400/10 transition flex items-center gap-3"
                                                            >
                                                                <span className="text-lg opacity-80">🗑</span> Remove Asset
                                                            </button>
                                                        </motion.div>
                                                    )}
                                                </AnimatePresence>
                                            </div>
                                        </td>
                                    </motion.tr>
                                );
                            })}
                        </motion.tbody>
                    </table>
                </div>
            )}
        </div>
    );
}
