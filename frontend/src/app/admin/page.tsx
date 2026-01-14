"use client";

import { useEffect, useState, useCallback } from "react";

interface AdminMetrics {
    total_users: number;
    active_users_web: number;
    active_users_mobile: number;
    subscription_tiers: {
        free: number;
        premium: number;
        vip: number;
    };
}

interface FeedbackStats {
    new: number;
    reviewing: number;
    confirmed: number;
    fixed: number;
    wontfix: number;
}

interface FeedbackItem {
    id: number;
    feedback_type: string;
    feature_category: string;
    message: string;
    status: string;
    user_email?: string;
    created_at?: string;
    agent_notes?: string;
    showNotes?: boolean;
}

export default function AdminPage() {
    const [metrics, setMetrics] = useState<AdminMetrics | null>(null);
    const [loadingMetrics, setLoadingMetrics] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const [feedbackList, setFeedbackList] = useState<FeedbackItem[]>([]);
    const [feedbackStats, setFeedbackStats] = useState<FeedbackStats>({ new: 0, reviewing: 0, confirmed: 0, fixed: 0, wontfix: 0 });
    const [loadingFeedback, setLoadingFeedback] = useState(true);

    const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

    // Fetch Metrics
    const fetchMetrics = useCallback(async () => {
        setLoadingMetrics(true);
        setError(null);
        try {
            const res = await fetch(`${API_BASE}/api/admin/metrics`, { credentials: "include" });
            if (res.ok) {
                setMetrics(await res.json());
            } else if (res.status === 403 || res.status === 401) {
                setError("Access Denied: specialized Admin privileges required");
            } else {
                setError("Failed to fetch metrics");
            }
        } catch (err) {
            console.error("Metrics fetch error:", err);
            setError("Network error");
        }
        setLoadingMetrics(false);
    }, []);

    // Fetch Feedback
    const fetchFeedback = useCallback(async () => {
        setLoadingFeedback(true);
        try {
            const [listRes, statsRes] = await Promise.all([
                fetch(`${API_BASE}/api/feedback`, { credentials: "include" }),
                fetch(`${API_BASE}/api/feedback/stats`, { credentials: "include" })
            ]);

            if (listRes.ok) setFeedbackList(await listRes.json());
            if (statsRes.ok) setFeedbackStats(await statsRes.json());
        } catch (err) {
            console.error("Feedback fetch error:", err);
        }
        setLoadingFeedback(false);
    }, []);

    useEffect(() => {
        fetchMetrics();
        fetchFeedback();
    }, [fetchMetrics, fetchFeedback]);

    // Update Feedback Status
    const updateFeedbackStatus = async (id: number, status: string) => {
        try {
            await fetch(`${API_BASE}/api/feedback/${id}`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ status }),
                credentials: "include"
            });
            // Refresh stats
            const statsRes = await fetch(`${API_BASE}/api/feedback/stats`, { credentials: "include" });
            if (statsRes.ok) setFeedbackStats(await statsRes.json());

            // Update local list to reflect change if needed (though v-model usually handles it, here we might need to rely on re-fetch or just local state update if we want to be snappy)
            setFeedbackList(prev => prev.map(item => item.id === id ? { ...item, status } : item));
        } catch (err) {
            console.error("Update status error:", err);
        }
    };

    // Update Notes
    const updateFeedbackNotes = async (id: number, notes: string) => {
        try {
            await fetch(`${API_BASE}/api/feedback/${id}`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ agent_notes: notes }),
                credentials: "include"
            });
        } catch (err) {
            console.error("Update notes error:", err);
        }
    };

    // Copy Feedback
    const copyFeedback = (fb: FeedbackItem) => {
        const text = `## User Feedback Report
**ID:** ${fb.id}
**Type:** ${fb.feedback_type}
**Feature:** ${fb.feature_category}
**Status:** ${fb.status}
**From:** ${fb.user_email || 'Anonymous'}
**Date:** ${fb.created_at?.substring(0, 10)}

**Message:**
${fb.message}

---
Please analyze this feedback and determine if it's a true bug.`;

        navigator.clipboard.writeText(text).then(() => {
            alert("Feedback copied! Paste to AI agent for review.");
        }).catch(err => console.error("Copy failed:", err));
    };

    const getTypeColor = (type: string) => {
        if (type === "bug") return "bg-red-500/30 text-red-300";
        if (type === "suggestion") return "bg-blue-500/30 text-blue-300";
        return "bg-purple-500/30 text-purple-300";
    };

    const getTypeIcon = (type: string) => {
        if (type === "bug") return "🐛";
        if (type === "suggestion") return "💡";
        return "❓";
    };

    if (error) {
        return (
            <div className="flex items-center justify-center min-h-[50vh]">
                <div className="text-center text-[var(--color-danger)] p-8 glass-card rounded-xl">
                    <h2 className="text-2xl font-bold mb-2">Access Denied</h2>
                    <p>{error}</p>
                    <p className="text-sm text-[var(--color-text-muted)] mt-4">
                        This area is restricted to Game Masters (Admins).
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-5xl mx-auto space-y-8 pb-10">
            {/* Header */}
            <div className="glass-card p-6 rounded-xl border border-[var(--color-cta)]/20">
                <h1 className="text-2xl font-bold text-[var(--color-primary)] mb-6 flex items-center gap-2">
                    ⚡ GM Dashboard
                </h1>

                {loadingMetrics ? (
                    <div className="text-center py-10 animate-pulse text-[var(--color-cta)]">
                        Loading metrics...
                    </div>
                ) : metrics && (
                    <div className="space-y-6">
                        {/* User Metrics */}
                        <div>
                            <h3 className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mb-3">User Metrics</h3>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div className="bg-black/40 p-5 rounded-xl border border-white/10">
                                    <div className="text-xs text-[var(--color-text-muted)] mb-1">Total Registered Users</div>
                                    <div className="text-3xl font-bold text-purple-400">{metrics.total_users}</div>
                                </div>
                                <div className="bg-black/40 p-5 rounded-xl border border-white/10">
                                    <div className="text-xs text-[var(--color-text-muted)] mb-1">Active Users (Web)</div>
                                    <div className="text-3xl font-bold text-cyan-400">{metrics.active_users_web}</div>
                                    <div className="text-xs text-[var(--color-text-muted)] mt-1">Last 30 days</div>
                                </div>
                                <div className="bg-black/40 p-5 rounded-xl border border-white/10">
                                    <div className="text-xs text-[var(--color-text-muted)] mb-1">Active Users (Mobile)</div>
                                    <div className="text-3xl font-bold text-emerald-400">{metrics.active_users_mobile}</div>
                                    <div className="text-xs text-[var(--color-text-muted)] mt-1">Last 30 days</div>
                                </div>
                            </div>
                        </div>

                        {/* Subscription Breakdown */}
                        <div>
                            <h3 className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mb-3">Subscription Breakdown</h3>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div className="bg-black/40 p-5 rounded-xl border border-white/10">
                                    <div className="text-xs text-[var(--color-text-muted)] mb-1">Free Tier</div>
                                    <div className="text-3xl font-bold text-[var(--color-text-muted)]">
                                        {metrics.subscription_tiers?.free || 0}
                                    </div>
                                </div>
                                <div className="bg-black/40 p-5 rounded-xl border border-white/10">
                                    <div className="text-xs text-[var(--color-text-muted)] mb-1">Premium Tier</div>
                                    <div className="text-3xl font-bold text-[var(--color-primary)]">
                                        {metrics.subscription_tiers?.premium || 0}
                                    </div>
                                </div>
                                <div className="bg-black/40 p-5 rounded-xl border border-white/10">
                                    <div className="text-xs text-[var(--color-text-muted)] mb-1">VIP Tier</div>
                                    <div className="text-3xl font-bold text-pink-400">
                                        {metrics.subscription_tiers?.vip || 0}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Feedback Panel */}
            <div className="glass-card p-6 rounded-xl border border-[var(--color-border)]">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-sm text-[var(--color-text-muted)] uppercase tracking-wider">
                        User Feedback & Bug Reports
                    </h3>
                    <button
                        onClick={fetchFeedback}
                        className="text-xs text-[var(--color-cta)] hover:text-white transition"
                    >
                        🔄 Refresh
                    </button>
                </div>

                {/* Feedback Stats */}
                <div className="grid grid-cols-5 gap-2 mb-4">
                    <div className="bg-red-500/20 p-2 rounded text-center">
                        <div className="text-lg font-bold text-red-400">{feedbackStats.new || 0}</div>
                        <div className="text-xs text-[var(--color-text-muted)]">New</div>
                    </div>
                    <div className="bg-yellow-500/20 p-2 rounded text-center">
                        <div className="text-lg font-bold text-yellow-400">{feedbackStats.reviewing || 0}</div>
                        <div className="text-xs text-[var(--color-text-muted)]">Reviewing</div>
                    </div>
                    <div className="bg-blue-500/20 p-2 rounded text-center">
                        <div className="text-lg font-bold text-blue-400">{feedbackStats.confirmed || 0}</div>
                        <div className="text-xs text-[var(--color-text-muted)]">Confirmed</div>
                    </div>
                    <div className="bg-green-500/20 p-2 rounded text-center">
                        <div className="text-lg font-bold text-green-400">{feedbackStats.fixed || 0}</div>
                        <div className="text-xs text-[var(--color-text-muted)]">Fixed</div>
                    </div>
                    <div className="bg-gray-500/20 p-2 rounded text-center">
                        <div className="text-lg font-bold text-gray-400">{feedbackStats.wontfix || 0}</div>
                        <div className="text-xs text-[var(--color-text-muted)]">Won't Fix</div>
                    </div>
                </div>

                {/* Feedback List */}
                <div className="bg-black/40 rounded-xl border border-white/10 max-h-96 overflow-y-auto">
                    {loadingFeedback ? (
                        <div className="p-4 text-center text-[var(--color-text-muted)] animate-pulse">
                            Loading feedback...
                        </div>
                    ) : feedbackList.length === 0 ? (
                        <div className="p-4 text-center text-[var(--color-text-muted)]">
                            No feedback reports yet
                        </div>
                    ) : (
                        feedbackList.map((fb) => (
                            <div key={fb.id} className="p-4 border-b border-white/5 hover:bg-white/5 transition">
                                <div className="flex justify-between items-start mb-2">
                                    <div>
                                        <span className={`text-xs px-2 py-1 rounded mr-2 ${getTypeColor(fb.feedback_type)}`}>
                                            {getTypeIcon(fb.feedback_type)} {fb.feedback_type}
                                        </span>
                                        <span className="text-xs text-[var(--color-text-muted)]">{fb.feature_category}</span>
                                    </div>
                                    <span className="text-xs text-[var(--color-text-muted)]">
                                        {fb.created_at?.substring(0, 10)}
                                    </span>
                                </div>
                                <p className="text-sm text-gray-300 mb-2">{fb.message}</p>
                                <div className="flex items-center gap-2 text-xs flex-wrap">
                                    <span className="text-[var(--color-text-muted)]">
                                        From: {fb.user_email || "Anonymous"}
                                    </span>
                                    <button
                                        onClick={() => copyFeedback(fb)}
                                        className="text-[var(--color-cta)] hover:text-white transition flex items-center gap-1"
                                        title="Copy to clipboard for AI review"
                                    >
                                        📋 Copy
                                    </button>
                                    <select
                                        value={fb.status}
                                        onChange={(e) => updateFeedbackStatus(fb.id, e.target.value)}
                                        className="ml-auto bg-gray-800 border border-gray-700 rounded px-2 py-1 text-xs text-white outline-none focus:border-[var(--color-cta)]"
                                    >
                                        <option value="new">🔴 New</option>
                                        <option value="reviewing">🟡 Reviewing</option>
                                        <option value="confirmed">🔵 Confirmed</option>
                                        <option value="fixed">🟢 Fixed</option>
                                        <option value="wontfix">⚫ Won't Fix</option>
                                    </select>
                                </div>

                                {/* Agent Notes */}
                                {(fb.agent_notes || fb.showNotes) ? (
                                    <div className="mt-2 text-right">
                                        <textarea
                                            defaultValue={fb.agent_notes}
                                            rows={2}
                                            className="w-full bg-gray-800 border border-gray-700 rounded px-2 py-1 text-xs text-gray-300 outline-none focus:border-[var(--color-cta)]"
                                            placeholder="AI agent notes..."
                                            onBlur={(e) => updateFeedbackNotes(fb.id, e.target.value)}
                                        />
                                    </div>
                                ) : (
                                    <button
                                        onClick={() => setFeedbackList(prev => prev.map(item => item.id === fb.id ? { ...item, showNotes: true } : item))}
                                        className="mt-1 text-xs text-[var(--color-text-muted)] hover:text-[var(--color-cta)] transition"
                                    >
                                        + Add AI notes
                                    </button>
                                )}
                            </div>
                        ))
                    )}
                </div>

                <div className="text-xs text-[var(--color-text-muted)] text-center mt-6">
                    Admin access only • {new Date().getFullYear()} Martian Investment
                </div>
            </div>
        </div>
    );
}
