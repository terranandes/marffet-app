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

interface CrawlerStatus {
    is_running: boolean;
    last_run_time: string | null;
    status: string;
    message: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function AdminPage() {
    const [metrics, setMetrics] = useState<AdminMetrics | null>(null);
    const [loadingMetrics, setLoadingMetrics] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const [feedbackList, setFeedbackList] = useState<FeedbackItem[]>([]);
    const [feedbackStats, setFeedbackStats] = useState<FeedbackStats>({ new: 0, reviewing: 0, confirmed: 0, fixed: 0, wontfix: 0 });
    const [loadingFeedback, setLoadingFeedback] = useState(true);

    // Crawler Status
    const [crawlerStatus, setCrawlerStatus] = useState<CrawlerStatus | null>(null);

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
        } catch {
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
        } catch {
            console.error("Feedback fetch error");
        }
        setLoadingFeedback(false);
    }, []);

    // Fetch Crawler Status
    const fetchCrawlerStatus = useCallback(async () => {
        try {
            const res = await fetch(`${API_BASE}/api/admin/crawl/status?key=secret`, { credentials: "include" });
            if (res.ok) {
                setCrawlerStatus(await res.json());
            }
        } catch {
            console.error("Crawler status fetch error");
        }
    }, []);

    useEffect(() => {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        fetchMetrics();
        fetchFeedback();
        fetchCrawlerStatus();
        const interval = setInterval(fetchCrawlerStatus, 5000);
        return () => clearInterval(interval);
    }, [fetchMetrics, fetchFeedback, fetchCrawlerStatus]);

    // Update Feedback Status
    const updateFeedbackStatus = async (id: number, status: string) => {
        try {
            await fetch(`${API_BASE}/api/feedback/${id}`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ status }),
                credentials: "include"
            });
            const statsRes = await fetch(`${API_BASE}/api/feedback/stats`, { credentials: "include" });
            if (statsRes.ok) setFeedbackStats(await statsRes.json());
            const listRes = await fetch(`${API_BASE}/api/feedback`, { credentials: "include" });
            if (listRes.ok) setFeedbackList(await listRes.json());
        } catch { alert("Failed to update status"); }
    };

    // Update Feedback Notes
    const updateFeedbackNotes = async (id: number, notes: string) => {
        try {
            await fetch(`${API_BASE}/api/feedback/${id}`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ agent_notes: notes }),
                credentials: "include"
            });
        } catch { console.error("Failed to update notes"); }
    };

    // Helper functions
    const getTypeColor = (type: string) => {
        switch (type) {
            case 'bug': return 'bg-red-900/50 text-red-200 border border-red-800';
            case 'feature': return 'bg-blue-900/50 text-blue-200 border border-blue-800';
            case 'content': return 'bg-green-900/50 text-green-200 border border-green-800';
            default: return 'bg-gray-800 text-gray-300 border border-gray-700';
        }
    };

    const getTypeIcon = (type: string) => {
        switch (type) {
            case 'bug': return '🐛';
            case 'feature': return '✨';
            case 'content': return '📝';
            default: return '🗨️';
        }
    };

    const copyFeedback = (item: FeedbackItem) => {
        const text = `[${item.feedback_type.toUpperCase()}] ${item.feature_category}\nFrom: ${item.user_email || 'Anon'}\nMessage: ${item.message}\n(ID: ${item.id})`;
        navigator.clipboard.writeText(text);
        alert("Copied to clipboard!");
    };

    // Handle Crawl Trigger
    const handleCrawl = async (force: boolean) => {
        const endpoint = `${API_BASE}/api/admin/crawl?key=secret&force=${force}`;
        try {
            const res = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
            });
            const data = await res.json();
            if (res.ok) {
                alert(`✅ Crawl initiated! ${data.message}`);
                fetchCrawlerStatus(); // Refresh status immediately
            } else {
                alert(`❌ Crawl failed: ${data.error || data.message}`);
            }
        } catch {
            alert('❌ Network error during crawl initiation.');
        }
    };

    if (loadingMetrics) return <div className="p-8 text-[var(--color-text-muted)] animate-pulse">Loading Admin Dashboard...</div>;
    if (error) return <div className="p-8 text-red-500">{error}</div>;

    return (
        <div className="min-h-screen bg-[var(--color-background)] p-8">
            <div className="max-w-6xl mx-auto space-y-8">

                {/* Header */}
                <div className="flex items-center gap-3 mb-8">
                    <span className="text-3xl">⚡</span>
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-secondary)]">
                        GM Dashboard
                    </h1>
                </div>

                {/* METRICS CARDS */}
                {metrics && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {/* Users */}
                        <div className="bg-[var(--color-card)] border border-[var(--color-border)] rounded-xl p-6">
                            <h3 className="text-[var(--color-text-muted)] text-sm font-semibold mb-2 uppercase tracking-wider">User Metrics</h3>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <p className="text-xs text-[var(--color-text-muted)]">Total Registered Users</p>
                                    <p className="text-3xl font-bold text-[var(--color-active)]">{metrics.total_users}</p>
                                </div>
                            </div>
                        </div>

                        {/* Active Users */}
                        <div className="bg-[var(--color-card)] border border-[var(--color-border)] rounded-xl p-6 col-span-2 grid grid-cols-2 gap-6">
                            <div>
                                <h3 className="text-[var(--color-text-muted)] text-sm font-semibold mb-2 uppercase tracking-wider">Active Users (Web)</h3>
                                <p className="text-3xl font-bold text-cyan-400">{metrics.active_users_web}</p>
                                <p className="text-xs text-[var(--color-text-muted)]">Last 30 days</p>
                            </div>
                            <div>
                                <h3 className="text-[var(--color-text-muted)] text-sm font-semibold mb-2 uppercase tracking-wider">Active Users (Mobile)</h3>
                                <p className="text-3xl font-bold text-green-400">{metrics.active_users_mobile}</p>
                                <p className="text-xs text-[var(--color-text-muted)]">Last 30 days</p>
                            </div>
                        </div>

                        {/* Subs Breakdown */}
                        <div className="bg-[var(--color-card)] border border-[var(--color-border)] rounded-xl p-6 col-span-3">
                            <h3 className="text-[var(--color-text-muted)] text-sm font-semibold mb-4 uppercase tracking-wider">Subscription Breakdown</h3>
                            <div className="grid grid-cols-3 gap-6">
                                <div className="bg-white/5 rounded-lg p-4">
                                    <p className="text-sm text-[var(--color-text-muted)]">Free Tier</p>
                                    <p className="text-2xl font-bold text-white">{metrics.subscription_tiers.free}</p>
                                </div>
                                <div className="bg-yellow-900/20 border border-yellow-700/30 rounded-lg p-4">
                                    <p className="text-sm text-yellow-500">Premium Tier</p>
                                    <p className="text-2xl font-bold text-yellow-400">{metrics.subscription_tiers.premium}</p>
                                </div>
                                <div className="bg-purple-900/20 border border-purple-700/30 rounded-lg p-4">
                                    <p className="text-sm text-purple-400">VIP Tier</p>
                                    <p className="text-2xl font-bold text-purple-300">{metrics.subscription_tiers.vip}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* SYSTEM OPERATIONS - With Crawler Status */}
                <div className="bg-[var(--color-card)] border border-[var(--color-border)] rounded-xl p-6">
                    <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                        🛠️ SYSTEM OPERATIONS
                        {crawlerStatus && (
                            <div className={`ml-4 text-sm px-3 py-1 rounded-full border flex items-center gap-2 transition-all ${crawlerStatus.is_running
                                ? "bg-yellow-900/30 border-yellow-500 text-yellow-500 animate-pulse shadow-[0_0_10px_rgba(234,179,8,0.3)]"
                                : crawlerStatus.status === "success"
                                    ? "bg-green-900/30 border-green-500 text-green-500"
                                    : crawlerStatus.status === "error"
                                        ? "bg-red-900/30 border-red-500 text-red-500"
                                        : "bg-gray-800 border-gray-600 text-gray-400"
                                }`}>
                                {crawlerStatus.is_running ? (
                                    <>
                                        <span className="w-2 h-2 rounded-full bg-yellow-500 animate-ping"></span>
                                        Running Data Update...
                                    </>
                                ) : (
                                    <>
                                        {crawlerStatus.status === "success" ? "✅" : crawlerStatus.status === "error" ? "❌" : "⚪"}
                                        {crawlerStatus.status.toUpperCase()}
                                    </>
                                )}
                                <span className="text-xs opacity-70 border-l border-white/20 pl-2 ml-1">
                                    {crawlerStatus.last_run_time ? new Date(crawlerStatus.last_run_time).toLocaleTimeString() : "No Run Recorded"}
                                </span>
                            </div>
                        )}
                        {/* Status Message Display */}
                        {crawlerStatus && crawlerStatus.is_running && (
                            <span className="ml-4 text-sm text-[var(--color-text-muted)] animate-pulse">
                                {crawlerStatus.message}
                            </span>
                        )}
                    </h2>

                    {/* Category 1: Crawler Speed Test */}
                    <div className="mb-4">
                        <h3 className="text-sm font-semibold text-[var(--color-text-muted)] mb-2 flex items-center gap-2">
                            📊 Crawler Speed Test
                        </h3>
                        <div className="flex gap-3">
                            <button
                                onClick={async () => {
                                    if (!confirm("Trigger analysis? (Background Task)")) return;
                                    await handleCrawl(false);
                                }}
                                className="bg-blue-900 hover:bg-blue-700 text-white border border-blue-600 px-4 py-2 rounded-lg transition flex items-center gap-2"
                            >
                                ⚡ Update Market Data (Smart)
                            </button>

                            <button
                                onClick={async () => {
                                    if (!confirm("⚠️ FORCE REBUILD ALL DATA?\nThis will clear current year cache and re-fetch everything (~5-6 min).")) return;
                                    await handleCrawl(true);
                                }}
                                className="bg-red-900/50 hover:bg-red-800 text-white border border-red-600 px-4 py-2 rounded-lg transition flex items-center gap-2"
                            >
                                🔥 Rebuild All (Cold Run)
                            </button>
                        </div>
                    </div>

                    {/* Category 2: Backup & Refresh */}
                    <div>
                        <h3 className="text-sm font-semibold text-[var(--color-text-muted)] mb-2 flex items-center gap-2">
                            💾 Backup & Refresh
                        </h3>
                        <div className="flex gap-3">
                            <button
                                onClick={async () => {
                                    if (!confirm("Trigger manual backup to GitHub?")) return;
                                    try {
                                        const res = await fetch(`${API_BASE}/api/admin/backup`, {
                                            method: "POST",
                                            credentials: "include"
                                        });
                                        const data = await res.json();
                                        if (res.ok) {
                                            alert("✅ Backup Successful!\n" + JSON.stringify(data.details, null, 2));
                                        } else {
                                            alert("❌ Backup Failed: " + (data.detail || "Unknown error"));
                                        }
                                    } catch {
                                        alert("❌ Network Error");
                                    }
                                }}
                                className="bg-gray-800 hover:bg-gray-700 text-white border border-gray-600 px-4 py-2 rounded-lg transition flex items-center gap-2"
                            >
                                💾 Backup Portfolio DB to GitHub
                            </button>

                            <button
                                onClick={async () => {
                                    if (!confirm("📦 Rebuild & Push Pre-warm Data to GitHub?\n\nThis will:\n1. Rebuild All (Cold Run) ~5-6 min\n2. Push ~60 cache files to GitHub")) return;
                                    try {
                                        const res = await fetch(`${API_BASE}/api/admin/refresh-prewarm`, {
                                            method: "POST",
                                            credentials: "include"
                                        });
                                        const data = await res.json();
                                        if (res.ok) {
                                            alert(`✅ Pre-warm Complete!\n${data.message}\n\nDetails: ${JSON.stringify(data.details, null, 2)}`);
                                        } else {
                                            alert("❌ Failed: " + (data.detail || "Unknown error"));
                                        }
                                    } catch {
                                        alert("❌ Network Error");
                                    }
                                }}
                                className="bg-purple-900/50 hover:bg-purple-800 text-white border border-purple-600 px-4 py-2 rounded-lg transition flex items-center gap-2"
                            >
                                📦 Rebuild & Push Pre-warm Data
                            </button>
                        </div>
                    </div>
                </div>

                {/* FEEDBACK SECTION */}
                <div className="bg-[var(--color-card)] border border-[var(--color-border)] rounded-xl p-6">
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-xl font-bold">USER FEEDBACK & BUG REPORTS</h2>
                        <button onClick={fetchFeedback} className="text-xs bg-blue-600 px-2 py-1 rounded hover:bg-blue-500 transition">🔄 Refresh</button>
                    </div>

                    {/* Stats */}
                    <div className="grid grid-cols-5 gap-2 mb-6">
                        <div className="bg-red-900/20 border border-red-700/50 p-3 rounded text-center">
                            <span className="text-xl font-bold text-red-400">{feedbackStats.new}</span>
                            <p className="text-[10px] text-red-300 uppercase">New</p>
                        </div>
                        <div className="bg-yellow-900/20 border border-yellow-700/50 p-3 rounded text-center">
                            <span className="text-xl font-bold text-yellow-400">{feedbackStats.reviewing}</span>
                            <p className="text-[10px] text-yellow-300 uppercase">Reviewing</p>
                        </div>
                        <div className="bg-blue-900/20 border border-blue-700/50 p-3 rounded text-center">
                            <span className="text-xl font-bold text-blue-400">{feedbackStats.confirmed}</span>
                            <p className="text-[10px] text-blue-300 uppercase">Confirmed</p>
                        </div>
                        <div className="bg-green-900/20 border border-green-700/50 p-3 rounded text-center">
                            <span className="text-xl font-bold text-green-400">{feedbackStats.fixed}</span>
                            <p className="text-[10px] text-green-300 uppercase">Fixed</p>
                        </div>
                        <div className="bg-gray-800/50 border border-gray-700/50 p-3 rounded text-center">
                            <span className="text-xl font-bold text-gray-400">{feedbackStats.wontfix}</span>
                            <p className="text-[10px] text-gray-400 uppercase">Won&apos;t Fix</p>
                        </div>
                    </div>

                    <div className="bg-[var(--color-background)] rounded-lg overflow-hidden max-h-[600px] overflow-y-auto">
                        {loadingFeedback ? (
                            <div className="p-4 text-center animate-pulse">Loading feedback...</div>
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
                                            <option value="wontfix">⚫ Won&apos;t Fix</option>
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
        </div>
    );
}
