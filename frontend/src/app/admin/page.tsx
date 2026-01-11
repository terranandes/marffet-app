"use client";

import { useEffect, useState } from "react";

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

const MetricCard = ({
    title,
    value,
    subtext,
    color,
}: {
    title: string;
    value: number | string;
    subtext?: string;
    color: string;
}) => (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 hover:border-zinc-700 transition-all">
        <div className="text-zinc-500 text-sm mb-2">{title}</div>
        <div className={`text-4xl font-bold ${color}`}>{value}</div>
        {subtext && <div className="text-zinc-600 text-xs mt-2">{subtext}</div>}
    </div>
);

export default function AdminPage() {
    const [metrics, setMetrics] = useState<AdminMetrics | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch("/api/admin/metrics", { credentials: "include" })
            .then((res) => {
                if (res.status === 403) {
                    throw new Error("Access Denied: Admin privileges required");
                }
                if (res.status === 401) {
                    throw new Error("Please login first");
                }
                if (!res.ok) {
                    throw new Error("Failed to fetch metrics");
                }
                return res.json();
            })
            .then((data) => {
                setMetrics(data);
                setLoading(false);
            })
            .catch((err) => {
                setError(err.message);
                setLoading(false);
            });
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="max-w-4xl mx-auto py-10">
                <div className="bg-red-900/20 border border-red-800 rounded-xl p-6 text-center">
                    <div className="text-red-400 text-xl font-bold mb-2">🚫 {error}</div>
                    <div className="text-zinc-500 text-sm">
                        This page is only accessible to authorized administrators.
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-6xl mx-auto py-10">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-white mb-2">GM Dashboard</h1>
                <p className="text-zinc-500">System metrics and user analytics</p>
            </div>

            {/* User Metrics */}
            <div className="mb-8">
                <h2 className="text-lg font-semibold text-zinc-300 mb-4">
                    User Metrics
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <MetricCard
                        title="Total Registered Users"
                        value={metrics?.total_users || 0}
                        color="text-purple-400"
                    />
                    <MetricCard
                        title="Active Users (Web)"
                        value={metrics?.active_users_web || 0}
                        subtext="Last 30 days"
                        color="text-cyan-400"
                    />
                    <MetricCard
                        title="Active Users (Mobile)"
                        value={metrics?.active_users_mobile || 0}
                        subtext="Last 30 days"
                        color="text-emerald-400"
                    />
                </div>
            </div>

            {/* Subscription Tiers */}
            <div className="mb-8">
                <h2 className="text-lg font-semibold text-zinc-300 mb-4">
                    Subscription Breakdown
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <MetricCard
                        title="Free Tier"
                        value={metrics?.subscription_tiers?.free || 0}
                        color="text-zinc-400"
                    />
                    <MetricCard
                        title="Premium Tier"
                        value={metrics?.subscription_tiers?.premium || 0}
                        color="text-amber-400"
                    />
                    <MetricCard
                        title="VIP Tier"
                        value={metrics?.subscription_tiers?.vip || 0}
                        color="text-pink-400"
                    />
                </div>
            </div>

            <div className="text-xs text-zinc-600 text-center mt-12">
                Data refreshes on page load • Admin access only
            </div>
        </div>
    );
}
