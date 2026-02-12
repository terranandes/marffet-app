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
    progress_pct: number;
    elapsed_seconds: number;
}

// Use relative paths to proxy via Next.js rewrites (preserves session cookies on Zeabur)
const API_BASE = "";

export default function AdminPage() {
    const [metrics, setMetrics] = useState<AdminMetrics | null>(null);
    const [loadingMetrics, setLoadingMetrics] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const [feedbackList, setFeedbackList] = useState<FeedbackItem[]>([]);
    const [feedbackStats, setFeedbackStats] = useState<FeedbackStats>({ new: 0, reviewing: 0, confirmed: 0, fixed: 0, wontfix: 0 });
    const [loadingFeedback, setLoadingFeedback] = useState(true);

    // Crawler Status
    const [crawlerStatus, setCrawlerStatus] = useState<CrawlerStatus | null>(null);
    const [lastRunDuration, setLastRunDuration] = useState<string | null>(null);
    const [syncProgress, setSyncProgress] = useState<number | null>(null);
    const [monitorPrewarm, setMonitorPrewarm] = useState(false);
    const [hasStartedRunning, setHasStartedRunning] = useState(false);
    const [safeMode, setSafeMode] = useState(true); // Phase 4: Safe Mode for Backfill (default ON)

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
                const data = await res.json();
                setCrawlerStatus(prev => {
                    // Update duration if:
                    // 1. Just finished (Running -> Not Running)
                    // 2. Or Loading page and already finished (prev is null & status=success)
                    const isJustFinished = prev?.is_running && !data.is_running;
                    const isAlreadyFinished = !prev && data.status === 'success'; // status could be 'success'

                    if ((isJustFinished || isAlreadyFinished) && data.elapsed_seconds > 0) {
                        const m = Math.floor(data.elapsed_seconds / 60);
                        const s = data.elapsed_seconds % 60;
                        setLastRunDuration(`${m}m ${s}s`);
                    }
                    // Reset duration on new start
                    if (!prev?.is_running && data.is_running) {
                        setLastRunDuration(null);
                    }
                    return data;
                });
            }
        } catch {
            console.error("Crawler status fetch error");
        }
    }, []);

    // Handle Sync All Dividends with Simulated Progress
    const handleSyncAllDividends = async () => {
        if (!confirm("Sync dividend cache for ALL stocks held by ALL users?\nThis may take a few minutes.")) return;

        setSyncProgress(0);
        const progressInterval = setInterval(() => {
            setSyncProgress(prev => {
                if (prev === null || prev >= 90) return prev;
                return prev + Math.floor(Math.random() * 5) + 1; // Increment 1-5%
            });
        }, 800);

        try {
            const res = await fetch(`${API_BASE}/api/sync/all-users-dividends`, {
                method: 'POST',
                credentials: 'include'
            });
            const data = await res.json();

            clearInterval(progressInterval);
            setSyncProgress(100);

            if (res.ok) {
                // Short delay to show 100%
                await new Promise(r => setTimeout(r, 500));
                alert(`✅ ${data.message}\nTotal Records: ${data.total_records}\n\nGit Backup: ${data.git_backup?.status === 'success' ? '✅ Success' : '⚠️ ' + (data.git_backup?.reason || 'Skipped')}`);
            } else {
                alert(`❌ ${data.detail || 'Sync failed'}`);
            }
        } catch {
            clearInterval(progressInterval);
            alert('❌ Network error during sync');
        } finally {
            setSyncProgress(null);
        }
    };

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

    // Handle Cache Initialize (Phase 4)
    const handleInitializeCache = async () => {
        try {
            const res = await fetch(`${API_BASE}/api/admin/system/initialize`, {
                method: 'POST',
                credentials: 'include'
            });
            const data = await res.json();
            if (res.ok) {
                alert(`✅ Cache Initialized! ${data.status === 'ok' ? 'Success' : 'Error: ' + data.error}`);
                fetchCrawlerStatus();
            } else {
                alert(`❌ Initialization failed: ${data.detail || data.error || 'Unknown error'}`);
            }
        } catch {
            alert('❌ Network error during cache initialization.');
        }
    };

    // Handle Smart Supplemental Refresh (Held Stocks) - New Phase 6
    const handleSupplementalRefresh = async () => {
        try {
            const res = await fetch(`${API_BASE}/api/admin/market-data/supplemental`, {
                method: 'POST',
                credentials: 'include'
            });
            const data = await res.json();
            if (res.ok) {
                alert(`✅ Smart Supplemental Refresh initiated! ${data.message}`);
                fetchCrawlerStatus();
            } else {
                alert(`❌ Supplemental refresh failed: ${data.detail || data.message || 'Unknown error'}`);
            }
        } catch {
            alert('❌ Network error during supplemental refresh.');
        }
    };

    // Handle Dividend Sync (Across all users)
    const handleSyncDividends = async () => {
        if (!confirm("🔄 Sync Dividends for ALL users' stocks?\nThis will update history and push to GitHub.")) return;
        try {
            const res = await fetch(`${API_BASE}/api/sync/all-users-dividends`, {
                method: 'POST',
                credentials: 'include'
            });
            const data = await res.json();
            if (res.ok) {
                alert(`✅ Dividend Sync Success! ${data.message}`);
            } else {
                alert(`❌ Sync failed: ${data.detail || data.message || 'Unknown error'}`);
            }
        } catch {
            alert('❌ Network error during dividend sync.');
        }
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

    // Handle Universe Backfill (Phase 4)
    const handleBackfill = async () => {
        const mode = safeMode ? 'SAFE (Incremental)' : '⚠️ OVERWRITE';
        if (!confirm(`🚀 START UNIVERSE BACKFILL?\n\nMode: ${mode}\nThis will fetch historical Prices + Dividends (2000-Present) for all stocks from Yahoo Finance.\n${safeMode ? "Safe Mode ON: Won't overwrite existing data." : "⚠️ DANGER: Will overwrite ALL existing data!"}\n\nThis is a heavy background task. Watch progress in the Crawler Status bar.`)) return;

        try {
            const res = await fetch(`${API_BASE}/api/admin/market-data/backfill?overwrite=${!safeMode}`, {
                method: 'POST',
                credentials: 'include'
            });
            const data = await res.json();
            if (res.ok) {
                alert(`✅ Backfill initiated! ${data.message}`);
                fetchCrawlerStatus();
            } else {
                alert(`❌ Backfill failed: ${data.detail || data.message}`);
            }
        } catch {
            alert('❌ Network error during backfill initiation.');
        }
    };

    // Handle Rebuild & Push Prewarm
    const handleRebuildPrewarm = async () => {
        if (!confirm("📦 Rebuild & Push Pre-warm Data to GitHub?\n\nThis will:\n1. Rebuild All (Cold Run) ~5-6 min\n2. Push ~60 cache files to GitHub")) return;

        try {
            const res = await fetch(`${API_BASE}/api/admin/refresh-prewarm`, {
                method: "POST",
                credentials: "include"
            });
            const data = await res.json();

            if (res.ok) {
                // Reset states to ensure we don't trigger "Success" based on old status
                setHasStartedRunning(false);
                setMonitorPrewarm(true);

                alert(`🚀 Job Started!\n${data.message}\n\nYou can watch the 'Crawler Speed Test' progress bar. You will be notified when it completes.`);
                fetchCrawlerStatus(); // Force update
            } else {
                alert("❌ Failed: " + (data.detail || "Unknown error"));
            }
        } catch {
            alert("❌ Network Error");
        }
    };

    // Handle DB Backup
    const handleDbBackup = async () => {
        if (!confirm("Trigger manual database backup to GitHub?")) return;
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
            alert("❌ Network Error during backup.");
        }
    };

    // Handle Copy Link
    const handleCopyMetrics = () => {
        const url = `${API_BASE}/api/admin/metrics`;
        navigator.clipboard.writeText(url);
        alert("Metrics URL copied to clipboard!");
    };

    // Monitor Prewarm Completion
    useEffect(() => {
        if (!monitorPrewarm || !crawlerStatus) return;

        // 1. Detect Start (Transition to Running)
        if (crawlerStatus.is_running) {
            setHasStartedRunning(true);
        }

        // 2. Detect Completion (Only if we saw it running previously)
        if (hasStartedRunning && !crawlerStatus.is_running && crawlerStatus.status === 'success') {
            alert("✅ Rebuild & Push Operation Completed!");
            setMonitorPrewarm(false);
            setHasStartedRunning(false);
        }
    }, [crawlerStatus, monitorPrewarm, hasStartedRunning]);

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
                        {/* Unified User Metrics Card */}
                        <div className="bg-[var(--color-card)] border border-[var(--color-border)] rounded-xl p-6 col-span-1 lg:col-span-3">
                            <h3 className="text-[var(--color-text-muted)] text-sm font-semibold mb-4 uppercase tracking-wider">User Metrics</h3>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                {/* Total Users */}
                                <div className="bg-white/5 rounded-lg p-4">
                                    <p className="text-sm text-[var(--color-text-muted)]">Total Registered</p>
                                    <p className="text-3xl font-bold text-[var(--color-active)]">{metrics.total_users}</p>
                                </div>
                                {/* Active Web */}
                                <div className="bg-cyan-900/20 border border-cyan-700/30 rounded-lg p-4">
                                    <p className="text-sm text-cyan-400">Active Users (Web)</p>
                                    <p className="text-3xl font-bold text-cyan-300">{metrics.active_users_web}</p>
                                    <p className="text-xs text-cyan-500/70 mt-1">Last 30 days</p>
                                </div>
                                {/* Active Mobile */}
                                <div className="bg-green-900/20 border border-green-700/30 rounded-lg p-4">
                                    <p className="text-sm text-green-400">Active Users (Mobile)</p>
                                    <p className="text-3xl font-bold text-green-300">{metrics.active_users_mobile}</p>
                                    <p className="text-xs text-green-500/70 mt-1">Last 30 days</p>
                                </div>
                            </div>
                        </div>

                        {/* Subs Breakdown */}
                        <div className="bg-[var(--color-card)] border border-[var(--color-border)] rounded-xl p-6 col-span-3">
                            <h3 className="text-[var(--color-text-muted)] text-sm font-semibold mb-4 uppercase tracking-wider">Subscription Breakdown</h3>
                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
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
                                        Running... {crawlerStatus.elapsed_seconds ? `(${Math.floor(crawlerStatus.elapsed_seconds / 60)}m ${crawlerStatus.elapsed_seconds % 60}s)` : ''}
                                    </>
                                ) : (
                                    <>
                                        {crawlerStatus.status === "success" ? "✅" : crawlerStatus.status === "error" ? "❌" : "⚪"}
                                        {crawlerStatus.status.toUpperCase()}
                                        {crawlerStatus.status === 'success' && lastRunDuration && (
                                            <span className="ml-2 text-xs text-green-300 font-mono">
                                                (Finished in {lastRunDuration})
                                            </span>
                                        )}
                                    </>
                                )}
                                <span className="text-xs opacity-70 border-l border-white/20 pl-2 ml-1">
                                    {crawlerStatus.last_run_time ? new Date(crawlerStatus.last_run_time).toLocaleTimeString() : "No Run Recorded"}
                                </span>
                            </div>
                        )}
                    </h2>

                    {/* Crawler Progress Bar */}
                    {crawlerStatus && (crawlerStatus.is_running || crawlerStatus.progress_pct > 0) && (
                        <div className="mb-6 bg-black/30 p-4 rounded-lg border border-white/5">
                            <div className="flex justify-between text-xs text-gray-400 mb-1">
                                <span>Crawler Progress: {crawlerStatus.progress_pct}%</span>
                                <span>{crawlerStatus.message}</span>
                            </div>
                            <div className="w-full bg-gray-700 h-2 rounded-full overflow-hidden">
                                <div
                                    className="bg-[#00f2ea] h-full transition-all duration-500 ease-out shadow-[0_0_10px_#00f2ea]"
                                    style={{ width: `${crawlerStatus.progress_pct}%` }}
                                ></div>
                            </div>
                        </div>
                    )}

                    {/* Sync Progress Bar */}
                    {syncProgress !== null && (
                        <div className="mb-6 bg-purple-900/20 p-4 rounded-lg border border-purple-500/30">
                            <div className="flex justify-between text-xs text-purple-300 mb-1">
                                <span>Syncing Dividends & Backing up...</span>
                                <span>{syncProgress}%</span>
                            </div>
                            <div className="w-full bg-gray-700 h-2 rounded-full overflow-hidden">
                                <div
                                    className="bg-purple-500 h-full transition-all duration-300 ease-out shadow-[0_0_10px_#a855f7]"
                                    style={{ width: `${syncProgress}%` }}
                                ></div>
                            </div>
                        </div>
                    )}

                    {/* Section 1: Routine Operations */}
                    <div className="mb-6 bg-gray-800/40 p-4 rounded-xl border border-blue-500/20">
                        <h4 className="text-sm font-semibold text-blue-400 mb-3 flex items-center gap-2">
                            📅 Routine Operations (Daily/Weekly)
                        </h4>
                        <div className="flex flex-wrap gap-3">
                            <button
                                onClick={handleSupplementalRefresh}
                                className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg transition flex items-center gap-2 shadow-lg shadow-blue-900/20"
                                title="Targets user portraits and top ETFs (Incremental)"
                            >
                                ✨ Smart Supplemental Refresh
                            </button>

                            <button
                                onClick={handleSyncAllDividends}
                                disabled={syncProgress !== null}
                                className={`px-4 py-2 rounded-lg transition flex items-center gap-2 text-white border ${syncProgress !== null
                                    ? 'bg-purple-900/30 border-purple-800 cursor-not-allowed opacity-70'
                                    : 'bg-purple-900/50 hover:bg-purple-800 border-purple-600'
                                    }`}
                                title="Syncs dividend history for ALL users' stocks"
                            >
                                {syncProgress !== null ? '⏳ Syncing Dividends...' : '💰 Sync All Dividends'}
                            </button>

                            <button
                                onClick={handleDbBackup}
                                className="bg-gray-700 hover:bg-gray-650 text-white px-4 py-2 rounded-lg transition flex items-center gap-1 border border-gray-600"
                            >
                                💾 GitHub Backup (DB)
                            </button>
                        </div>
                    </div>

                    {/* Section 2: Maintenance & Reconstruction */}
                    <div className="mb-6 bg-gray-800/40 p-4 rounded-xl border border-red-500/10">
                        <h4 className="text-sm font-semibold text-red-400 mb-3 flex items-center gap-2">
                            🛠️ Maintenance & Repair
                        </h4>
                        <div className="flex flex-wrap gap-3">
                            <button
                                onClick={async () => {
                                    if (!confirm("⚠️ START FULL ANALYSIS?\nThis is a standard Smart Analysis run (~2-3 min).")) return;
                                    await handleCrawl(false);
                                }}
                                className="bg-gray-700 hover:bg-gray-600 text-white border border-gray-600 px-4 py-2 rounded-lg transition flex items-center gap-2"
                                title="Full Crawler run (Main Loop)"
                            >
                                🕷️ Crawler Analysis (Full)
                            </button>

                            <button
                                onClick={async () => {
                                    if (!confirm("⚠️ FORCE REBUILD ALL DATA?\nThis will clear current year cache and re-fetch everything (~5-6 min).")) return;
                                    await handleCrawl(true);
                                }}
                                className="bg-red-900/50 hover:bg-red-800 text-white border border-red-600 px-4 py-2 rounded-lg transition flex items-center gap-2"
                                title="Clears cache and rebuilds current year"
                            >
                                🔥 Force Rebuild (Cold)
                            </button>

                            <button
                                onClick={handleRebuildPrewarm}
                                disabled={monitorPrewarm}
                                className={`px-4 py-2 rounded-lg transition flex items-center gap-2 text-white border ${monitorPrewarm
                                    ? 'bg-indigo-900/30 border-indigo-800 cursor-not-allowed opacity-70'
                                    : 'bg-indigo-900/50 hover:bg-indigo-800 border-indigo-600'
                                    }`}
                            >
                                {monitorPrewarm ? '⏳ Pushing to GitHub...' : '📦 Rebuild Pre-warm Data'}
                            </button>
                        </div>
                    </div>

                    {/* Section 3: Low-Level System & Universe */}
                    <div className="mb-6 bg-gray-800/40 p-4 rounded-xl border border-gray-500/10">
                        <h4 className="text-sm font-semibold text-gray-400 mb-3 flex items-center gap-2">
                            ⚙️ System Tools & Deep Universe
                        </h4>
                        <div className="flex flex-wrap gap-3">
                            <button
                                onClick={handleInitializeCache}
                                className="bg-green-900/50 hover:bg-green-800 text-white border border-green-600 px-4 py-2 rounded-lg transition flex items-center gap-2"
                                title="Force reload of prices from JSON into RAM"
                            >
                                🔋 Reload Price Cache (Force)
                            </button>

                            <button
                                onClick={handleCopyMetrics}
                                className="bg-gray-700 hover:bg-gray-600 text-white border border-gray-500 px-4 py-2 rounded-lg transition flex items-center gap-2"
                            >
                                🔗 Copy Metrics URL
                            </button>

                            {/* Backfill with Safe Mode Toggle */}
                            <div className="flex items-center gap-3 bg-black/40 px-3 py-1 rounded-lg border border-white/5">
                                <label className="flex items-center gap-2 text-[10px] cursor-pointer select-none">
                                    <input
                                        type="checkbox"
                                        checked={safeMode}
                                        onChange={(e) => setSafeMode(e.target.checked)}
                                        className="w-3 h-3 accent-cyan-500 rounded"
                                    />
                                    <span className={safeMode ? 'text-cyan-400' : 'text-orange-400 font-bold'}>
                                        {safeMode ? '🛡️ Safe Mode' : '⚠️ Overwrite'}
                                    </span>
                                </label>
                                <button
                                    onClick={handleBackfill}
                                    className="text-[10px] bg-cyan-900 hover:bg-cyan-800 px-3 py-1 rounded border border-cyan-700"
                                >
                                    🚀 Universe Backfill (2000+)
                                </button>
                            </div>
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
                    <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 mb-6">
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
