"use client";

import { useEffect, useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import toast from "react-hot-toast";
import ReactECharts from "echarts-for-react";
import { useUser } from "@/lib/UserContext";

/* ─── Types ─── */
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

const API_BASE = "";

/* ─── Collapsible Section ─── */
function CollapsibleSection({
    id,
    title,
    icon,
    defaultOpen = false,
    accentColor = "cyan",
    children,
}: {
    id: string;
    title: string;
    icon: string;
    defaultOpen?: boolean;
    accentColor?: string;
    children: React.ReactNode;
}) {
    const [isOpen, setIsOpen] = useState(() => {
        if (typeof window === "undefined") return defaultOpen;
        const saved = localStorage.getItem(`admin-section-${id}`);
        return saved !== null ? saved === "true" : defaultOpen;
    });

    const toggle = () => {
        const next = !isOpen;
        setIsOpen(next);
        localStorage.setItem(`admin-section-${id}`, String(next));
    };

    const borderColor = {
        cyan: "border-cyan-700/40",
        amber: "border-amber-700/40",
        red: "border-red-700/40",
        emerald: "border-emerald-700/40",
        gray: "border-gray-700/40",
    }[accentColor] || "border-gray-700/40";

    const headerText = {
        cyan: "text-cyan-400",
        amber: "text-amber-400",
        red: "text-red-400",
        emerald: "text-emerald-400",
        gray: "text-gray-400",
    }[accentColor] || "text-gray-400";

    return (
        <div className={`bg-[#0d0d1a] border ${borderColor} rounded-sm overflow-hidden`}>
            <button
                onClick={toggle}
                className={`w-full flex items-center justify-between p-4 hover:bg-white/[0.02] transition-colors ${headerText}`}
            >
                <span className="flex items-center gap-2 text-base font-semibold tracking-wide uppercase">
                    <span>{icon}</span>
                    {title}
                </span>
                <motion.span
                    animate={{ rotate: isOpen ? 180 : 0 }}
                    transition={{ duration: 0.2 }}
                    className="text-xs opacity-60"
                >
                    ▼
                </motion.span>
            </button>
            <AnimatePresence initial={false}>
                {isOpen && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.25, ease: "easeInOut" }}
                        className="overflow-hidden"
                    >
                        <div className="p-5 pt-2 border-t border-white/5">{children}</div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}

/* ─── Inline Spinner ─── */
function Spinner() {
    return (
        <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
    );
}

/* ─── User Growth Chart ─── */
interface GrowthPoint { date: string; registered: number; premium: number; vip: number; }

function UserGrowthChart({ data }: { data: GrowthPoint[] }) {
    if (!data.length) {
        return (
            <div className="flex items-center justify-center h-40 text-zinc-600 text-sm">
                No registration data yet.
            </div>
        );
    }

    const dates = data.map(d => d.date);
    const option = {
        backgroundColor: "transparent",
        tooltip: {
            trigger: "axis",
            backgroundColor: "#0d0d1a",
            borderColor: "#ffffff18",
            textStyle: { color: "#e2e8f0", fontSize: 12 },
        },
        legend: {
            data: ["Registered", "Premium", "VIP"],
            textStyle: { color: "#94a3b8", fontSize: 11 },
            top: 0,
        },
        grid: { left: 40, right: 16, top: 36, bottom: 24 },
        xAxis: {
            type: "category",
            data: dates,
            axisLine: { lineStyle: { color: "#334155" } },
            axisLabel: { color: "#64748b", fontSize: 10, rotate: 30 },
            boundaryGap: false,
        },
        yAxis: {
            type: "value",
            minInterval: 1,
            axisLabel: { color: "#64748b", fontSize: 10 },
            splitLine: { lineStyle: { color: "#1e293b" } },
        },
        series: [
            {
                name: "Registered",
                type: "line",
                data: data.map(d => d.registered),
                smooth: true,
                symbol: "none",
                lineStyle: { color: "#22d3ee", width: 2 },
                areaStyle: { color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: "#22d3ee30" }, { offset: 1, color: "#22d3ee04" }] } },
            },
            {
                name: "Premium",
                type: "line",
                data: data.map(d => d.premium),
                smooth: true,
                symbol: "none",
                lineStyle: { color: "#f59e0b", width: 2 },
                areaStyle: { color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: "#f59e0b28" }, { offset: 1, color: "#f59e0b04" }] } },
            },
            {
                name: "VIP",
                type: "line",
                data: data.map(d => d.vip),
                smooth: true,
                symbol: "none",
                lineStyle: { color: "#34d399", width: 2 },
                areaStyle: { color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: "#34d39928" }, { offset: 1, color: "#34d39904" }] } },
            },
        ],
    };

    return (
        <div className="mt-4">
            <p className="text-xs text-zinc-500 uppercase tracking-wider mb-2 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-cyan-400 shadow-[0_0_6px_#22d3ee]"></span>
                Account Growth History
            </p>
            <ReactECharts option={option} style={{ height: 200 }} />
        </div>
    );
}

/* ─── Main Page ─── */
export default function AdminPage() {
    const { user } = useUser();
    const [metrics, setMetrics] = useState<AdminMetrics | null>(null);
    const [loadingMetrics, setLoadingMetrics] = useState(true);
    const [growthData, setGrowthData] = useState<GrowthPoint[]>([]);
    const [error, setError] = useState<string | null>(null);

    const [feedbackList, setFeedbackList] = useState<FeedbackItem[]>([]);
    const [feedbackStats, setFeedbackStats] = useState<FeedbackStats>({ new: 0, reviewing: 0, confirmed: 0, fixed: 0, wontfix: 0 });
    const [loadingFeedback, setLoadingFeedback] = useState(true);

    const [crawlerStatus, setCrawlerStatus] = useState<CrawlerStatus | null>(null);
    const [lastRunDuration, setLastRunDuration] = useState<string | null>(null);
    const [syncProgress, setSyncProgress] = useState<number | null>(null);
    const [monitorPrewarm, setMonitorPrewarm] = useState(false);
    const [hasStartedRunning, setHasStartedRunning] = useState(false);
    const [safeMode, setSafeMode] = useState(true);
    const [pushToGithub, setPushToGithub] = useState(false);
    const [deepUniverse, setDeepUniverse] = useState(false);

    // Loading states for buttons
    const [loadingBtn, setLoadingBtn] = useState<string | null>(null);

    // Membership Management State
    const [memberships, setMemberships] = useState<any[]>([]);
    const [loadingMemberships, setLoadingMemberships] = useState(false);
    const [memberEmail, setMemberEmail] = useState("");
    const [memberTier, setMemberTier] = useState("PREMIUM");
    const [memberDuration, setMemberDuration] = useState("1");

    useEffect(() => {
        const isLocal = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
        if (isLocal) setDeepUniverse(true);
    }, []);

    /* ─── Fetchers ─── */
    const fetchMetrics = useCallback(async () => {
        if (!user) {
            setLoadingMetrics(false);
            return;
        }
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
    }, [user]);

    const fetchFeedback = useCallback(async () => {
        if (!user) {
            setLoadingFeedback(false);
            return;
        }
        setLoadingFeedback(true);
        try {
            const [listRes, statsRes] = await Promise.all([
                fetch(`${API_BASE}/api/feedback`, { credentials: "include" }),
                fetch(`${API_BASE}/api/feedback/stats`, { credentials: "include" }),
            ]);
            if (listRes.ok) setFeedbackList(await listRes.json());
            if (statsRes.ok) setFeedbackStats(await statsRes.json());
        } catch {
            console.error("Feedback fetch error");
        }
        setLoadingFeedback(false);
    }, [user]);

    const fetchMemberships = useCallback(async () => {
        if (!user) {
            setLoadingMemberships(false);
            return;
        }
        setLoadingMemberships(true);
        try {
            const res = await fetch(`${API_BASE}/api/admin/memberships`, { credentials: "include" });
            if (res.ok) setMemberships(await res.json());
        } catch {
            console.error("Membership fetch error");
        }
        setLoadingMemberships(false);
    }, [user]);

    const handleInjectMembership = async () => {
        if (!memberEmail) return toast.error("Email required");
        await withLoading("inject-membership", async () => {
            try {
                const res = await fetch(`${API_BASE}/api/admin/memberships`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        email: memberEmail,
                        tier: memberTier,
                        duration_months: parseInt(memberDuration)
                    }),
                    credentials: "include"
                });
                const data = await res.json();
                if (res.ok) {
                    toast.success(data.message);
                    setMemberEmail("");
                    fetchMemberships();
                } else {
                    toast.error(data.detail || "Injection failed");
                }
            } catch {
                toast.error("Network Error injecting membership");
            }
        });
    };

    const handleRevokeMembership = async (email: string) => {
        if (!confirm(`Revoke membership for ${email}?`)) return;
        await withLoading(`revoke-${email}`, async () => {
            try {
                const res = await fetch(`${API_BASE}/api/admin/memberships/${encodeURIComponent(email)}`, {
                    method: "DELETE",
                    credentials: "include"
                });
                if (res.ok) {
                    toast.success("Membership revoked");
                    fetchMemberships();
                } else {
                    toast.error("Failed to revoke");
                }
            } catch {
                toast.error("Network Error revoking membership");
            }
        });
    };

    const fetchCrawlerStatus = useCallback(async () => {
        try {
            const res = await fetch(`${API_BASE}/api/admin/crawl/status?key=secret`, { credentials: "include" });
            if (res.ok) {
                const data = await res.json();
                setCrawlerStatus(prev => {
                    const isJustFinished = prev?.is_running && !data.is_running;
                    const isAlreadyFinished = !prev && data.status === "success";
                    if ((isJustFinished || isAlreadyFinished) && data.elapsed_seconds > 0) {
                        const m = Math.floor(data.elapsed_seconds / 60);
                        const s = data.elapsed_seconds % 60;
                        setLastRunDuration(`${m}m ${s}s`);
                    }
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

    /* ─── Handlers (with toast) ─── */
    const withLoading = async (key: string, fn: () => Promise<void>) => {
        setLoadingBtn(key);
        try {
            await fn();
        } finally {
            setLoadingBtn(null);
        }
    };

    const handleSyncAllDividends = async () => {
        if (!confirm("Sync dividend cache for ALL stocks held by ALL users?\nThis may take a few minutes.")) return;
        await withLoading("sync-div", async () => {
            setSyncProgress(0);
            const progressInterval = setInterval(() => {
                setSyncProgress(prev => {
                    if (prev === null || prev >= 90) return prev;
                    return prev + Math.floor(Math.random() * 5) + 1;
                });
            }, 800);
            try {
                const res = await fetch(`${API_BASE}/api/sync/all-users-dividends`, { method: "POST", credentials: "include" });
                const data = await res.json();
                clearInterval(progressInterval);
                setSyncProgress(100);
                await new Promise(r => setTimeout(r, 500));
                if (res.ok) {
                    toast.success(`Synced! Total Records: ${data.total_records}`);
                } else {
                    toast.error(data.detail || "Sync failed");
                }
            } catch {
                clearInterval(progressInterval);
                toast.error("Network error during sync");
            } finally {
                setSyncProgress(null);
            }
        });
    };

    const handleInitializeCache = async () => {
        await withLoading("init-cache", async () => {
            try {
                const res = await fetch(`${API_BASE}/api/admin/system/initialize`, { method: "POST", credentials: "include" });
                const data = await res.json();
                if (res.ok) {
                    toast.success("Cache Initialized!");
                    fetchCrawlerStatus();
                } else {
                    toast.error(`Init failed: ${data.detail || data.error || "Unknown error"}`);
                }
            } catch {
                toast.error("Network error during cache initialization.");
            }
        });
    };

    const handleSupplementalRefresh = async () => {
        await withLoading("supp-refresh", async () => {
            try {
                const res = await fetch(`${API_BASE}/api/admin/market-data/supplemental`, { method: "POST", credentials: "include" });
                const data = await res.json();
                if (res.ok) {
                    toast.success(`Smart Refresh initiated! ${data.message}`);
                    fetchCrawlerStatus();
                } else {
                    toast.error(`Refresh failed: ${data.detail || data.message || "Unknown error"}`);
                }
            } catch {
                toast.error("Network error during supplemental refresh.");
            }
        });
    };

    const handleSyncDividends = async () => {
        if (!confirm("🔄 Sync Dividends for ALL targets in the UNIVERSE?\nThis will update history and push to GitHub.")) return;
        await withLoading("sync-univ-div", async () => {
            try {
                const res = await fetch(`${API_BASE}/api/admin/market-data/sync-dividends`, { method: "POST", credentials: "include" });
                const data = await res.json();
                if (res.ok) {
                    toast.success(`Global Dividend Sync initiated! ${data.message}`);
                } else {
                    toast.error(`Sync failed: ${data.detail || data.message || "Unknown error"}`);
                }
            } catch {
                toast.error("Network error during dividend sync.");
            }
        });
    };

    const handleCrawl = async (force: boolean) => {
        const key = force ? "crawl-force" : "crawl-full";
        await withLoading(key, async () => {
            try {
                const res = await fetch(`${API_BASE}/api/admin/crawl?key=secret&force=${force}`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    credentials: "include",
                });
                const data = await res.json();
                if (res.ok) {
                    toast.success(`Crawl initiated! ${data.message}`);
                    fetchCrawlerStatus();
                } else {
                    toast.error(`Crawl failed: ${data.error || data.message}`);
                }
            } catch {
                toast.error("Network error during crawl initiation.");
            }
        });
    };

    const handleBackfill = async () => {
        const mode = safeMode ? "SAFE (Incremental)" : "⚠️ OVERWRITE";
        const pushMsg = pushToGithub ? "\n📤 WILL PUSH TO GITHUB ON COMPLETION" : "";
        if (
            !confirm(
                `🚀 START UNIVERSE BACKFILL?\n\nMode: ${mode}${pushMsg}\n\nThis will fetch historical Prices + Dividends (2000-Present).\n${safeMode ? "Safe Mode ON: Won't overwrite existing data." : "⚠️ DANGER: Will overwrite ALL existing data!"}`
            )
        )
            return;

        await withLoading("backfill", async () => {
            try {
                const res = await fetch(`${API_BASE}/api/admin/market-data/backfill?overwrite=${!safeMode}&push=${pushToGithub}&deep=${deepUniverse}`, {
                    method: "POST",
                    credentials: "include",
                });
                const data = await res.json();
                if (res.ok) {
                    toast.success(`Backfill initiated! ${data.message}`);
                    fetchCrawlerStatus();
                } else {
                    toast.error(`Backfill failed: ${data.detail || data.message}`);
                }
            } catch {
                toast.error("Network error during backfill initiation.");
            }
        });
    };

    const handleRebuildPrewarm = async () => {
        if (!confirm("📦 Rebuild & Push Pre-warm Data to GitHub?\n\nThis will:\n1. Rebuild All (Cold Run) ~5-6 min\n2. Push ~60 cache files to GitHub")) return;
        await withLoading("rebuild", async () => {
            try {
                const res = await fetch(`${API_BASE}/api/admin/refresh-prewarm`, { method: "POST", credentials: "include" });
                const data = await res.json();
                if (res.ok) {
                    setHasStartedRunning(false);
                    setMonitorPrewarm(true);
                    toast.success(`Job Started! ${data.message}`);
                    fetchCrawlerStatus();
                } else {
                    toast.error("Failed: " + (data.detail || "Unknown error"));
                }
            } catch {
                toast.error("Network Error");
            }
        });
    };

    const handleDbBackup = async () => {
        if (!confirm("Trigger manual database backup to GitHub?")) return;
        await withLoading("db-backup", async () => {
            try {
                const res = await fetch(`${API_BASE}/api/admin/backup`, { method: "POST", credentials: "include" });
                const data = await res.json();
                if (res.ok) {
                    toast.success("Backup Successful!");
                } else {
                    toast.error("Backup Failed: " + (data.detail || "Unknown error"));
                }
            } catch {
                toast.error("Network Error during backup.");
            }
        });
    };

    const handleCopyMetrics = () => {
        const url = `${API_BASE}/api/admin/metrics`;
        navigator.clipboard.writeText(url);
        toast.success("Metrics URL copied!");
    };

    useEffect(() => {
        fetchMetrics();
        fetchFeedback();
        fetchMemberships();
        fetchCrawlerStatus();
        // Fetch user growth data once
        fetch(`${API_BASE}/api/admin/user-growth`, { credentials: "include" })
            .then(r => r.ok ? r.json() : [])
            .then(setGrowthData)
            .catch(() => { });
        const interval = setInterval(fetchCrawlerStatus, 5000);
        return () => clearInterval(interval);
    }, [fetchMetrics, fetchFeedback, fetchMemberships, fetchCrawlerStatus]);

    const updateFeedbackStatus = async (id: number, status: string) => {
        try {
            await fetch(`${API_BASE}/api/feedback/${id}`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ status }),
                credentials: "include",
            });
            toast.success(`Status → ${status}`);
            const statsRes = await fetch(`${API_BASE}/api/feedback/stats`, { credentials: "include" });
            if (statsRes.ok) setFeedbackStats(await statsRes.json());
            const listRes = await fetch(`${API_BASE}/api/feedback`, { credentials: "include" });
            if (listRes.ok) setFeedbackList(await listRes.json());
        } catch {
            toast.error("Failed to update status");
        }
    };

    const updateFeedbackNotes = async (id: number, notes: string) => {
        try {
            await fetch(`${API_BASE}/api/feedback/${id}`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ agent_notes: notes }),
                credentials: "include",
            });
            toast.success("Notes saved");
        } catch {
            console.error("Failed to update notes");
        }
    };

    const getTypeColor = (type: string) => {
        switch (type) {
            case "bug": return "bg-red-900/50 text-red-200 border border-red-800";
            case "feature": return "bg-cyan-900/50 text-cyan-200 border border-cyan-800";
            case "content": return "bg-emerald-900/50 text-emerald-200 border border-emerald-800";
            default: return "bg-gray-800 text-gray-300 border border-gray-700";
        }
    };

    const getTypeIcon = (type: string) => {
        switch (type) {
            case "bug": return "🐛";
            case "feature": return "✨";
            case "content": return "📝";
            default: return "🗨️";
        }
    };

    const copyFeedbackToJira = (item: FeedbackItem) => {
        const md = `## [${item.feedback_type.toUpperCase()}] ${item.feature_category}\n\n**Reporter:** ${item.user_email || "Anonymous"}\n**Date:** ${item.created_at?.substring(0, 10) || "N/A"}\n**Status:** ${item.status}\n\n### Description\n${item.message}\n\n---\n*Feedback ID: ${item.id}*`;
        navigator.clipboard.writeText(md);
        toast.success("Copied as JIRA markdown!");
    };

    // Monitor Prewarm Completion
    useEffect(() => {
        if (!monitorPrewarm || !crawlerStatus) return;
        if (crawlerStatus.is_running) setHasStartedRunning(true);
        if (hasStartedRunning && !crawlerStatus.is_running && crawlerStatus.status === "success") {
            toast.success("Rebuild & Push Operation Completed!");
            setMonitorPrewarm(false);
            setHasStartedRunning(false);
        }
    }, [crawlerStatus, monitorPrewarm, hasStartedRunning]);

    /* ─── Render ─── */
    if (loadingMetrics) {
        return (
            <div className="min-h-screen bg-[var(--color-background)] flex items-center justify-center">
                <div className="flex items-center gap-3 text-[var(--color-text-muted)]">
                    <Spinner />
                    <span className="text-sm tracking-widest uppercase">Loading Dashboard...</span>
                </div>
            </div>
        );
    }
    if (error) return <div className="p-8 text-red-500 font-mono text-sm">{error}</div>;

    const btnBase = "px-4 py-2 rounded-sm transition-all duration-150 flex items-center gap-2 text-sm font-medium border disabled:opacity-50 disabled:cursor-not-allowed";

    return (
        <div className="min-h-screen bg-[var(--color-background)] p-4 md:p-8">
            <div className="max-w-6xl mx-auto space-y-4">
                {/* Header */}
                <div className="flex items-center gap-3 mb-6">
                    <span className="text-3xl">⚡</span>
                    <h1 className="text-3xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-emerald-400">
                        GM Dashboard
                    </h1>
                </div>

                {/* ── Crawler Global Status Bar ── */}
                {crawlerStatus && (
                    <div className="bg-[#0d0d1a] border border-white/5 rounded-sm p-3 flex items-center gap-3 text-xs font-mono">
                        <div
                            className={`px-2 py-1 rounded-sm border flex items-center gap-2 transition-all ${crawlerStatus.is_running
                                ? "bg-amber-900/30 border-amber-500 text-amber-400 animate-pulse shadow-[0_0_8px_rgba(245,158,11,0.2)]"
                                : crawlerStatus.status === "success"
                                    ? "bg-emerald-900/30 border-emerald-500 text-emerald-400"
                                    : crawlerStatus.status === "error"
                                        ? "bg-red-900/30 border-red-500 text-red-400"
                                        : "bg-gray-800 border-gray-600 text-gray-400"
                                }`}
                        >
                            {crawlerStatus.is_running ? (
                                <>
                                    <span className="w-2 h-2 rounded-full bg-amber-500 animate-ping" />
                                    Running... {crawlerStatus.elapsed_seconds ? `(${Math.floor(crawlerStatus.elapsed_seconds / 60)}m ${crawlerStatus.elapsed_seconds % 60}s)` : ""}
                                </>
                            ) : (
                                <>
                                    {crawlerStatus.status === "success" ? "✅" : crawlerStatus.status === "error" ? "❌" : "⚪"}
                                    {crawlerStatus.status.toUpperCase()}
                                    {crawlerStatus.status === "success" && lastRunDuration && (
                                        <span className="ml-1 text-emerald-300">(Finished in {lastRunDuration})</span>
                                    )}
                                </>
                            )}
                        </div>
                        <span className="opacity-50 border-l border-white/10 pl-2">
                            {crawlerStatus.last_run_time ? new Date(crawlerStatus.last_run_time).toLocaleTimeString() : "No Run Recorded"}
                        </span>
                    </div>
                )}

                {/* Crawler Progress Bar */}
                {crawlerStatus && (crawlerStatus.is_running || crawlerStatus.progress_pct > 0) && (
                    <div className="bg-[#0d0d1a] border border-white/5 rounded-sm p-3">
                        <div className="flex justify-between text-xs text-gray-400 mb-1">
                            <span>Crawler Progress: {crawlerStatus.progress_pct}%</span>
                            <span className="font-mono">{crawlerStatus.message}</span>
                        </div>
                        <div className="w-full bg-gray-800 h-1.5 rounded-sm overflow-hidden">
                            <motion.div
                                className="bg-cyan-500 h-full shadow-[0_0_8px_#06b6d4]"
                                initial={{ width: 0 }}
                                animate={{ width: `${crawlerStatus.progress_pct}%` }}
                                transition={{ duration: 0.5 }}
                            />
                        </div>
                    </div>
                )}

                {/* Sync Progress Bar */}
                {syncProgress !== null && (
                    <div className="bg-amber-900/10 border border-amber-700/30 rounded-sm p-3">
                        <div className="flex justify-between text-xs text-amber-300 mb-1">
                            <span>Syncing Dividends & Backing up...</span>
                            <span>{syncProgress}%</span>
                        </div>
                        <div className="w-full bg-gray-800 h-1.5 rounded-sm overflow-hidden">
                            <motion.div
                                className="bg-amber-500 h-full shadow-[0_0_8px_#f59e0b]"
                                animate={{ width: `${syncProgress}%` }}
                                transition={{ duration: 0.3 }}
                            />
                        </div>
                    </div>
                )}

                {/* ── Section: Metrics ── */}
                <CollapsibleSection id="metrics" title="User Metrics" icon="📊" defaultOpen={true} accentColor="cyan">
                    {metrics && (
                        <div className="space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                                <div className="bg-white/[0.03] border border-white/5 rounded-sm p-4">
                                    <p className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider">Total Registered</p>
                                    <p className="text-3xl font-bold text-[var(--color-active)] mt-1 font-mono">{metrics.total_users}</p>
                                </div>
                                <div className="bg-cyan-900/10 border border-cyan-700/20 rounded-sm p-4">
                                    <p className="text-xs text-cyan-400 uppercase tracking-wider">Active Users (Web)</p>
                                    <p className="text-3xl font-bold text-cyan-300 mt-1 font-mono">{metrics.active_users_web}</p>
                                    <p className="text-[10px] text-cyan-500/60 mt-1">Last 30 days</p>
                                </div>
                                <div className="bg-emerald-900/10 border border-emerald-700/20 rounded-sm p-4">
                                    <p className="text-xs text-emerald-400 uppercase tracking-wider">Active Users (Mobile)</p>
                                    <p className="text-3xl font-bold text-emerald-300 mt-1 font-mono">{metrics.active_users_mobile}</p>
                                    <p className="text-[10px] text-emerald-500/60 mt-1">Last 30 days</p>
                                </div>
                            </div>

                            {/* Subscription Breakdown */}
                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                                <div className="bg-white/[0.03] border border-white/5 rounded-sm p-4">
                                    <p className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider">Free Tier</p>
                                    <p className="text-2xl font-bold text-white font-mono">{metrics.subscription_tiers.free}</p>
                                </div>
                                <div className="bg-amber-900/10 border border-amber-700/20 rounded-sm p-4">
                                    <p className="text-xs text-amber-400 uppercase tracking-wider">Premium Tier</p>
                                    <p className="text-2xl font-bold text-amber-300 font-mono">{metrics.subscription_tiers.premium}</p>
                                </div>
                                <div className="bg-emerald-900/10 border border-emerald-700/20 rounded-sm p-4">
                                    <p className="text-xs text-emerald-400 uppercase tracking-wider">VIP Tier</p>
                                    <p className="text-2xl font-bold text-emerald-300 font-mono">{metrics.subscription_tiers.vip}</p>
                                </div>
                            </div>

                            {/* ── Account Growth History Chart ── */}
                            <UserGrowthChart data={growthData} />
                        </div>
                    )}
                </CollapsibleSection>

                {/* ── Section: Routine Operations ── */}
                <CollapsibleSection id="routine" title="Routine Operations" icon="📅" defaultOpen={false} accentColor="cyan">
                    <div className="flex flex-wrap gap-3">
                        <button
                            onClick={handleSupplementalRefresh}
                            disabled={loadingBtn === "supp-refresh"}
                            className={`${btnBase} bg-cyan-900/40 hover:bg-cyan-800/60 text-cyan-200 border-cyan-700/50`}
                        >
                            {loadingBtn === "supp-refresh" ? <Spinner /> : "✨"} Smart Supplemental Refresh
                        </button>

                        <button
                            onClick={handleSyncAllDividends}
                            disabled={syncProgress !== null || loadingBtn === "sync-div"}
                            className={`${btnBase} bg-amber-900/40 hover:bg-amber-800/60 text-amber-200 border-amber-700/50`}
                        >
                            {syncProgress !== null ? <Spinner /> : "💰"} {syncProgress !== null ? "Syncing Dividends..." : "Sync All Dividends"}
                        </button>

                        <button
                            onClick={handleDbBackup}
                            disabled={loadingBtn === "db-backup"}
                            className={`${btnBase} bg-gray-800/60 hover:bg-gray-700/80 text-gray-200 border-gray-600/50`}
                        >
                            {loadingBtn === "db-backup" ? <Spinner /> : "💾"} GitHub Backup (DB)
                        </button>
                    </div>
                </CollapsibleSection>

                {/* ── Section: Maintenance ── */}
                <CollapsibleSection id="maintenance" title="Maintenance & Repair" icon="🛠️" defaultOpen={false} accentColor="red">
                    <div className="flex flex-wrap gap-3">
                        <button
                            onClick={async () => {
                                if (!confirm("⚠️ START FULL ANALYSIS?\nThis is a standard Smart Analysis run (~2-3 min).")) return;
                                await handleCrawl(false);
                            }}
                            disabled={loadingBtn === "crawl-full"}
                            className={`${btnBase} bg-gray-800/60 hover:bg-gray-700/80 text-gray-200 border-gray-600/50`}
                        >
                            {loadingBtn === "crawl-full" ? <Spinner /> : "🕷️"} Crawler Analysis (Full)
                        </button>

                        <button
                            onClick={async () => {
                                if (!confirm("⚠️ FORCE REBUILD ALL DATA?\nThis will clear current year cache and re-fetch everything (~5-6 min).")) return;
                                await handleCrawl(true);
                            }}
                            disabled={loadingBtn === "crawl-force"}
                            className={`${btnBase} bg-red-900/40 hover:bg-red-800/60 text-red-200 border-red-700/50`}
                        >
                            {loadingBtn === "crawl-force" ? <Spinner /> : "🔥"} Force Rebuild (Cold)
                        </button>

                        <button
                            onClick={handleRebuildPrewarm}
                            disabled={monitorPrewarm || loadingBtn === "rebuild"}
                            className={`${btnBase} bg-amber-900/40 hover:bg-amber-800/60 text-amber-200 border-amber-700/50`}
                        >
                            {monitorPrewarm ? <Spinner /> : "📦"} {monitorPrewarm ? "Pushing to GitHub..." : "Rebuild Pre-warm Data"}
                        </button>
                    </div>
                </CollapsibleSection>

                {/* ── Section: System Tools ── */}
                <CollapsibleSection id="system" title="System Tools & Deep Universe" icon="⚙️" defaultOpen={false} accentColor="gray">
                    <div className="flex flex-wrap gap-3">
                        <button
                            onClick={handleInitializeCache}
                            disabled={loadingBtn === "init-cache"}
                            className={`${btnBase} bg-emerald-900/40 hover:bg-emerald-800/60 text-emerald-200 border-emerald-700/50`}
                        >
                            {loadingBtn === "init-cache" ? <Spinner /> : "🔋"} Reload Price Cache (Force)
                        </button>

                        <button
                            onClick={handleCopyMetrics}
                            className={`${btnBase} bg-gray-800/60 hover:bg-gray-700/80 text-gray-200 border-gray-600/50`}
                        >
                            🔗 Copy Metrics URL
                        </button>

                        {/* Backfill Controls */}
                        <div className="w-full flex flex-col gap-2 bg-black/30 px-4 py-3 rounded-sm border border-white/5 mt-2">
                            <div className="flex items-center gap-6 flex-wrap">
                                <label className="flex items-center gap-2 text-xs cursor-pointer select-none">
                                    <input
                                        type="checkbox"
                                        checked={safeMode}
                                        onChange={(e) => setSafeMode(e.target.checked)}
                                        className="w-3 h-3 accent-cyan-500 rounded-sm"
                                    />
                                    <span className={safeMode ? "text-cyan-400" : "text-orange-400 font-bold"}>
                                        {safeMode ? "🛡️ Safe Mode" : "⚠️ Overwrite"}
                                    </span>
                                </label>
                                <label className="flex items-center gap-2 text-xs cursor-pointer select-none">
                                    <input
                                        type="checkbox"
                                        checked={pushToGithub}
                                        onChange={(e) => setPushToGithub(e.target.checked)}
                                        className="w-3 h-3 accent-amber-500 rounded-sm"
                                    />
                                    <span className={pushToGithub ? "text-amber-400 font-bold" : "text-gray-500"}>
                                        {pushToGithub ? "📤 Push to GitHub (Remote)" : "🏠 Zeabur Local Only"}
                                    </span>
                                </label>
                                <label className="flex items-center gap-2 text-xs cursor-pointer select-none">
                                    <input
                                        type="checkbox"
                                        checked={deepUniverse}
                                        onChange={(e) => setDeepUniverse(e.target.checked)}
                                        className="w-3 h-3 accent-emerald-500 rounded-sm"
                                    />
                                    <span className={deepUniverse ? "text-emerald-400 font-bold" : "text-gray-500"}>
                                        {deepUniverse ? "🌌 Deep Universe (Incl. Warrants)" : "🔭 Smart Universe (Stocks/ETFs)"}
                                    </span>
                                </label>
                            </div>
                            <button
                                onClick={handleBackfill}
                                disabled={loadingBtn === "backfill"}
                                className={`${btnBase} bg-cyan-900/40 hover:bg-cyan-800/60 text-cyan-200 border-cyan-700/50 w-full justify-center text-xs`}
                            >
                                {loadingBtn === "backfill" ? <Spinner /> : "🚀"} Universe Backfill (2000+)
                            </button>
                        </div>
                    </div>
                </CollapsibleSection>

                {/* ── Section: Feedback ── */}
                <CollapsibleSection id="feedback" title="User Feedback & Bug Reports" icon="📬" defaultOpen={true} accentColor="amber">
                    {/* Stats Row */}
                    <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 mb-4">
                        <div className="bg-red-900/15 border border-red-700/30 p-3 rounded-sm text-center">
                            <span className="text-xl font-bold text-red-400 font-mono">{feedbackStats.new}</span>
                            <p className="text-[10px] text-red-300 uppercase tracking-widest">New</p>
                        </div>
                        <div className="bg-amber-900/15 border border-amber-700/30 p-3 rounded-sm text-center">
                            <span className="text-xl font-bold text-amber-400 font-mono">{feedbackStats.reviewing}</span>
                            <p className="text-[10px] text-amber-300 uppercase tracking-widest">Reviewing</p>
                        </div>
                        <div className="bg-cyan-900/15 border border-cyan-700/30 p-3 rounded-sm text-center">
                            <span className="text-xl font-bold text-cyan-400 font-mono">{feedbackStats.confirmed}</span>
                            <p className="text-[10px] text-cyan-300 uppercase tracking-widest">Confirmed</p>
                        </div>
                        <div className="bg-emerald-900/15 border border-emerald-700/30 p-3 rounded-sm text-center">
                            <span className="text-xl font-bold text-emerald-400 font-mono">{feedbackStats.fixed}</span>
                            <p className="text-[10px] text-emerald-300 uppercase tracking-widest">Fixed</p>
                        </div>
                        <div className="bg-gray-800/40 border border-gray-700/30 p-3 rounded-sm text-center">
                            <span className="text-xl font-bold text-gray-400 font-mono">{feedbackStats.wontfix}</span>
                            <p className="text-[10px] text-gray-400 uppercase tracking-widest">Won&apos;t Fix</p>
                        </div>
                    </div>

                    <div className="flex justify-end mb-2">
                        <button onClick={fetchFeedback} className="text-xs bg-cyan-600 px-3 py-1 rounded-sm hover:bg-cyan-500 transition text-white">
                            🔄 Refresh
                        </button>
                    </div>

                    {/* Feedback List */}
                    <div className="bg-black/20 rounded-sm overflow-hidden max-h-[500px] overflow-y-auto border border-white/5">
                        {loadingFeedback ? (
                            <div className="p-6 text-center flex items-center justify-center gap-2 text-[var(--color-text-muted)]">
                                <Spinner />
                                <span className="text-xs">Loading feedback...</span>
                            </div>
                        ) : feedbackList.length === 0 ? (
                            <div className="p-6 text-center text-[var(--color-text-muted)] text-sm">No feedback reports yet</div>
                        ) : (
                            feedbackList.map((fb) => (
                                <div key={fb.id} className="p-4 border-b border-white/5 hover:bg-white/[0.02] transition-colors">
                                    <div className="flex justify-between items-start mb-2">
                                        <div className="flex items-center gap-2">
                                            <span className={`text-[10px] px-2 py-0.5 rounded-sm ${getTypeColor(fb.feedback_type)}`}>
                                                {getTypeIcon(fb.feedback_type)} {fb.feedback_type}
                                            </span>
                                            <span className="text-[10px] text-[var(--color-text-muted)] font-mono">{fb.feature_category}</span>
                                        </div>
                                        <span className="text-[10px] text-[var(--color-text-muted)] font-mono">{fb.created_at?.substring(0, 10)}</span>
                                    </div>
                                    <p className="text-sm text-gray-300 mb-2 leading-relaxed">{fb.message}</p>
                                    <div className="flex items-center gap-3 text-xs flex-wrap">
                                        <span className="text-[var(--color-text-muted)] font-mono text-[10px]">
                                            {fb.user_email || "Anonymous"}
                                        </span>
                                        <button
                                            onClick={() => copyFeedbackToJira(fb)}
                                            className="text-cyan-400 hover:text-white transition text-[10px] flex items-center gap-1"
                                        >
                                            📋 Copy as JIRA
                                        </button>
                                        <select
                                            value={fb.status}
                                            onChange={(e) => updateFeedbackStatus(fb.id, e.target.value)}
                                            className="ml-auto bg-gray-900 border border-gray-700 rounded-sm px-2 py-1 text-[10px] text-white outline-none focus:border-cyan-500 transition"
                                        >
                                            <option value="new">🔴 New</option>
                                            <option value="reviewing">🟡 Reviewing</option>
                                            <option value="confirmed">🔵 Confirmed</option>
                                            <option value="fixed">🟢 Fixed</option>
                                            <option value="wontfix">⚫ Won&apos;t Fix</option>
                                        </select>
                                    </div>

                                    {/* Agent Notes */}
                                    {fb.agent_notes || fb.showNotes ? (
                                        <div className="mt-2">
                                            <textarea
                                                defaultValue={fb.agent_notes}
                                                rows={2}
                                                className="w-full bg-gray-900 border border-gray-700 rounded-sm px-2 py-1 text-xs text-gray-300 outline-none focus:border-cyan-500 transition resize-none"
                                                placeholder="Agent notes..."
                                                onBlur={(e) => updateFeedbackNotes(fb.id, e.target.value)}
                                            />
                                        </div>
                                    ) : (
                                        <button
                                            onClick={() => setFeedbackList(prev => prev.map(item => (item.id === fb.id ? { ...item, showNotes: true } : item)))}
                                            className="mt-1 text-[10px] text-[var(--color-text-muted)] hover:text-cyan-400 transition"
                                        >
                                            + Add agent notes
                                        </button>
                                    )}
                                </div>
                            ))
                        )}
                    </div>

                    <div className="text-[10px] text-[var(--color-text-muted)] text-center mt-4 font-mono tracking-widest uppercase">
                        Admin access only • {new Date().getFullYear()} Marffet Investment
                    </div>
                </CollapsibleSection>

                {/* ── Section: Membership Injection ── */}
                <CollapsibleSection id="memberships" title="Membership Injection" icon="👑" defaultOpen={false} accentColor="emerald">
                    <div className="flex flex-col gap-6">
                        {/* Injection Form */}
                        <div className="bg-black/30 border border-emerald-900/30 rounded-sm p-4">
                            <h3 className="text-sm font-semibold text-emerald-400 mb-3 flex items-center gap-2">
                                🪄 Inject Membership
                            </h3>
                            <div className="grid grid-cols-1 md:grid-cols-4 gap-3 items-end">
                                <div className="flex flex-col gap-1">
                                    <label className="text-xs text-gray-400">User Email</label>
                                    <input
                                        type="email"
                                        value={memberEmail}
                                        onChange={(e) => setMemberEmail(e.target.value)}
                                        placeholder="user@example.com"
                                        className="bg-gray-900 border border-gray-700 rounded-sm px-3 py-2 text-sm text-white focus:border-emerald-500 outline-none"
                                    />
                                </div>
                                <div className="flex flex-col gap-1">
                                    <label className="text-xs text-gray-400">Tier</label>
                                    <select
                                        value={memberTier}
                                        onChange={(e) => setMemberTier(e.target.value)}
                                        className="bg-gray-900 border border-gray-700 rounded-sm px-3 py-2 text-sm text-white focus:border-emerald-500 outline-none"
                                    >
                                        <option value="PREMIUM">Premium</option>
                                        <option value="VIP">VIP</option>
                                    </select>
                                </div>
                                <div className="flex flex-col gap-1">
                                    <label className="text-xs text-gray-400">Duration</label>
                                    <select
                                        value={memberDuration}
                                        onChange={(e) => setMemberDuration(e.target.value)}
                                        className="bg-gray-900 border border-gray-700 rounded-sm px-3 py-2 text-sm text-white focus:border-emerald-500 outline-none"
                                    >
                                        <option value="1">1 Month</option>
                                        <option value="3">3 Months</option>
                                        <option value="6">6 Months</option>
                                        <option value="12">1 Year (12 Months)</option>
                                        <option value="240">Lifetime (20 Years)</option>
                                    </select>
                                </div>
                                <div>
                                    <button
                                        onClick={handleInjectMembership}
                                        disabled={loadingBtn === "inject-membership" || !memberEmail}
                                        className={`${btnBase} w-full justify-center bg-emerald-900/40 hover:bg-emerald-800/60 text-emerald-200 border-emerald-700/50 h-[38px]`}
                                    >
                                        {loadingBtn === "inject-membership" ? <Spinner /> : "Inject"}
                                    </button>
                                </div>
                            </div>
                        </div>

                        {/* Injected Memberships Table */}
                        <div className="space-y-3">
                            <div className="flex items-center justify-between">
                                <h3 className="text-sm font-semibold text-gray-300">Active Injections</h3>
                                <button
                                    onClick={fetchMemberships}
                                    className="text-xs text-emerald-500 hover:text-emerald-400 flex items-center gap-1 transition"
                                >
                                    🔄 Refresh
                                </button>
                            </div>

                            <div className="bg-black/20 rounded-sm border border-white/5 overflow-hidden">
                                {loadingMemberships ? (
                                    <div className="p-8 text-center flex items-center justify-center gap-3 text-gray-500">
                                        <Spinner /> <span className="text-sm">Loading Memberships...</span>
                                    </div>
                                ) : memberships.length === 0 ? (
                                    <div className="p-8 text-center text-gray-500 text-sm">
                                        No manually injected memberships found.
                                    </div>
                                ) : (
                                    <div className="overflow-x-auto">
                                        <table className="w-full text-left text-sm whitespace-nowrap">
                                            <thead className="text-xs text-gray-500 bg-black/40 border-b border-white/5 uppercase tracking-wider">
                                                <tr>
                                                    <th className="px-4 py-3 font-medium">Email</th>
                                                    <th className="px-4 py-3 font-medium">Tier</th>
                                                    <th className="px-4 py-3 font-medium">Valid Until</th>
                                                    <th className="px-4 py-3 font-medium">Injected By</th>
                                                    <th className="px-4 py-3 font-medium text-right">Actions</th>
                                                </tr>
                                            </thead>
                                            <tbody className="divide-y divide-white/5">
                                                {memberships.map((m) => (
                                                    <tr key={m.email} className="hover:bg-white/[0.02] transition">
                                                        <td className="px-4 py-3 text-gray-200">{m.email}</td>
                                                        <td className="px-4 py-3">
                                                            <span className={`px-2 py-0.5 rounded-sm text-xs font-medium border ${m.tier === 'VIP'
                                                                ? 'bg-purple-900/30 text-purple-300 border-purple-700/50'
                                                                : 'bg-emerald-900/30 text-emerald-300 border-emerald-700/50'
                                                                }`}>
                                                                {m.tier}
                                                            </span>
                                                        </td>
                                                        <td className="px-4 py-3 text-gray-400 font-mono text-xs">
                                                            {new Date(m.valid_until).toLocaleString()}
                                                        </td>
                                                        <td className="px-4 py-3 text-gray-500 text-xs">{m.injected_by}</td>
                                                        <td className="px-4 py-3 text-right">
                                                            <button
                                                                onClick={() => handleRevokeMembership(m.email)}
                                                                disabled={loadingBtn === `revoke-${m.email}`}
                                                                className="text-red-400 hover:text-red-300 text-xs font-medium transition disabled:opacity-50"
                                                            >
                                                                {loadingBtn === `revoke-${m.email}` ? '...' : 'Revoke'}
                                                            </button>
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </CollapsibleSection>
            </div >
        </div >
    );
}
