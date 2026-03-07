"use client";

import { useState } from "react";
import useSWR from "swr";
import ShareButton from "@/components/ShareButton";
import { LeaderboardSkeleton } from "@/components/Skeleton";
import { useLanguage } from "@/lib/i18n/LanguageContext";

interface LeaderboardEntry {
    id: string;
    nickname: string;
    avatar?: string;
    market_value: number;
    roi: number;
    total_cost: number;
    rank?: number;
    holdings_count?: number;
}

const fetcher = (url: string) => fetch(url, { credentials: "include" }).then(res => {
    if (!res.ok) throw new Error("Fetch failed");
    return res.json();
});

export default function LadderPage() {
    const { t } = useLanguage();

    const [showProfileModal, setShowProfileModal] = useState(false);
    const [profileData, setProfileData] = useState<{
        nickname: string;
        roi?: number;
        holdings?: { stock_id: string; stock_name: string; shares: number }[];
        allocation?: { name: string; pct: number }[];
    } | null>(null);

    const API_BASE = "";

    // SWR Data Fetching for Leaderboard
    const { data: rawData = [], isValidating: loading, mutate: fetchLeaderboard } = useSWR<LeaderboardEntry[]>(
        `${API_BASE}/api/leaderboard`,
        fetcher,
        {
            revalidateOnFocus: false
        }
    );

    const leaderboard = Array.isArray(rawData) ? rawData : [];

    // Open user profile modal
    const openProfile = async (userId: string) => {
        try {
            const res = await fetch(`${API_BASE}/api/public/profile/${userId}`, { credentials: "include" });
            if (res.ok) {
                const data = await res.json();
                setProfileData(data);
                setShowProfileModal(true);
            }
        } catch (err) {
            console.error("Profile fetch error:", err);
        }
    };

    const formatCurrency = (val: number) => {
        if (val >= 1e9) return `$${(val / 1e9).toFixed(1)}B`;
        if (val >= 1e6) return `$${(val / 1e6).toFixed(1)}M`;
        if (val >= 1e3) return `$${(val / 1e3).toFixed(0)}K`;
        return `$${val.toFixed(0)}`;
    };

    const getRankBadge = (rank: number) => {
        if (rank === 1) return "🥇";
        if (rank === 2) return "🥈";
        if (rank === 3) return "🥉";
        return null;
    };

    const getRankColor = (rank: number) => {
        if (rank === 1) return "from-yellow-400 to-amber-600";
        if (rank === 2) return "from-gray-300 to-gray-500";
        if (rank === 3) return "from-amber-600 to-orange-700";
        if (rank <= 10) return "from-amber-500 to-orange-700";
        return "from-zinc-600 to-zinc-700";
    };

    return (
        <div className="max-w-3xl mx-auto space-y-6">
            {/* Header */}
            <div className="text-center">
                <h1 className="text-3xl font-bold bg-gradient-to-r from-yellow-400 to-orange-600 bg-clip-text text-transparent">
                    {t('Ladder.Title')}
                </h1>
                <p className="text-[var(--color-text-muted)]">
                    {t('Ladder.Subtitle')}
                </p>
            </div>

            {/* Leaderboard */}
            <div className="glass-card rounded-xl overflow-hidden">
                {loading ? (
                    <LeaderboardSkeleton rows={8} />
                ) : leaderboard.length === 0 ? (
                    <div className="text-center py-20 text-[var(--color-text-muted)]">
                        <p className="text-6xl mb-4">🏆</p>
                        <h2 className="text-xl font-bold mb-2">{t('Ladder.NoRankings')}</h2>
                        <p>{t('Ladder.BeFirst')}</p>
                    </div>
                ) : (
                    <div className="divide-y divide-[var(--color-border)]">
                        {leaderboard.map((user, index) => {
                            const rank = index + 1;
                            const badge = getRankBadge(rank);

                            return (
                                <div
                                    key={user.id}
                                    onClick={() => openProfile(user.id)}
                                    className="flex items-center gap-4 p-4 hover:bg-white/5 transition cursor-pointer"
                                >
                                    {/* Rank Badge */}
                                    <div
                                        className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg bg-gradient-to-br ${getRankColor(rank)} shadow-lg flex-shrink-0`}
                                    >
                                        {badge ? (
                                            <span className="text-2xl">{badge}</span>
                                        ) : (
                                            <span className="text-black">{rank}</span>
                                        )}
                                    </div>

                                    {/* User Info */}
                                    <div className="flex-1 min-w-0">
                                        <div className="font-bold text-white truncate flex items-center gap-2">
                                            {user.avatar && (
                                                <img
                                                    src={user.avatar}
                                                    alt=""
                                                    className="w-6 h-6 rounded-full"
                                                />
                                            )}
                                            {user.nickname || `${t('Ladder.Anonymous')} ${user.id.substring(0, 8)}`}
                                        </div>
                                        <div className="text-xs text-[var(--color-text-muted)]">
                                            {t('Ladder.Invested')}: {user.holdings_count || "?"} {t('Ladder.Assets')}
                                        </div>
                                    </div>

                                    {/* Stats */}
                                    <div className="text-right flex-shrink-0">
                                        <div
                                            className={`text-sm font-mono font-bold ${(user.roi || 0) >= 0 ? "text-[var(--color-success)]" : "text-[var(--color-danger)]"
                                                }`}
                                        >
                                            {(user.roi || 0) >= 0 ? "▲" : "▼"} {Math.abs(user.roi || 0).toFixed(1)}% ROI
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>

            {/* Sync Stats Button */}
            <div className="text-center">
                <p className="text-sm text-[var(--color-text-muted)] mb-2">
                    {t('Ladder.SyncInfo')}
                </p>
                <button
                    onClick={async () => {
                        try {
                            const res = await fetch(`${API_BASE}/api/portfolio/sync-stats`, {
                                method: "POST",
                                credentials: "include",
                            });
                            if (res.ok) {
                                const data = await res.json();
                                alert(t('Ladder.RankSynced').replace('{roi}', data.roi));
                                fetchLeaderboard();
                            }
                        } catch (err) {
                            console.error("Sync error:", err);
                        }
                    }}
                    className="bg-[var(--color-cta)]/20 border border-[var(--color-cta)] text-[var(--color-cta)] px-6 py-2 rounded-lg hover:bg-[var(--color-cta)] hover:text-black transition font-bold cursor-pointer"
                >
                    {t('Ladder.SyncMyStats')}
                </button>
            </div>

            {/* Share Button (Fixed Bottom-Right for Mobile or Header) */}
            <div className="fixed bottom-6 right-6 z-40 md:static md:text-center md:mt-4">
                <ShareButton
                    text={`Check out the Marffet Investment Leaderboard! 🏆`}
                    label={t('Ladder.ShareRankings')}
                />
            </div>

            {/* Profile Modal */}
            {
                showProfileModal && profileData && (
                    <div
                        className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4"
                        onClick={() => setShowProfileModal(false)}
                    >
                        <div
                            className="glass-card rounded-xl p-6 max-w-md w-full"
                            onClick={(e) => e.stopPropagation()}
                        >
                            <div className="flex justify-between items-start mb-4">
                                <h2 className="text-xl font-bold">{profileData.nickname || t('Ladder.Anonymous')}</h2>
                                <div className="flex gap-2">
                                    <ShareButton
                                        title={`${profileData.nickname}'s Portfolio`}
                                        text={`Check out ${profileData.nickname}'s performance on Marffet! ROI: ${profileData.roi || 0}%`}
                                        label={t('Ladder.Share')}
                                    />
                                    <button
                                        onClick={() => setShowProfileModal(false)}
                                        className="text-[var(--color-text-muted)] hover:text-white"
                                    >
                                        ✕
                                    </button>
                                </div>
                            </div>

                            {/* Holdings */}
                            {profileData.holdings && profileData.holdings.length > 0 && (
                                <div className="mb-4">
                                    <h3 className="text-sm font-bold text-[var(--color-text-muted)] mb-2">
                                        {t('Ladder.TopHoldings')}
                                    </h3>
                                    <div className="space-y-1">
                                        {profileData.holdings.slice(0, 5).map((h) => (
                                            <div key={h.stock_id} className="flex justify-between text-sm">
                                                <span>{h.stock_name || h.stock_id}</span>
                                                {/* Privacy: Hide exact shares */}
                                                {/* <span className="font-mono">{h.shares} shares</span> */}
                                                <span className="text-xs bg-white/10 px-2 py-0.5 rounded">{t('Ladder.Holding')}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Allocation */}
                            {profileData.allocation && profileData.allocation.length > 0 && (
                                <div>
                                    <h3 className="text-sm font-bold text-[var(--color-text-muted)] mb-2">
                                        {t('Ladder.Allocation')}
                                    </h3>
                                    <div className="h-4 rounded-full overflow-hidden flex">
                                        {profileData.allocation.map((a, i) => (
                                            <div
                                                key={i}
                                                style={{ width: `${a.pct}%` }}
                                                className={`h-full ${i === 0 ? "bg-[var(--color-cta)]" :
                                                    i === 1 ? "bg-[var(--color-primary)]" :
                                                        i === 2 ? "bg-[var(--color-success)]" :
                                                            "bg-[var(--color-warning)]"
                                                    }`}
                                                title={`${a.name}: ${a.pct}%`}
                                            />
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )
            }
        </div >
    );
}
