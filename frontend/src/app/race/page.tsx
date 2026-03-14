"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import useSWR from "swr";
import { motion, AnimatePresence } from "framer-motion";
import { ChartSkeleton } from "@/components/Skeleton";
import { useLanguage } from "@/lib/i18n/LanguageContext";

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

const fetcher = (url: string) => fetch(url, { credentials: "include" }).then(res => {
    if (!res.ok) throw new Error("Fetch failed");
    return res.json();
});

export default function RacePage() {
    const { t } = useLanguage();
    const [currentYear, setCurrentYear] = useState<number>(2015);
    const [isPlaying, setIsPlaying] = useState(false);
    const [metric, setMetric] = useState<"wealth" | "cagr">("wealth");
    const [user, setUser] = useState<any>(null);

    const [sim, setSim] = useState<SimSettings>({
        startYear: 2006,
        principal: 1000000,
        contribution: 60000,
    });

    const API_BASE = "";
    const isPremium = user?.is_admin || user?.is_premium;

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

    // Fetch user auth status
    const { data: userData } = useSWR(`${API_BASE}/auth/me`, fetcher, { revalidateOnFocus: false, keepPreviousData: true });
    useEffect(() => {
        if (userData) setUser(userData);
    }, [userData]);

    const animationRef = useRef<NodeJS.Timeout | null>(null);
    const chartRef = useRef<HTMLDivElement>(null);

    const TOP_N = 50;

    // SWR Data Fetching for Race
    const { data: rawFrames = [], isValidating: loading } = useSWR<RaceFrame[]>(
        `${API_BASE}/api/race-data?start_year=${sim.startYear}&principal=${sim.principal}&contribution=${sim.contribution}`,
        fetcher,
        {
            revalidateOnFocus: false, // Don't recalculate heavy sim on focus
            revalidateIfStale: false,
            keepPreviousData: true
        }
    );

    const frames = Array.isArray(rawFrames) ? rawFrames : [];

    // Initialize current year on data load
    useEffect(() => {
        if (frames.length > 0 && !isPlaying) {
            setCurrentYear(frames[0].year);
        }
    }, [frames]); // Only runs when fetched data length actually changes

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
        }, 2000);  // 2 seconds per year
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
    // Generate consistent color from string
    const getColor = (id: string) => {
        const colors = [
            "bg-gradient-to-r from-red-500 to-orange-500",
            "bg-gradient-to-r from-orange-500 to-amber-500",
            "bg-gradient-to-r from-amber-400 to-yellow-500",
            "bg-gradient-to-r from-yellow-400 to-lime-500",
            "bg-gradient-to-r from-lime-500 to-green-500",
            "bg-gradient-to-r from-green-500 to-emerald-500",
            "bg-gradient-to-r from-emerald-500 to-teal-500",
            "bg-gradient-to-r from-teal-500 to-cyan-500",
            "bg-gradient-to-r from-cyan-500 to-sky-500",
            "bg-gradient-to-r from-sky-500 to-blue-500",
            "bg-gradient-to-r from-blue-500 to-indigo-500",
            "bg-gradient-to-r from-teal-500 to-cyan-500",
            "bg-gradient-to-r from-cyan-500 to-sky-600",
            "bg-gradient-to-r from-amber-500 to-orange-500",
            "bg-gradient-to-r from-fuchsia-500 to-pink-500",
            "bg-gradient-to-r from-pink-500 to-rose-500",
            "bg-gradient-to-r from-rose-500 to-red-500",
            "bg-gradient-to-r from-slate-400 to-slate-500",
            "bg-gradient-to-r from-zinc-400 to-zinc-500",
            "bg-gradient-to-r from-neutral-400 to-neutral-500",
            "bg-gradient-to-r from-stone-400 to-stone-500",
            "bg-gradient-to-r from-red-400 to-orange-400",
            "bg-gradient-to-r from-orange-400 to-amber-400",
            "bg-gradient-to-r from-amber-300 to-yellow-400",
            "bg-gradient-to-r from-lime-400 to-green-400",
            "bg-gradient-to-r from-emerald-400 to-teal-400",
            "bg-gradient-to-r from-cyan-400 to-sky-400",
            "bg-gradient-to-r from-blue-400 to-indigo-400",
            "bg-gradient-to-r from-teal-400 to-cyan-400",
            "bg-gradient-to-r from-fuchsia-400 to-pink-400",
        ];

        let hash = 0;
        for (let i = 0; i < id.length; i++) {
            hash = id.charCodeAt(i) + ((hash << 5) - hash);
        }

        const index = Math.abs(hash) % colors.length;
        return colors[index];
    };

    return (
        <div className="max-w-6xl mx-auto space-y-4">
            {/* Header */}
            <div className="flex flex-col lg:flex-row lg:justify-between lg:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-600 bg-clip-text text-transparent">
                        {t('Race.Title')}
                    </h1>
                    <p className="text-[var(--color-text-muted)]">
                        {t('Race.Subtitle', { startYear: sim.startYear, maxYear })}
                    </p>
                </div>

                {/* Controls */}
                <div className="flex gap-2">
                    <button
                        onClick={playRace}
                        disabled={isPlaying || loading}
                        className="bg-[var(--color-success)]/20 border border-[var(--color-success)] text-[var(--color-success)] px-4 py-2 rounded hover:bg-[var(--color-success)] hover:text-black transition font-bold text-sm cursor-pointer disabled:opacity-50"
                    >
                        {t('Race.Play')}
                    </button>
                    <button
                        onClick={pauseRace}
                        disabled={!isPlaying}
                        className="bg-[var(--color-warning)]/20 border border-[var(--color-warning)] text-[var(--color-warning)] px-4 py-2 rounded hover:bg-[var(--color-warning)] hover:text-black transition font-bold text-sm cursor-pointer disabled:opacity-50"
                    >
                        {t('Race.Pause')}
                    </button>
                    <button
                        onClick={resetRace}
                        className="bg-white/10 border border-white/20 text-white px-4 py-2 rounded hover:bg-white/20 transition font-bold text-sm cursor-pointer"
                    >
                        {t('Race.Reset')}
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
                    {t('Race.Wealth')}
                </button>
                <button
                    onClick={() => {
                        if (isPremium) {
                            setMetric("cagr"); resetRace();
                        } else {
                            alert(t('Race.PremiumAlert'));
                        }
                    }}
                    className={`px-4 py-2 text-sm font-bold rounded transition cursor-pointer flex items-center gap-1 ${metric === "cagr"
                        ? "bg-[var(--color-cta)] text-black"
                        : "text-[var(--color-text-muted)] hover:text-white"
                        }`}
                >
                    {!isPremium && <span className="text-xs">🔒</span>}
                    {t('Race.CAGR')}
                </button>
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

            {/* Chart */}
            <div className="glass-card rounded-xl p-6" ref={chartRef}>
                {loading ? (
                    <ChartSkeleton height="h-[450px]" />
                ) : currentFrameData.length === 0 ? (
                    <div className="text-center py-20 text-[var(--color-text-muted)]">
                        {t('Race.NoData')}
                    </div>
                ) : (
                    <div className="relative min-h-[450px]">
                        {/* Year Display - Floating Background */}
                        <div className="absolute right-0 bottom-0 text-9xl font-bold text-[var(--color-cta)] font-mono opacity-10 pointer-events-none select-none transition-all duration-700">
                            {currentYear}
                        </div>

                        {/* Bars Container */}
                        <div className="flex flex-col gap-1.5">
                            <AnimatePresence mode="popLayout">
                                {currentFrameData.map((stock, index) => {
                                    const value = metric === "wealth" ? stock.wealth : stock.cagr || 0;
                                    const barWidth = (value / maxValue) * 100;
                                    const rank = index + 1;

                                    return (
                                        <motion.div
                                            key={stock.id}
                                            layout
                                            initial={{ opacity: 0, x: -50 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            exit={{ opacity: 0, scale: 0.9 }}
                                            transition={{
                                                layout: { type: "spring", stiffness: 45, damping: 15 }, // Smooth overtaking
                                                opacity: { duration: 0.3 }
                                            }}
                                            className="flex items-center gap-2 h-7 w-full"
                                        >
                                            {/* Rank */}
                                            <div className="w-8 text-right font-mono text-[var(--color-text-muted)]">
                                                {rank}
                                            </div>

                                            {/* Bar */}
                                            <div className="flex-1 relative h-6">
                                                <motion.div
                                                    initial={{ width: 0 }}
                                                    animate={{ width: `${Math.max(barWidth, 1)}%` }}
                                                    transition={{ duration: 1.5, ease: "linear" }}
                                                    className={`h-full rounded-r ${getColor(stock.id)} shadow-lg flex items-center`}
                                                >
                                                    <span className="px-2 text-sm font-bold text-black truncate drop-shadow-md">
                                                        {stock.name}
                                                    </span>
                                                </motion.div>
                                            </div>

                                            {/* Value */}
                                            <div className="w-24 text-right font-mono font-bold text-[var(--color-primary)]">
                                                {formatValue(value)}
                                            </div>
                                        </motion.div>
                                    );
                                })}
                            </AnimatePresence>
                        </div>
                    </div>
                )}
            </div>

            {/* Configuration removed - Reusing Mars Strategy Settings */}
        </div>
    );
}
