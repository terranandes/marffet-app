"use client";

import { useEffect, useState, useCallback, useRef } from "react";

import { PortfolioFactory, IPortfolioService, Group, Target, Transaction, Dividend } from "../../services/portfolioService";

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

    // Mobile Card View State
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

    const [dividendCash, setDividendCash] = useState({ total_cash: 0, dividend_count: 0 });
    const [syncing, setSyncing] = useState(false);

    // Request tracking to prevent race conditions on rapid group switches
    const fetchRequestIdRef = useRef(0);

    // Use relative paths (empty string) to proxy via Next.js rewrites
    // This ensures session cookies are passed correctly on Zeabur (cross-domain)
    const API_BASE = "";

    // Services
    const [service, setService] = useState<IPortfolioService | null>(null);
    const [isGuest, setIsGuest] = useState(false);

    // Initialize Service
    useEffect(() => {
        const initService = async () => {
            // Check auth by hitting a strictly protected endpoint.
            // GET /groups returns 200 [] for anon (legacy behavior), so it's unreliable.
            // GET /targets requires auth (401 if missing).
            try {
                const res = await fetch(`${API_BASE}/api/portfolio/targets?group_id=auth_check`, { credentials: "include" });
                if (res.status === 401 || res.status === 403) {
                    console.log("Unauthorized, using Guest Mode");
                    setService(PortfolioFactory.getService(false)); // Guest
                    setIsGuest(true);
                } else {
                    // 200, 404, 422 etc mean we are logged in (or at least passed auth middleware)
                    setService(PortfolioFactory.getService(true)); // API
                }
            } catch (e) {
                // Network error? Default to Guest?
                console.log("API Unreachable, using Guest Mode");
                setService(PortfolioFactory.getService(false));
                setIsGuest(true);
            }
        };
        initService();
    }, []);

    // Fetch groups
    const fetchGroups = useCallback(async () => {
        if (!service) return;
        setLoading(true);
        const data = await service.getGroups();
        setGroups(data);
        if (data.length > 0 && !selectedGroupId) {
            setSelectedGroupId(data[0].id);
        }
        setLoading(false);
    }, [service, selectedGroupId]);

    // Fetch targets with race condition prevention
    const fetchTargets = useCallback(async () => {
        if (!service || !selectedGroupId) return;

        // Increment request ID to track this specific request
        const requestId = ++fetchRequestIdRef.current;

        setLoading(true);
        const data = await service.getTargets(selectedGroupId);

        // Only update state if this is still the latest request
        if (requestId !== fetchRequestIdRef.current) {
            console.log(`[Portfolio] Discarding stale response for request ${requestId}`);
            return; // Stale request, discard
        }

        setTargets(data);
        setLoading(false);

        // Calculate stats
        let marketValue = 0;
        let realized = 0;
        let unrealized = 0;
        let totalCost = 0;

        data.forEach((t) => {
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
    }, [service, selectedGroupId]);

    // Fetch dividends
    const fetchDividends = useCallback(async () => {
        if (!service) return;
        const data = await service.getDividendStats();
        setDividendCash(data);
    }, [service]);

    useEffect(() => {
        if (service) {
            fetchGroups();
            fetchDividends();
        }
    }, [service, fetchGroups, fetchDividends]);

    useEffect(() => {
        if (service && selectedGroupId) {
            fetchTargets();
        }
    }, [service, selectedGroupId, fetchTargets]);

    // Actions
    const handleCreateGroup = async () => {
        if (!service || !newGroupName.trim()) return;
        const res = await service.createGroup(newGroupName);
        if (res) {
            setNewGroupName("");
            setShowAddGroup(false);
            fetchGroups();
        }
    };

    const handleDeleteGroup = async (groupId: string) => {
        if (!service || !confirm("Delete this group?")) return;
        if (await service.deleteGroup(groupId)) {
            if (selectedGroupId === groupId) setSelectedGroupId(null);
            fetchGroups();
        }
    };

    const handleAddTarget = async () => {
        if (!service || !selectedGroupId || !newTargetId.trim()) return;
        const res = await service.addTarget(selectedGroupId, newTargetId, newTargetName.trim() || "");
        if (res) {
            setNewTargetId("");
            setNewTargetName("");
            fetchTargets();
        }
    };

    const handleDeleteTarget = async (targetId: string) => {
        if (!service || !confirm("Delete this stock?")) return;
        if (await service.deleteTarget(targetId)) fetchTargets();
    };

    // Helper to refresh only one target's summary (Performance)
    const refreshSingleTarget = async (targetId: string) => {
        if (!service) return;
        const target = targets.find(t => t.id === targetId);
        // Pass current price if available to avoid refetching it inside service
        const currentPrice = target?.livePrice?.price;

        const newSummary = await service.getTargetSummary(targetId, currentPrice);

        if (newSummary) {
            setTargets(prev => prev.map(t =>
                t.id === targetId ? { ...t, summary: newSummary } : t
            ));
        }
    };

    const handleSaveTransaction = async (targetId: string) => {
        if (!service) return;
        const txData = editingTxId
            ? { id: editingTxId, ...newTx }
            : { target_id: targetId, ...newTx };

        if (await service.saveTransaction(txData)) {
            setShowTxForm(null);
            setEditingTxId(null);
            setNewTx({ type: "buy", shares: 0, price: 0, date: new Date().toISOString().split("T")[0] });
            // Refresh history
            if (showTxHistory) fetchTxHistory(showTxHistory);
            // Refresh summary for this target only (Fast)
            refreshSingleTarget(targetId);
        }
    };

    const handleSyncDividends = async () => {
        if (!service) return;
        setSyncing(true);
        await service.syncDividends();
        await fetchTargets();
        fetchDividends();
        setSyncing(false);
    };

    const fetchTxHistory = async (targetId: string) => {
        if (!service) return;
        const data = await service.getTransactions(targetId);
        setTxHistory(data);
        setShowTxHistory(targetId);
    };

    const fetchDivHistory = async (targetId: string, stockName: string) => {
        if (!service) return;
        const data = await service.getDividends(targetId);
        setDivHistory(data);
        setShowDivHistory({ targetId, stockName });
    };

    const handleDeleteTransaction = async (txId: string) => {
        if (!service || !confirm("Delete transaction?")) return;
        if (await service.deleteTransaction(txId)) {
            // Only refresh transaction history, NOT the full targets list
            if (showTxHistory) fetchTxHistory(showTxHistory);

            // We need targetId to refresh summary. 
            // In delete, we don't have it easily unless we look it up or pass it.
            // Assumption: User deletes from Modal where showTxHistory == targetId
            if (showTxHistory) refreshSingleTarget(showTxHistory);
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
                        <h1 className="text-2xl font-bold text-[var(--color-cta)] flex items-center gap-2">
                            📊 My Portfolio
                            {isGuest && (
                                <span className="text-xs bg-yellow-500/20 text-yellow-500 px-2 py-1 rounded border border-yellow-500/50">
                                    Guest Mode
                                </span>
                            )}
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

                {/* Group Tabs - Horizontal Scroll on Mobile, Wrap on Desktop */}
                <div className="flex gap-2 overflow-x-auto pb-2 flex-nowrap lg:flex-wrap no-scrollbar">
                    {groups.map((group) => (
                        <button
                            key={group.id}
                            onClick={() => setSelectedGroupId(group.id)}
                            className={`px-4 py-2 rounded-lg text-sm font-medium border transition cursor-pointer whitespace-nowrap shrink-0 ${selectedGroupId === group.id
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
                                        className={`font-mono font-bold text-lg lg:text-xl ${groupStats.realized >= 0 ? "text-red-400" : "text-green-400"
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
                                        className={`font-mono font-bold text-lg ${groupStats.unrealized >= 0 ? "text-red-400" : "text-green-400"
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

                    {/* MOBILE CARD VIEW (Phone/Tablet) - Collapsible */}
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
                                                    <span className="font-mono text-[var(--color-text-muted)]">
                                                        {target.livePrice?.price?.toLocaleString() || "-"}
                                                    </span>
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
                                                    <div className="text-right cursor-pointer" onClick={(e) => { e.stopPropagation(); fetchDivHistory(target.id, target.stock_name || target.id); }}>
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
                                                            setShowTxForm(target.id);
                                                            setEditingTxId(null);
                                                            setNewTx({ type: "buy", shares: 0, price: 0, date: new Date().toISOString().split("T")[0] });
                                                        }}
                                                        className="flex-1 bg-[var(--color-cta)]/20 text-[var(--color-cta)] py-2 rounded-lg hover:bg-[var(--color-cta)] hover:text-black transition text-sm font-bold"
                                                    >
                                                        ➕ Add Tx
                                                    </button>
                                                    <button
                                                        onClick={(e) => { e.stopPropagation(); fetchTxHistory(target.id); }}
                                                        className="flex-1 bg-white/10 text-white py-2 rounded-lg hover:bg-white/20 transition text-sm font-bold"
                                                    >
                                                        📜 History
                                                    </button>
                                                    <button
                                                        onClick={(e) => { e.stopPropagation(); handleDeleteTarget(target.id); }}
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

                    {/* Targets Table (Desktop) */}
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
                                            <td className="p-2 text-right cursor-pointer hover:bg-white/5 transition" onClick={() => fetchDivHistory(target.id, target.stock_name)}>
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
                            <div className="overflow-x-auto">
                                <table className="w-full text-sm min-w-[500px]">
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
                                                <td className={`p-2 font-bold ${tx.type === 'buy' ? 'text-red-400' : 'text-green-400'}`}>
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
                                                        className="text-[var(--color-cta)] hover:text-white hover:bg-[var(--color-cta)]/30 px-2 py-1 rounded transition-all duration-150 cursor-pointer hover:scale-110"
                                                        title="Edit transaction"
                                                    >
                                                        ✏️
                                                    </button>
                                                    <button
                                                        onClick={() => handleDeleteTransaction(tx.id)}
                                                        className="text-red-400 hover:text-white hover:bg-red-500/30 px-2 py-1 rounded transition-all duration-150 cursor-pointer hover:scale-110"
                                                        title="Delete transaction"
                                                    >
                                                        🗑
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
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
                                    ? "bg-red-500 text-white"
                                    : "bg-black/40 border border-white/20 text-white hover:bg-red-500/20"
                                    }`}
                            >
                                Buy
                            </button>
                            <button
                                onClick={() => setNewTx({ ...newTx, type: "sell" })}
                                className={`flex-1 py-3 rounded-lg font-bold text-sm transition ${newTx.type === "sell"
                                    ? "bg-green-500 text-black"
                                    : "bg-black/40 border border-white/20 text-white hover:bg-green-500/20"
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
