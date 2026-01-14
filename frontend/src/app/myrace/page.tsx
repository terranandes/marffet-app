"use client";

import { useEffect, useState, useCallback, useRef } from "react";

interface RaceDataPoint {
    month: string;
    id: string;
    name: string;
    value: number;
}

interface AssetGroups {
    stock: { stock_id: string; stock_name: string }[];
    etf: { stock_id: string; stock_name: string }[];
    cb: { stock_id: string; stock_name: string }[];
}

export default function MyRacePage() {
    const [raceData, setRaceData] = useState<RaceDataPoint[]>([]);
    const [assetGroups, setAssetGroups] = useState<AssetGroups>({ stock: [], etf: [], cb: [] });
    const [loading, setLoading] = useState(true);
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentMonth, setCurrentMonth] = useState<string>("");
    const [currentFrame, setCurrentFrame] = useState<RaceDataPoint[]>([]);

    const animationRef = useRef<NodeJS.Timeout | null>(null);
    const frameIndexRef = useRef(0);

    const API_BASE = "http://localhost:8000";
    const TOP_N = 10;

    // Fetch race data
    const fetchRaceData = useCallback(async () => {
        setLoading(true);
        try {
            const raceRes = await fetch(`${API_BASE}/api/portfolio/race-data`, { credentials: "include" });
            if (raceRes.ok) {
                const data = await raceRes.json();
                setRaceData(data);
            }

            const groupRes = await fetch(`${API_BASE}/api/portfolio/by-type`, { credentials: "include" });
            if (groupRes.ok) {
                setAssetGroups(await groupRes.json());
            }
        } catch (err) {
            console.error("My Race fetch error:", err);
        }
        setLoading(false);
    }, []);

    useEffect(() => {
        fetchRaceData();
    }, [fetchRaceData]);

    // Get months from data
    const months = [...new Set(raceData.map((d) => d.month))].sort();

    // Play animation
    const playRace = () => {
        if (isPlaying || months.length === 0) return;
        setIsPlaying(true);

        frameIndexRef.current = 0;

        const animate = () => {
            if (frameIndexRef.current >= months.length) {
                setIsPlaying(false);
                return;
            }

            const month = months[frameIndexRef.current];
            setCurrentMonth(month);

            const frameData = raceData
                .filter((d) => d.month === month)
                .sort((a, b) => b.value - a.value)
                .slice(0, TOP_N);
            setCurrentFrame(frameData);

            frameIndexRef.current++;
            animationRef.current = setTimeout(animate, 600);
        };

        animate();
    };

    // Pause animation
    const pauseRace = () => {
        setIsPlaying(false);
        if (animationRef.current) {
            clearTimeout(animationRef.current);
            animationRef.current = null;
        }
    };

    const formatCurrency = (val: number) => {
        if (val >= 1e6) return `$${(val / 1e6).toFixed(1)}M`;
        if (val >= 1e3) return `$${(val / 1e3).toFixed(0)}K`;
        return `$${val.toFixed(0)}`;
    };

    const maxValue = Math.max(...currentFrame.map((d) => d.value), 1);

    const getBarColor = (index: number) => {
        const colors = [
            "from-cyan-400 to-blue-500",
            "from-red-400 to-pink-500",
            "from-yellow-400 to-orange-500",
            "from-green-400 to-emerald-500",
            "from-purple-400 to-violet-500",
            "from-orange-400 to-amber-500",
            "from-pink-400 to-rose-500",
            "from-blue-400 to-indigo-500",
        ];
        return colors[index % colors.length];
    };

    return (
        <div className="max-w-6xl mx-auto space-y-6">
            {/* Header */}
            <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-red-400 to-pink-600 bg-clip-text text-transparent">
                        🏎️ My Race
                    </h1>
                    <p className="text-[var(--color-text-muted)]">
                        Watch your portfolio holdings compete over time
                    </p>
                </div>

                {/* Controls */}
                <div className="flex gap-2">
                    <button
                        onClick={playRace}
                        disabled={isPlaying || raceData.length === 0}
                        className="bg-[var(--color-success)]/20 border border-[var(--color-success)] text-[var(--color-success)] px-4 py-2 rounded hover:bg-[var(--color-success)] hover:text-black transition font-bold text-sm cursor-pointer disabled:opacity-50"
                    >
                        ▶ Play
                    </button>
                    <button
                        onClick={pauseRace}
                        disabled={!isPlaying}
                        className="bg-[var(--color-warning)]/20 border border-[var(--color-warning)] text-[var(--color-warning)] px-4 py-2 rounded hover:bg-[var(--color-warning)] hover:text-black transition font-bold text-sm cursor-pointer disabled:opacity-50"
                    >
                        ⏸ Pause
                    </button>
                    <button
                        onClick={fetchRaceData}
                        className="bg-[var(--color-cta)]/20 border border-[var(--color-cta)] text-[var(--color-cta)] px-4 py-2 rounded hover:bg-[var(--color-cta)] hover:text-black transition font-bold text-sm cursor-pointer"
                    >
                        🔄 Refresh
                    </button>
                </div>
            </div>

            {/* Race Chart */}
            <div className="glass-card rounded-xl p-6 min-h-[400px]">
                {loading ? (
                    <div className="text-center py-20 animate-pulse text-[var(--color-text-muted)]">
                        Loading race data...
                    </div>
                ) : raceData.length === 0 ? (
                    <div className="text-center py-20">
                        <p className="text-6xl mb-4">🏎️</p>
                        <h2 className="text-xl font-bold mb-2 text-[var(--color-text-muted)]">No Race Data Yet</h2>
                        <p className="text-[var(--color-text-muted)]">
                            Add transactions in Portfolio tab to see your investments race!
                        </p>
                        <a
                            href="/portfolio"
                            className="inline-block mt-4 bg-[var(--color-cta)] text-black px-4 py-2 rounded font-bold"
                        >
                            Go to Portfolio →
                        </a>
                    </div>
                ) : currentFrame.length === 0 ? (
                    <div className="text-center py-20">
                        <p className="text-[var(--color-cta)] text-lg mb-2">
                            {raceData.length} data points ready
                        </p>
                        <p className="text-[var(--color-text-muted)]">
                            Click Play to start the race!
                        </p>
                    </div>
                ) : (
                    <div className="space-y-2">
                        {/* Month Display */}
                        <div className="text-right text-5xl font-bold text-[var(--color-cta)] font-mono mb-4">
                            {currentMonth}
                        </div>

                        {/* Bars */}
                        {currentFrame.map((item, index) => {
                            const barWidth = (item.value / maxValue) * 100;

                            return (
                                <div key={item.id} className="flex items-center gap-3 h-10">
                                    {/* Rank */}
                                    <div className="w-8 text-right font-mono text-[var(--color-text-muted)]">
                                        {index + 1}
                                    </div>

                                    {/* Name */}
                                    <div className="w-24 text-right text-sm font-medium truncate">
                                        {item.name || item.id}
                                    </div>

                                    {/* Bar */}
                                    <div className="flex-1 h-8 bg-black/30 rounded overflow-hidden">
                                        <div
                                            className={`h-full bg-gradient-to-r ${getBarColor(index)} transition-all duration-500 ease-out`}
                                            style={{ width: `${Math.max(barWidth, 3)}%` }}
                                        />
                                    </div>

                                    {/* Value */}
                                    <div className="w-20 text-right font-mono font-bold text-white">
                                        {formatCurrency(item.value)}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>

            {/* Asset Stats */}
            <div className="glass-card rounded-xl p-4">
                <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                        <div className="text-2xl font-bold text-[var(--color-cta)]">
                            {assetGroups.stock?.length || 0}
                        </div>
                        <div className="text-xs text-[var(--color-text-muted)]">Stocks</div>
                    </div>
                    <div>
                        <div className="text-2xl font-bold text-[var(--color-primary)]">
                            {assetGroups.etf?.length || 0}
                        </div>
                        <div className="text-xs text-[var(--color-text-muted)]">ETFs</div>
                    </div>
                    <div>
                        <div className="text-2xl font-bold text-[var(--color-success)]">
                            {assetGroups.cb?.length || 0}
                        </div>
                        <div className="text-xs text-[var(--color-text-muted)]">CBs</div>
                    </div>
                </div>
            </div>
        </div>
    );
}
