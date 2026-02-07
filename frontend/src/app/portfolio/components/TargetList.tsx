import React, { useState } from "react";
import { Target } from "../../../services/portfolioService";

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
    const [newTargetId, setNewTargetId] = useState("");
    const [newTargetName, setNewTargetName] = useState("");

    const formatCurrency = (val: number) => {
        return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(val);
    };

    const handleAdd = () => {
        onAddTarget(newTargetId, newTargetName);
        setNewTargetId("");
        setNewTargetName("");
    };

    return (
        <div>
            {/* Add Target Form */}
            <div className="flex gap-2 mb-4">
                <input
                    type="text"
                    value={newTargetId}
                    onChange={(e) => setNewTargetId(e.target.value)}
                    placeholder="Stock ID (e.g. 2330)"
                    className="bg-black/50 border border-[var(--color-border)] rounded px-3 py-2 text-sm w-32 focus:border-[var(--color-cta)] outline-none"
                />
                <input
                    type="text"
                    value={newTargetName}
                    onChange={(e) => setNewTargetName(e.target.value)}
                    placeholder="Name (e.g. 台積電)"
                    className="bg-black/50 border border-[var(--color-border)] rounded px-3 py-2 text-sm flex-1 focus:border-[var(--color-cta)] outline-none"
                    onKeyDown={(e) => e.key === "Enter" && handleAdd()}
                />
                <button
                    onClick={handleAdd}
                    className="bg-[var(--color-primary)] text-black px-4 py-2 rounded text-sm font-bold cursor-pointer"
                >
                    + Add Stock
                </button>
            </div>

            {targets.length === 0 && (
                <div className="hidden lg:block text-center text-[var(--color-text-muted)] py-8">
                    No stocks in this group yet. Add one above!
                </div>
            )}

            {targets.length > 0 && (
                <div className="hidden lg:block overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-[var(--color-border)] text-[var(--color-text-muted)] text-xs uppercase">
                                <th className="text-left p-2">Stock</th>
                                <th className="text-right p-2">Price/Change</th>
                                <th className="text-right p-2">Shares</th>
                                <th className="text-right p-2">Cost/Avg</th>
                                <th className="text-right p-2">Market Val</th>
                                <th className="text-right p-2">Realized</th>
                                <th className="text-right p-2">Unrealized</th>
                                <th className="text-right p-2">Div. Receipt</th>
                                <th className="text-center p-2">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-[var(--color-border)]">
                            {targets.map((target) => (
                                <tr key={target.id} className="hover:bg-white/5">
                                    <td className="p-2">
                                        <div className="font-bold text-white">{target.stock_name}</div>
                                        <div className="text-xs text-[var(--color-text-muted)]">{target.stock_id}</div>
                                    </td>
                                    <td className="p-2 text-right">
                                        <div className="font-mono font-bold">
                                            {target.livePrice?.price?.toLocaleString() || "---"}
                                        </div>
                                        {target.livePrice && (
                                            <div className={`text-xs font-mono ${(target.livePrice.change || 0) >= 0 ? "text-red-400" : "text-green-400"}`}>
                                                {(target.livePrice.change || 0) >= 0 ? "▲" : "▼"}
                                                {Math.abs(target.livePrice.change || 0).toFixed(1)}
                                                ({Math.abs(target.livePrice.change_pct || 0).toFixed(2)}%)
                                            </div>
                                        )}
                                    </td>
                                    <td className="p-2 text-right font-mono">
                                        {target.summary?.total_shares || 0}
                                    </td>
                                    <td className="p-2 text-right font-mono">
                                        {target.summary?.avg_cost?.toFixed(2) || "0.00"}
                                    </td>
                                    <td className="p-2 text-right font-mono font-bold text-white">
                                        {formatCurrency(target.summary?.market_value || 0)}
                                    </td>
                                    <td className={`p-2 text-right font-mono ${(target.summary?.realized_pnl || 0) >= 0
                                        ? "text-red-400"
                                        : "text-green-400"
                                        }`}>
                                        {(target.summary?.realized_pnl || 0) >= 0 ? "+" : ""}
                                        {formatCurrency(target.summary?.realized_pnl || 0)}
                                    </td>
                                    <td className={`p-2 text-right ${(target.summary?.unrealized_pnl || 0) >= 0
                                        ? "text-red-400"
                                        : "text-green-400"
                                        }`}>
                                        <div className="font-mono font-bold">
                                            {(target.summary?.unrealized_pnl || 0) >= 0 ? "+" : ""}
                                            {formatCurrency(target.summary?.unrealized_pnl || 0)}
                                        </div>
                                        <div className="text-xs">
                                            ({(target.summary?.unrealized_pnl_pct || 0).toFixed(2)}%)
                                        </div>
                                    </td>
                                    <td className="p-2 text-right cursor-pointer hover:bg-white/5 transition" onClick={() => onShowDividends(target.id, target.stock_id, target.stock_name || target.stock_id)}>
                                        <div className="font-mono text-[var(--color-warning)] font-bold hover:text-white transition">
                                            {formatCurrency(target.summary?.total_dividend_cash || 0)}
                                        </div>
                                        <div className="text-xs text-[var(--color-cta)] hover:underline">
                                            View Details 📄
                                        </div>
                                    </td>
                                    <td className="p-2 text-center">
                                        <div className="flex gap-1 justify-center">
                                            <button
                                                onClick={() => onAddTransaction(target.id)}
                                                className="bg-[var(--color-cta)]/20 text-[var(--color-cta)] px-2 py-1 rounded text-xs hover:bg-[var(--color-cta)] hover:text-black transition cursor-pointer"
                                            >
                                                +Tx
                                            </button>
                                            <button
                                                onClick={() => onShowHistory(target.id)}
                                                className="bg-purple-500/20 text-purple-400 px-2 py-1 rounded text-xs hover:bg-purple-500 hover:text-white transition cursor-pointer"
                                            >
                                                📜
                                            </button>
                                            <button
                                                onClick={() => onDelete(target.id)}
                                                className="bg-[var(--color-danger)]/20 text-[var(--color-danger)] px-2 py-1 rounded text-xs hover:bg-[var(--color-danger)] hover:text-white transition cursor-pointer"
                                            >
                                                🗑
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}
