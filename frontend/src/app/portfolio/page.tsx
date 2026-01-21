"use client";

import { useEffect, useState, useCallback } from "react";

interface Group {
    id: string;
    name: string;
}

interface Target {
    id: string;
    group_id: string;
    stock_id: string;
    stock_name: string;
    summary?: {
        total_shares: number;
        avg_cost: number;
        market_value: number;
        realized_pnl: number;
        unrealized_pnl: number;
        unrealized_pnl_pct: number;
        total_dividend_cash: number;
    };
    livePrice?: {
        price: number;
        change: number;
        change_pct: number;
    };
}

interface Transaction {
    id: string;
    target_id: string;
    type: "buy" | "sell";
    shares: number;
    price: number;
    date: string;
    fee?: number;
}

interface Dividend {
    id: string;
    target_id: string;
    ex_date: string;
    shares_held: number;
    amount_per_share: number;
    total_cash: number;
}

export default function PortfolioPage() {
    const [groups, setGroups] = useState<Group[]>([]);
    const [selectedGroupId, setSelectedGroupId] = useState<string | null>(null);
    const [targets, setTargets] = useState<Target[]>([]);
    const [loading, setLoading] = useState(true);

    // Forms
    const [showAddGroup, setShowAddGroup] = useState(false);
    const [newGroupName, setNewGroupName] = useState("");
    const [newTargetId, setNewTargetId] = useState("");
    const [newTargetName, setNewTargetName] = useState("");

    // Transaction form
    const [showTxForm, setShowTxForm] = useState<string | null>(null);
    const [editingTxId, setEditingTxId] = useState<string | null>(null); // Track ID if editing
    const [newTx, setNewTx] = useState({
        type: "buy" as "buy" | "sell",
        shares: 0,
        price: 0,
        date: new Date().toISOString().split("T")[0],
    });

    // Transaction history
    const [showTxHistory, setShowTxHistory] = useState<string | null>(null);
    const [txHistory, setTxHistory] = useState<Transaction[]>([]);

    // Dividend history
    const [showDivHistory, setShowDivHistory] = useState<{ targetId: string; stockName: string } | null>(null);
    const [divHistory, setDivHistory] = useState<Dividend[]>([]);

    // Stats
    const [groupStats, setGroupStats] = useState({
        marketValue: 0,
        realized: 0,
        unrealized: 0,
        unrealizedPct: 0,
    });

    const [dividendCash, setDividendCash] = useState({ total_cash: 0, dividend_count: 0 });
    const [syncing, setSyncing] = useState(false);

    const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

    // Fetch groups
    const fetchGroups = useCallback(async () => {
        try {
            const res = await fetch(`${API_BASE}/api/portfolio/groups`, { credentials: "include" });
            if (res.ok) {
                const data = await res.json();
                setGroups(data);
                if (data.length > 0 && !selectedGroupId) {
                    setSelectedGroupId(data[0].id);
                }
            }
        } catch (err) {
            console.error("Failed to fetch groups:", err);
        }
        setLoading(false);
    }, [selectedGroupId]);

    // Fetch targets for selected group (matches Legacy UI pattern)
    const fetchTargets = useCallback(async () => {
        if (!selectedGroupId) return;
        try {
            // Step 1: Get basic target list
            const res = await fetch(`${API_BASE}/api/portfolio/groups/${selectedGroupId}/targets`, {
                credentials: "include"
            });
            if (!res.ok) return;

            const targets = await res.json();

            // Step 2: Fetch live prices for all stocks
            const stockIds = targets.map((t: Target) => t.stock_id).join(',');
            let livePrices: Record<string, { price: number; change: number; change_pct: number }> = {};
            if (stockIds) {
                try {
                    const priceRes = await fetch(`${API_BASE}/api/portfolio/prices?stock_ids=${stockIds}`, {
                        credentials: "include"
                    });
                    if (priceRes.ok) {
                        livePrices = await priceRes.json();
                    }
                } catch (e) {
                    console.warn("Live price fetch failed:", e);
                }
            }

            // Step 3: Fetch summary for each target (with current_price for accurate P/L)
            for (const t of targets) {
                const livePrice = livePrices[t.stock_id]?.price || null;
                t.livePrice = livePrices[t.stock_id] || null;

                try {
                    const summaryUrl = livePrice
                        ? `${API_BASE}/api/portfolio/targets/${t.id}/summary?current_price=${livePrice}`
                        : `${API_BASE}/api/portfolio/targets/${t.id}/summary`;
                    const sumRes = await fetch(summaryUrl, { credentials: "include" });
                    if (sumRes.ok) {
                        t.summary = await sumRes.json();
                    }
                } catch (e) {
                    console.warn(`Summary fetch failed for ${t.stock_id}:`, e);
                }
            }

            setTargets(targets);

            // Calculate group stats from summaries
            let marketValue = 0;
            let realized = 0;
            let unrealized = 0;
            let totalCost = 0;

            targets.forEach((t: Target) => {
                marketValue += t.summary?.market_value || 0;
                realized += t.summary?.realized_pnl || 0;
                unrealized += t.summary?.unrealized_pnl || 0;
                totalCost += (t.summary?.avg_cost || 0) * (t.summary?.total_shares || 0);
            });

            setGroupStats({
                marketValue,
                realized,
                unrealized,
                unrealizedPct: totalCost > 0 ? (unrealized / totalCost) * 100 : 0,
            });
        } catch (err) {
            console.error("Failed to fetch targets:", err);
        }
    }, [selectedGroupId]);

    // Fetch dividend cash
    const fetchDividends = useCallback(async () => {
        try {
            const res = await fetch(`${API_BASE}/api/portfolio/dividends/total`, { credentials: "include" });
            if (res.ok) {
                const data = await res.json();
                setDividendCash(data);
            }
        } catch (err) {
            console.error("Failed to fetch dividends:", err);
        }
    }, []);

    useEffect(() => {
        fetchGroups();
        fetchDividends();
    }, [fetchGroups, fetchDividends]);

    useEffect(() => {
        fetchTargets();
    }, [selectedGroupId, fetchTargets]);

    // Create group
    const handleCreateGroup = async () => {
        if (!newGroupName.trim()) return;
        try {
            const res = await fetch(`${API_BASE}/api/portfolio/groups`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ name: newGroupName }),
            });
            if (res.ok) {
                setNewGroupName("");
                setShowAddGroup(false);
                fetchGroups();
            }
        } catch (err) {
            console.error("Failed to create group:", err);
        }
    };

    // Delete group
    const handleDeleteGroup = async (groupId: string) => {
        if (!confirm("Delete this group and all its contents?")) return;
        try {
            await fetch(`${API_BASE}/api/portfolio/groups/${groupId}`, {
                method: "DELETE",
                credentials: "include",
            });
            if (selectedGroupId === groupId) {
                setSelectedGroupId(null);
            }
            fetchGroups();
        } catch (err) {
            console.error("Failed to delete group:", err);
        }
    };

    // Add target
    const handleAddTarget = async () => {
        if (!selectedGroupId || !newTargetId.trim()) return;
        try {
            const res = await fetch(`${API_BASE}/api/portfolio/targets`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({
                    group_id: selectedGroupId,
                    stock_id: newTargetId,
                    stock_name: newTargetName.trim() || null,
                }),
            });
            if (res.ok) {
                setNewTargetId("");
                setNewTargetName("");
                fetchTargets();
            }
        } catch (err) {
            console.error("Failed to add target:", err);
        }
    };

    // Delete target
    const handleDeleteTarget = async (targetId: string) => {
        if (!confirm("Delete this stock from portfolio?")) return;
        try {
            await fetch(`${API_BASE}/api/portfolio/targets/${targetId}`, {
                method: "DELETE",
                credentials: "include",
            });
            fetchTargets();
        } catch (err) {
            console.error("Failed to delete target:", err);
        }
    };

    // Add/Update transaction
    const handleSaveTransaction = async (targetId: string) => {
        try {
            const isEdit = !!editingTxId;
            const url = isEdit
                ? `${API_BASE}/api/portfolio/transactions/${editingTxId}`
                : `${API_BASE}/api/portfolio/targets/${targetId}/transactions`;

            const method = isEdit ? "PUT" : "POST";
            const body = isEdit ? {
                type: newTx.type,
                shares: newTx.shares,
                price: newTx.price,
                date: newTx.date
            } : {
                target_id: targetId,
                ...newTx,
            };

            const res = await fetch(url, {
                method,
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify(body),
            });

            if (res.ok) {
                setShowTxForm(null);
                setEditingTxId(null);
                setNewTx({ type: "buy", shares: 0, price: 0, date: new Date().toISOString().split("T")[0] });

                // Refresh parent data
                fetchTargets();

                // Refresh history if open
                if (showTxHistory) {
                    fetchTxHistory(showTxHistory);
                }
            }
        } catch (err) {
            console.error("Failed to save transaction:", err);
        }
    };

    // Sync dividends
    const handleSyncDividends = async () => {
        setSyncing(true);
        try {
            await fetch(`${API_BASE}/api/portfolio/dividends/sync`, {
                method: "POST",
                credentials: "include",
            });
            await fetchTargets();
            fetchDividends();
        } catch (err) {
            console.error("Failed to sync dividends:", err);
        } finally {
            setSyncing(false);
        }
    };

    // Fetch transaction history
    const fetchTxHistory = async (targetId: string) => {
        try {
            const res = await fetch(`${API_BASE}/api/portfolio/targets/${targetId}/transactions`, {
                credentials: "include"
            });
            if (res.ok) {
                setTxHistory(await res.json());
                setShowTxHistory(targetId);
            }
        } catch (err) {
            console.error("Failed to fetch transactions:", err);
        }
    };

    // Fetch dividend history
    const fetchDivHistory = async (targetId: string, stockName: string) => {
        try {
            const res = await fetch(`${API_BASE}/api/portfolio/targets/${targetId}/dividends`, {
                credentials: "include"
            });
            if (res.ok) {
                setDivHistory(await res.json());
                setShowDivHistory({ targetId, stockName });
            }
        } catch (err) {
            console.error("Failed to fetch dividends:", err);
        }
    };

    // Delete transaction
    const handleDeleteTransaction = async (txId: string) => {
        if (!confirm("Delete this transaction?")) return;
        try {
            await fetch(`${API_BASE}/api/portfolio/transactions/${txId}`, {
                method: "DELETE",
                credentials: "include",
            });
            if (showTxHistory) fetchTxHistory(showTxHistory);
            fetchTargets();
        } catch (err) {
            console.error("Failed to delete transaction:", err);
        }
    };

    const formatCurrency = (val: number) => {
        return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(val);
    };

    return (
        <div className="max-w-6xl mx-auto space-y-6">
            {/* Header */}
            <div className="glass-card p-5 rounded-xl">
                <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center mb-4 gap-4">
                    <div>
                        <h1 className="text-2xl font-bold text-[var(--color-cta)]">
                            📊 My Portfolio
                        </h1>
                        <div className="text-sm text-[var(--color-text-muted)] mt-1">
                            💰 Dividend Cash:{" "}
                            <span className="text-[var(--color-success)] font-mono font-bold">
                                ${formatCurrency(dividendCash.total_cash)}
                            </span>
                            <span className="ml-2">({dividendCash.dividend_count} payments)</span>
                        </div>
                    </div>
                    <div className="flex gap-2 w-full lg:w-auto">
                        <button
                            onClick={handleSyncDividends}
                            disabled={syncing}
                            className={`flex-1 lg:flex-none border px-4 py-2 rounded transition text-sm font-bold cursor-pointer flex items-center justify-center gap-2 ${syncing
                                ? "bg-[var(--color-success)]/10 border-[var(--color-success)]/30 text-[var(--color-success)] cursor-not-allowed"
                                : "bg-[var(--color-success)]/20 border-[var(--color-success)] text-[var(--color-success)] hover:bg-[var(--color-success)] hover:text-black"
                                }`}
                        >
                            <span className={syncing ? "animate-spin" : ""}>{syncing ? "⏳" : "🔄"}</span>
                            <span>{syncing ? "Syncing..." : "Sync Dividends"}</span>
                        </button>
                        <button
                            onClick={() => setShowAddGroup(!showAddGroup)}
                            className="flex-1 lg:flex-none bg-[var(--color-cta)]/20 border border-[var(--color-cta)] text-[var(--color-cta)] px-4 py-2 rounded hover:bg-[var(--color-cta)] hover:text-black transition text-sm font-bold cursor-pointer"
                        >
                            + New Group
                        </button>
                    </div>
                </div>

                {/* Add Group Form */}
                {showAddGroup && (
                    <div className="mb-4 p-3 bg-black/30 rounded-lg flex gap-2">
                        <input
                            type="text"
                            value={newGroupName}
                            onChange={(e) => setNewGroupName(e.target.value)}
                            placeholder="Group name..."
                            className="bg-black/50 border border-[var(--color-border)] rounded px-3 py-2 text-sm flex-1 focus:border-[var(--color-cta)] outline-none"
                            onKeyDown={(e) => e.key === "Enter" && handleCreateGroup()}
                        />
                        <button
                            onClick={handleCreateGroup}
                            className="bg-[var(--color-cta)] text-black px-4 py-2 rounded text-sm font-bold cursor-pointer"
                        >
                            Create
                        </button>
                    </div>
                )}

                {/* Group Tabs */}
                <div className="flex gap-2 flex-wrap">
                    {groups.map((group) => (
                        <button
                            key={group.id}
                            onClick={() => setSelectedGroupId(group.id)}
                            className={`px-4 py-2 rounded-lg text-sm font-medium border transition cursor-pointer ${selectedGroupId === group.id
                                ? "bg-[var(--color-cta)] text-black border-[var(--color-cta)]"
                                : "border-[var(--color-border)] hover:border-[var(--color-cta)]"
                                }`}
                        >
                            {group.name}
                            <span
                                onClick={(e) => {
                                    e.stopPropagation();
                                    handleDeleteGroup(group.id);
                                }}
                                className="ml-2 text-[var(--color-danger)] hover:text-red-300 cursor-pointer"
                            >
                                ×
                            </span>
                        </button>
                    ))}
                    {groups.length === 0 && !loading && (
                        <span className="text-[var(--color-text-muted)] text-sm">
                            No groups yet. Create one to start tracking!
                        </span>
                    )}
                </div>
            </div>

            {/* Portfolio Content */}
            {selectedGroupId && (
                <div className="glass-card p-5 rounded-xl">
                    {/* Stats Summary */}
                    <div className="mb-6 bg-black/40 rounded-xl p-4 lg:p-6 border border-white/5">
                        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6">
                            <div>
                                <div className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mb-1">
                                    Market Value
                                </div>
                                <div className="font-mono font-bold text-3xl lg:text-4xl text-white">
                                    {formatCurrency(groupStats.marketValue)}
                                    <span className="text-base text-[var(--color-text-muted)] ml-2">TWD</span>
                                </div>
                            </div>
                            <div className="flex w-full lg:w-auto gap-4 lg:gap-12">
                                <div className="flex-1">
                                    <div className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mb-1">
                                        Realized P/L
                                    </div>
                                    <div
                                        className={`font-mono font-bold text-lg lg:text-xl ${groupStats.realized >= 0 ? "text-[var(--color-success)]" : "text-[var(--color-danger)]"
                                            }`}
                                    >
                                        {groupStats.realized >= 0 ? "+" : ""}
                                        {formatCurrency(groupStats.realized)}
                                    </div>
                                </div>
                                <div className="flex-1 text-right lg:text-left">
                                    <div className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mb-1">
                                        Unrealized P/L
                                    </div>
                                    <div
                                        className={`font-mono font-bold text-lg ${groupStats.unrealized >= 0 ? "text-[var(--color-success)]" : "text-[var(--color-danger)]"
                                            }`}
                                    >
                                        {groupStats.unrealized >= 0 ? "+" : ""}
                                        {formatCurrency(groupStats.unrealized)}
                                        <span className="text-sm ml-1">
                                            ({groupStats.unrealizedPct >= 0 ? "▲" : "▼"}
                                            {Math.abs(groupStats.unrealizedPct).toFixed(2)}%)
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

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
                        />
                        <button
                            onClick={handleAddTarget}
                            className="bg-[var(--color-primary)] text-black px-4 py-2 rounded text-sm font-bold cursor-pointer"
                        >
                            + Add Stock
                        </button>
                    </div>

                    {/* Targets Table */}
                    {targets.length === 0 ? (
                        <div className="text-center text-[var(--color-text-muted)] py-8">
                            No stocks in this group yet. Add one above!
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
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
                                                ${target.summary?.avg_cost?.toFixed(2) || "0.00"}
                                            </td>
                                            <td className="p-2 text-right font-mono font-bold text-white">
                                                {formatCurrency(target.summary?.market_value || 0)}
                                            </td>
                                            <td className={`p-2 text-right font-mono ${(target.summary?.realized_pnl || 0) >= 0
                                                ? "text-[var(--color-success)]"
                                                : "text-[var(--color-danger)]"
                                                }`}>
                                                {(target.summary?.realized_pnl || 0) >= 0 ? "+" : ""}
                                                {formatCurrency(target.summary?.realized_pnl || 0)}
                                            </td>
                                            <td className={`p-2 text-right font-mono font-bold ${(target.summary?.unrealized_pnl || 0) >= 0
                                                ? "text-[var(--color-success)]"
                                                : "text-[var(--color-danger)]"
                                                }`}>
                                                {(target.summary?.unrealized_pnl || 0) >= 0 ? "+" : ""}
                                                {formatCurrency(target.summary?.unrealized_pnl || 0)}
                                            </td>
                                            <td className="p-2 text-right">
                                                <div className="font-mono text-[var(--color-warning)] font-bold">
                                                    {formatCurrency(target.summary?.total_dividend_cash || 0)}
                                                </div>
                                                {(target.summary?.total_dividend_cash || 0) > 0 && (
                                                    <button
                                                        onClick={() => fetchDivHistory(target.id, target.stock_name)}
                                                        className="text-xs text-[var(--color-cta)] hover:underline cursor-pointer"
                                                    >
                                                        View Details
                                                    </button>
                                                )}
                                            </td>
                                            <td className="p-2 text-center">
                                                <div className="flex gap-1 justify-center">
                                                    <button
                                                        onClick={() => {
                                                            setShowTxForm(target.id);
                                                            setEditingTxId(null); // Ensure add mode
                                                            setNewTx({ type: "buy", shares: 0, price: 0, date: new Date().toISOString().split("T")[0] });
                                                        }}
                                                        className="bg-[var(--color-cta)]/20 text-[var(--color-cta)] px-2 py-1 rounded text-xs hover:bg-[var(--color-cta)] hover:text-black transition cursor-pointer"
                                                    >
                                                        +Tx
                                                    </button>
                                                    <button
                                                        onClick={() => fetchTxHistory(target.id)}
                                                        className="bg-purple-500/20 text-purple-400 px-2 py-1 rounded text-xs hover:bg-purple-500 hover:text-white transition cursor-pointer"
                                                    >
                                                        📜
                                                    </button>
                                                    <button
                                                        onClick={() => handleDeleteTarget(target.id)}
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
            )}

            {/* Empty State */}
            {!selectedGroupId && !loading && groups.length === 0 && (
                <div className="glass-card p-8 text-center">
                    <p className="text-6xl mb-4">📊</p>
                    <h2 className="text-2xl font-bold mb-2">Start Your Portfolio</h2>
                    <p className="text-[var(--color-text-muted)]">
                        Create a group above to start tracking your investments.
                    </p>
                </div>
            )}

            {/* Transaction History Modal */}
            {showTxHistory && (
                <div
                    className="fixed inset-0 bg-black/80 flex items-center justify-center z-50"
                    onClick={() => setShowTxHistory(null)}
                >
                    <div
                        className="bg-[#1a1a2e] p-6 rounded-xl border border-white/20 w-full max-w-2xl max-h-[80vh] overflow-auto"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="text-xl font-bold">📜 Transaction History</h3>
                            <button
                                onClick={() => {
                                    setShowTxForm(showTxHistory);
                                    setEditingTxId(null); // Ensure add mode
                                    setNewTx({ type: "buy", shares: 0, price: 0, date: new Date().toISOString().split("T")[0] });
                                }}
                                className="bg-[var(--color-cta)]/20 border border-[var(--color-cta)] text-[var(--color-cta)] px-3 py-1.5 rounded text-sm hover:bg-[var(--color-cta)] hover:text-black transition cursor-pointer"
                            >
                                + Add
                            </button>
                        </div>

                        {txHistory.length === 0 ? (
                            <p className="text-[var(--color-text-muted)] text-center py-8">
                                No transactions yet. Add one above!
                            </p>
                        ) : (
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="text-left text-[var(--color-text-muted)] text-xs uppercase border-b border-white/10">
                                        <th className="p-2">Date</th>
                                        <th className="p-2">Type</th>
                                        <th className="p-2 text-right">Shares</th>
                                        <th className="p-2 text-right">Price</th>
                                        <th className="p-2 text-right">Total</th>
                                        <th className="p-2 text-center">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-white/5">
                                    {txHistory.map((tx) => (
                                        <tr key={tx.id} className="hover:bg-white/5">
                                            <td className="p-2 font-mono text-xs">{tx.date}</td>
                                            <td className={`p-2 font-bold ${tx.type === 'buy' ? 'text-green-400' : 'text-red-400'}`}>
                                                {tx.type.toUpperCase()}
                                            </td>
                                            <td className="p-2 font-mono text-right">{tx.shares}</td>
                                            <td className="p-2 font-mono text-right">${tx.price}</td>
                                            <td className="p-2 font-mono text-right font-bold">
                                                ${(tx.shares * tx.price).toLocaleString()}
                                            </td>
                                            <td className="p-2 text-center">
                                                <button
                                                    onClick={() => {
                                                        setEditingTxId(tx.id);
                                                        setNewTx({
                                                            type: tx.type,
                                                            shares: tx.shares,
                                                            price: tx.price,
                                                            date: tx.date
                                                        });
                                                        setShowTxForm(tx.target_id);
                                                    }}
                                                    className="text-[var(--color-cta)] hover:text-white px-2"
                                                >
                                                    ✏️
                                                </button>
                                                <button
                                                    onClick={() => handleDeleteTransaction(tx.id)}
                                                    className="text-red-400 hover:text-red-300 px-2"
                                                >
                                                    🗑
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        )}
                        <div className="mt-4 flex justify-end">
                            <button
                                onClick={() => setShowTxHistory(null)}
                                className="px-4 py-2 border border-white/20 rounded hover:bg-white/10 transition cursor-pointer"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Add Transaction Modal Popup */}
            {showTxForm && (
                <div
                    className="fixed inset-0 bg-black/80 flex items-center justify-center z-[60]"
                    onClick={() => setShowTxForm(null)}
                >
                    <div
                        className="bg-[#1a1a2e] p-6 rounded-xl border border-white/20 w-full max-w-md"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
                            <span className="text-[var(--color-cta)]">{editingTxId ? "✏️" : "+"}</span>
                            {editingTxId ? "Edit Transaction" : "New Transaction"}
                        </h3>

                        {/* Buy/Sell Toggle */}
                        <div className="flex gap-2 mb-6">
                            <button
                                onClick={() => setNewTx({ ...newTx, type: "buy" })}
                                className={`flex-1 py-3 rounded-lg font-bold text-sm transition ${newTx.type === "buy"
                                    ? "bg-green-500 text-black"
                                    : "bg-black/40 border border-white/20 text-white hover:bg-green-500/20"
                                    }`}
                            >
                                Buy
                            </button>
                            <button
                                onClick={() => setNewTx({ ...newTx, type: "sell" })}
                                className={`flex-1 py-3 rounded-lg font-bold text-sm transition ${newTx.type === "sell"
                                    ? "bg-red-500 text-white"
                                    : "bg-black/40 border border-white/20 text-red-400 hover:bg-red-500/20"
                                    }`}
                            >
                                Sell
                            </button>
                        </div>

                        {/* Date */}
                        <div className="mb-4">
                            <label className="block text-xs text-[var(--color-text-muted)] mb-1">Date</label>
                            <div className="relative">
                                <input
                                    type="date"
                                    value={newTx.date}
                                    onChange={(e) => setNewTx({ ...newTx, date: e.target.value })}
                                    className="w-full bg-black/50 border border-white/20 rounded-lg px-4 py-3 text-sm focus:border-[var(--color-cta)] outline-none cursor-pointer [&::-webkit-calendar-picker-indicator]:opacity-100 [&::-webkit-calendar-picker-indicator]:cursor-pointer [&::-webkit-calendar-picker-indicator]:invert [&::-webkit-calendar-picker-indicator]:hover:scale-110 [&::-webkit-calendar-picker-indicator]:transition-transform"
                                />
                            </div>
                        </div>

                        {/* Shares & Price */}
                        <div className="grid grid-cols-2 gap-4 mb-6">
                            <div>
                                <label className="block text-xs text-[var(--color-text-muted)] mb-1">Shares</label>
                                <input
                                    type="number"
                                    value={newTx.shares || ""}
                                    onChange={(e) => setNewTx({ ...newTx, shares: Number(e.target.value) })}
                                    placeholder="0"
                                    className="w-full bg-black/50 border border-white/20 rounded-lg px-4 py-3 text-sm focus:border-[var(--color-cta)] outline-none"
                                />
                            </div>
                            <div>
                                <label className="block text-xs text-[var(--color-text-muted)] mb-1">Price</label>
                                <input
                                    type="number"
                                    value={newTx.price || ""}
                                    onChange={(e) => setNewTx({ ...newTx, price: Number(e.target.value) })}
                                    placeholder="0"
                                    className="w-full bg-black/50 border border-white/20 rounded-lg px-4 py-3 text-sm focus:border-[var(--color-cta)] outline-none"
                                />
                            </div>
                        </div>

                        {/* Buttons */}
                        <div className="flex gap-3">
                            <button
                                onClick={async () => {
                                    await handleSaveTransaction(showTxForm);
                                    // No need to manually refresh here as handleSaveTransaction does it
                                }}
                                className="flex-1 bg-[var(--color-cta)] text-black py-3 rounded-lg font-bold text-sm hover:opacity-90 transition cursor-pointer"
                            >
                                {editingTxId ? "Update" : "Confirm"}
                            </button>
                            <button
                                onClick={() => setShowTxForm(null)}
                                className="flex-1 border border-white/20 text-white py-3 rounded-lg font-bold text-sm hover:bg-white/10 transition cursor-pointer"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Dividend History Modal */}
            {showDivHistory && (
                <div
                    className="fixed inset-0 bg-black/80 flex items-center justify-center z-50"
                    onClick={() => setShowDivHistory(null)}
                >
                    <div
                        className="bg-[#1a1a2e] p-6 rounded-xl border border-white/20 w-full max-w-2xl max-h-[80vh] overflow-auto"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="text-xl font-bold">💰 Dividend Receipt - {showDivHistory.stockName}</h3>
                        </div>
                        {divHistory.length === 0 ? (
                            <p className="text-[var(--color-text-muted)] text-center py-8">
                                No dividend records found. Click "Sync Dividends" to fetch data.
                            </p>
                        ) : (
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="border-b border-[var(--color-border)] text-[var(--color-text-muted)]">
                                        <th className="text-left p-2">Ex-Date</th>
                                        <th className="text-right p-2">Shares Held</th>
                                        <th className="text-right p-2">$/Share</th>
                                        <th className="text-right p-2">Total Cash</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-[var(--color-border)]">
                                    {divHistory.map((div) => (
                                        <tr key={div.id} className="hover:bg-white/5">
                                            <td className="p-2">{div.ex_date}</td>
                                            <td className="p-2 font-mono text-right">{div.shares_held}</td>
                                            <td className="p-2 font-mono text-right">${div.amount_per_share?.toFixed(4)}</td>
                                            <td className="p-2 font-mono text-right font-bold text-[var(--color-warning)]">
                                                ${div.total_cash?.toLocaleString()}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                                <tfoot>
                                    <tr className="border-t border-[var(--color-border)] font-bold">
                                        <td colSpan={3} className="p-2 text-right">Total:</td>
                                        <td className="p-2 text-right text-[var(--color-warning)]">
                                            ${divHistory.reduce((sum, d) => sum + (d.total_cash || 0), 0).toLocaleString()}
                                        </td>
                                    </tr>
                                </tfoot>
                            </table>
                        )}
                        <div className="mt-4 flex justify-end">
                            <button
                                onClick={() => setShowDivHistory(null)}
                                className="px-4 py-2 border border-white/20 rounded hover:bg-white/10 transition cursor-pointer"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
