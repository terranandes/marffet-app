"use client";

import { useEffect, useState, useRef, useCallback } from "react";

interface RaceFrame {
    year: number;
    id: string;
    name: string;
    wealth: number;
    cagr?: number;
    roi?: number;
}

interface SimSettings {
    startYear: number;
    principal: number;
    contribution: number;
}

export default function RacePage() {
    const [frames, setFrames] = useState<RaceFrame[]>([]);
    const [currentYear, setCurrentYear] = useState<number>(2015);
    const [isPlaying, setIsPlaying] = useState(false);
    const [loading, setLoading] = useState(true);
    const [metric, setMetric] = useState<"wealth" | "cagr">("wealth");

    const [sim, setSim] = useState<SimSettings>({
        startYear: 2006,
        principal: 1000000,
        contribution: 60000,
    });

    // Load settings from Mars page (localStorage)
    useEffect(() => {
        const saved = localStorage.getItem("mars_sim_settings");
        if (saved) {
            try {
                const parsed = JSON.parse(saved);
                setSim({
                    startYear: parsed.startYear || 2006,
                    principal: parsed.principal || 1000000,
                    contribution: parsed.contribution || 60000
                });
            } catch (e) {
                console.error("Failed to parse mars settings", e);
            }
        }
    }, []);

    const animationRef = useRef<NodeJS.Timeout | null>(null);
    const chartRef = useRef<HTMLDivElement>(null);

    const TOP_N = 20;
    const API_BASE = "";

    // Fetch race data
    const fetchRaceData = useCallback(async () => {
        setLoading(true);
        try {
            const res = await fetch(
                `${API_BASE}/api/race-data?start_year=${sim.startYear}&principal=${sim.principal}&contribution=${sim.contribution}`
            );
            if (res.ok) {
                const data = await res.json();
                setFrames(data);
                if (data.length > 0) {
                    setCurrentYear(data[0].year);
                }
            }
        } catch (err) {
            console.error("Failed to fetch race data:", err);
        }
        setLoading(false);
    }, [sim]);

    useEffect(() => {
        fetchRaceData();
    }, [fetchRaceData]);

    // Get years from data
    const years = [...new Set(frames.map((f) => f.year))].sort((a, b) => a - b);
    const minYear = years[0] || sim.startYear;
    const maxYear = years[years.length - 1] || new Date().getFullYear();

    // Get current frame data
    const currentFrameData = frames
        .filter((f) => f.year === currentYear)
        .sort((a, b) => (metric === "wealth" ? b.wealth - a.wealth : (b.cagr || 0) - (a.cagr || 0)))
        .slice(0, TOP_N);

    // Calculate max value for scaling
    const maxValue = Math.max(
        ...currentFrameData.map((f) => (metric === "wealth" ? f.wealth : f.cagr || 0)),
        1
    );

    // Play animation
    const playRace = () => {
        if (isPlaying) return;
        setIsPlaying(true);

        let yearIndex = years.indexOf(currentYear);
        if (yearIndex === years.length - 1) yearIndex = 0;

        animationRef.current = setInterval(() => {
            yearIndex++;
            if (yearIndex >= years.length) {
                pauseRace();
                return;
            }
            setCurrentYear(years[yearIndex]);
        }, 1000);
    };

    // Pause animation
    const pauseRace = () => {
        setIsPlaying(false);
        if (animationRef.current) {
            clearInterval(animationRef.current);
            animationRef.current = null;
        }
    };

    // Reset to start
    const resetRace = () => {
        pauseRace();
        setCurrentYear(minYear);
    };

    // Seek to year
    const seekToYear = (year: number) => {
        pauseRace();
        setCurrentYear(year);
    };

    // Format currency
    const formatValue = (val: number) => {
        if (metric === "cagr") return `${val.toFixed(1)}%`;
        if (val >= 1e9) return `$${(val / 1e9).toFixed(1)}B`;
        if (val >= 1e6) return `$${(val / 1e6).toFixed(1)}M`;
        if (val >= 1e3) return `$${(val / 1e3).toFixed(0)}K`;
        return `$${val.toFixed(0)}`;
    };

    // Bar colors based on rank
    const getBarColor = (index: number) => {
        const colors = [
            "bg-gradient-to-r from-yellow-400 to-amber-500", // Gold
            "bg-gradient-to-r from-gray-300 to-gray-400",    // Silver
            "bg-gradient-to-r from-amber-600 to-orange-600", // Bronze
            "bg-gradient-to-r from-purple-500 to-violet-600",
            "bg-gradient-to-r from-cyan-400 to-blue-500",
            "bg-gradient-to-r from-green-400 to-emerald-500",
        ];
        return colors[index] || "bg-gradient-to-r from-zinc-500 to-zinc-600";
    };

    return (
        <div className="max-w-6xl mx-auto space-y-4">
            {/* Header */}
            <div className="flex flex-col lg:flex-row lg:justify-between lg:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-600 bg-clip-text text-transparent">
                        🏎️ Bar Chart Race
                    </h1>
                    <p className="text-[var(--color-text-muted)]">
                        Watch stocks compete from {sim.startYear} to {maxYear}
                    </p>
                </div>

                {/* Controls */}
                <div className="flex gap-2">
                    <button
                        onClick={playRace}
                        disabled={isPlaying || loading}
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
                        onClick={resetRace}
                        className="bg-white/10 border border-white/20 text-white px-4 py-2 rounded hover:bg-white/20 transition font-bold text-sm cursor-pointer"
                    >
                        ↺ Reset
                    </button>
                </div>
            </div>

            {/* Metric Toggle */}
            <div className="flex bg-black/50 rounded-lg p-1 border border-[var(--color-border)] w-fit">
                <button
                    onClick={() => { setMetric("wealth"); resetRace(); }}
                    className={`px-4 py-2 text-sm font-bold rounded transition cursor-pointer ${metric === "wealth"
                        ? "bg-[var(--color-cta)] text-black"
                        : "text-[var(--color-text-muted)] hover:text-white"
                        }`}
                >
                    💰 Wealth
                </button>
                <button
                    onClick={() => { setMetric("cagr"); resetRace(); }}
                    className={`px-4 py-2 text-sm font-bold rounded transition cursor-pointer ${metric === "cagr"
                        ? "bg-[var(--color-cta)] text-black"
                        : "text-[var(--color-text-muted)] hover:text-white"
                        }`}
                >
                    📈 CAGR
                </button>
            </div>

            {/* Chart */}
            <div className="glass-card rounded-xl p-6" ref={chartRef}>
                {loading ? (
                    <div className="text-center py-20 animate-pulse text-[var(--color-text-muted)]">
                        Loading race data...
                    </div>
                ) : currentFrameData.length === 0 ? (
                    <div className="text-center py-20 text-[var(--color-text-muted)]">
                        No data available for this period.
                    </div>
                ) : (
                    <div className="space-y-2">
                        {/* Year Display */}
                        <div className="text-right text-6xl font-bold text-[var(--color-cta)] font-mono mb-4 opacity-80">
                            {currentYear}
                        </div>

                        {/* Bars */}
                        {currentFrameData.map((stock, index) => {
                            const value = metric === "wealth" ? stock.wealth : stock.cagr || 0;
                            const barWidth = (value / maxValue) * 100;

                            return (
                                <div key={stock.id} className="flex items-center gap-3 h-10">
                                    {/* Rank */}
                                    <div className="w-8 text-right font-mono text-[var(--color-text-muted)]">
                                        {index + 1}
                                    </div>

                                    {/* Bar */}
                                    <div className="flex-1 relative h-8">
                                        <div
                                            className={`h-full rounded-r ${getBarColor(index)} transition-all duration-500 ease-out flex items-center`}
                                            style={{ width: `${Math.max(barWidth, 5)}%` }}
                                        >
                                            <span className="px-2 text-sm font-bold text-black truncate">
                                                {stock.name}
                                            </span>
                                        </div>
                                    </div>

                                    {/* Value */}
                                    <div className="w-24 text-right font-mono font-bold text-[var(--color-primary)]">
                                        {formatValue(value)}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>

            {/* Timeline Scrubber */}
            <div className="glass-card rounded-xl p-4">
                <div className="flex items-center gap-4">
                    <span className="text-[var(--color-cta)] font-mono font-bold w-12">
                        {currentYear}
                    </span>
                    <input
                        type="range"
                        min={0}
                        max={years.length - 1}
                        value={years.indexOf(currentYear)}
                        onChange={(e) => seekToYear(years[Number(e.target.value)])}
                        className="flex-1 h-2 bg-[var(--color-border)] rounded-full appearance-none cursor-pointer"
                        style={{ accentColor: "var(--color-cta)" }}
                    />
                    <span className="text-[var(--color-text-muted)] font-mono w-12 text-right">
                        {maxYear}
                    </span>
                </div>
            </div>

            {/* Configuration removed - Reusing Mars Strategy Settings */}
        </div>
    );
}
