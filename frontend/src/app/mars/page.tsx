"use client";

import { useEffect, useState, useMemo } from "react";

interface Stock {
    id: string;
    name: string;
    price: number;
    cagr_pct: number;
    cagr_std: number;
    valid_years: number;
    volatility_pct?: number;
    finalValue?: number;
}

interface SimSettings {
    startYear: number;
    principal: number;
    contribution: number;
}

type SortKey = "finalValue" | "cagr_pct" | "volatility_pct" | "name";
type SortDir = "asc" | "desc";

export default function MarsPage() {
    const [stocks, setStocks] = useState<Stock[]>([]);
    const [loading, setLoading] = useState(true);
    const [isCalculating, setIsCalculating] = useState(false);

    // Simulation settings
    const [sim, setSim] = useState<SimSettings>({
        startYear: 2006,
        principal: 1000000,
        contribution: 60000,
    });

    // Mobile Settings Toggle
    const [showSettings, setShowSettings] = useState(false);

    // Load settings from local storage on mount
    useEffect(() => {
        const saved = localStorage.getItem("mars_sim_settings");
        if (saved) {
            try {
                setSim(JSON.parse(saved));
            } catch (e) { console.error("Failed to parse settings", e); }
        }
    }, []);

    // Save settings to local storage on change
    useEffect(() => {
        localStorage.setItem("mars_sim_settings", JSON.stringify(sim));
    }, [sim]);

    // Sorting
    const [sortKey, setSortKey] = useState<SortKey>("finalValue");
    const [sortDir, setSortDir] = useState<SortDir>("desc");

    const currentYear = new Date().getFullYear();

    // Fetch stocks with simulation
    const fetchStocks = async () => {
        setIsCalculating(true);
        try {
            const res = await fetch(
                `/api/results?start_year=${sim.startYear}&principal=${sim.principal}&contribution=${sim.contribution}`
            );
            const data = await res.json();
            if (Array.isArray(data)) {
                // Calculate simulated final value for each stock
                const processed = data.map((stock: Stock) => ({
                    ...stock,
                    finalValue: calculateFinalValue(stock, sim),
                    volatility_pct: stock.cagr_std ? stock.cagr_std * 100 / (stock.cagr_pct || 1) : 0,
                }));
                setStocks(processed);
            }
        } catch (err) {
            console.error("Failed to fetch stocks:", err);
            setStocks([]);
        }
        setLoading(false);
        setIsCalculating(false);
    };

    // Simple final value calculation based on CAGR
    const calculateFinalValue = (stock: Stock, settings: SimSettings): number => {
        const years = currentYear - settings.startYear;
        if (years <= 0 || !stock.cagr_pct) return settings.principal;

        const rate = stock.cagr_pct / 100;
        let value = settings.principal;

        for (let i = 0; i < years; i++) {
            value = value * (1 + rate) + settings.contribution;
        }
        return Math.round(value);
    };

    useEffect(() => {
        fetchStocks();
    }, []); // Initial load

    // Sorted stocks
    const sortedStocks = useMemo(() => {
        const sorted = [...stocks].sort((a, b) => {
            let aVal = a[sortKey] ?? 0;
            let bVal = b[sortKey] ?? 0;
            if (sortKey === "name") {
                return sortDir === "asc"
                    ? String(aVal).localeCompare(String(bVal))
                    : String(bVal).localeCompare(String(aVal));
            }
            return sortDir === "asc" ? Number(aVal) - Number(bVal) : Number(bVal) - Number(aVal);
        });
        return sorted.slice(0, 50); // Top 50
    }, [stocks, sortKey, sortDir]);

    const handleSort = (key: SortKey) => {
        if (sortKey === key) {
            setSortDir(sortDir === "asc" ? "desc" : "asc");
        } else {
            setSortKey(key);
            setSortDir("desc");
        }
    };

    const getSortIcon = (key: SortKey) => {
        if (sortKey !== key) return "opacity-30";
        return sortDir === "desc" ? "text-[var(--color-cta)]" : "text-[var(--color-cta)] rotate-180";
    };

    const formatCurrency = (val: number) => {
        return new Intl.NumberFormat("en-US", {
            style: "currency",
            currency: "TWD",
            maximumFractionDigits: 0,
        }).format(val);
    };

    const handleRecalculate = () => {
        fetchStocks();
    };

    const handleExport = () => {
        const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        window.open(
            `${API_URL}/api/export-excel?mode=filtered&start_year=${sim.startYear}&principal=${sim.principal}&contribution=${sim.contribution}`,
            "_blank"
        );
    };

    return (
        <div className="flex flex-col lg:flex-row gap-6">
            {/* Sidebar - Simulation Settings */}
            <aside className="w-full lg:w-72 flex-shrink-0 space-y-4">
                {/* Mobile Toggle Header */}
                <div
                    className="md:hidden flex items-center justify-between p-4 glass-card rounded-xl cursor-pointer active:scale-95 transition-transform"
                    onClick={() => setShowSettings(!showSettings)}
                >
                    <span className="font-bold text-[var(--color-primary)] uppercase text-xs tracking-wider">
                        ⚙️ Simulation Settings
                    </span>
                    <span className={`transform transition-transform ${showSettings ? 'rotate-180' : ''}`}>
                        ▼
                    </span>
                </div>

                <div className={`${showSettings ? 'block' : 'hidden'} md:block glass-card p-5 rounded-xl`}>
                    <h3 className="hidden md:block text-[var(--color-primary)] font-bold mb-4 uppercase text-xs tracking-wider border-b border-[var(--color-border)] pb-2">
                        Simulation Settings
                    </h3>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-xs text-[var(--color-text-muted)] mb-1">
                                Start Year (2006-{currentYear})
                            </label>
                            <input
                                type="number"
                                min={2006}
                                max={currentYear}
                                value={sim.startYear}
                                onChange={(e) => setSim({ ...sim, startYear: Number(e.target.value) })}
                                className="w-full bg-black/50 border border-[var(--color-border)] rounded px-3 py-2 text-sm focus:border-[var(--color-cta)] outline-none transition"
                            />
                        </div>

                        <div>
                            <label className="block text-xs text-[var(--color-text-muted)] mb-1">
                                Initial Capital ($)
                            </label>
                            <input
                                type="number"
                                step={10000}
                                value={sim.principal}
                                onChange={(e) => setSim({ ...sim, principal: Number(e.target.value) })}
                                className="w-full bg-black/50 border border-[var(--color-border)] rounded px-3 py-2 text-sm focus:border-[var(--color-cta)] outline-none transition"
                            />
                        </div>

                        <div>
                            <label className="block text-xs text-[var(--color-text-muted)] mb-1">
                                Annual Contribution ($)
                            </label>
                            <input
                                type="number"
                                step={10000}
                                value={sim.contribution}
                                onChange={(e) => setSim({ ...sim, contribution: Number(e.target.value) })}
                                className="w-full bg-black/50 border border-[var(--color-border)] rounded px-3 py-2 text-sm focus:border-[var(--color-cta)] outline-none transition"
                            />
                        </div>

                        <button
                            onClick={handleRecalculate}
                            disabled={isCalculating}
                            className="w-full bg-[var(--color-cta)]/10 border border-[var(--color-cta)] text-[var(--color-cta)] hover:bg-[var(--color-cta)] hover:text-black font-bold py-2 rounded transition cursor-pointer disabled:opacity-50"
                        >
                            {isCalculating ? "Calculating..." : "Apply (Recalculate)"}
                        </button>

                        <button
                            onClick={handleExport}
                            className="w-full bg-[var(--color-primary)]/10 border border-[var(--color-primary)] text-[var(--color-primary)] hover:bg-[var(--color-primary)] hover:text-black font-bold py-2 rounded transition cursor-pointer"
                        >
                            📥 Export Excel
                        </button>
                    </div>
                </div>

                <div className="glass-card p-5 rounded-xl">
                    <h3 className="text-[var(--color-text-muted)] text-xs mb-2">Universe Stats</h3>
                    <div className="flex justify-between items-center mb-1">
                        <span>Total Listed</span>
                        <span className="font-mono">{stocks.length}</span>
                    </div>
                    <div className="flex justify-between items-center">
                        <span>Top Candidates</span>
                        <span className="font-mono text-[var(--color-primary)]">{sortedStocks.length}</span>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <div className="flex-1">
                <header className="mb-6">
                    <div className="flex items-center gap-3">
                        <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
                            Mars Strategy
                        </h1>
                        {isCalculating && (
                            <div className="flex items-center gap-2 text-[var(--color-cta)] animate-pulse">
                                <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                <span className="text-xs">Calculating...</span>
                            </div>
                        )}
                    </div>
                    <p className="text-[var(--color-text-muted)]">
                        Top 50 Survivors ({sim.startYear} - {currentYear})
                    </p>
                </header>

                {loading ? (
                    <div className="text-center py-20 animate-pulse text-[var(--color-text-muted)]">
                        Loading Market Data...
                    </div>
                ) : (
                    <div className="glass-card rounded-xl overflow-hidden">
                        <table className="w-full text-left text-sm">
                            <thead className="bg-black/30 uppercase text-xs text-[var(--color-text-muted)] tracking-wider">
                                <tr>
                                    <th className="px-4 py-3">Rank</th>
                                    <th className="px-4 py-3">ID</th>
                                    <th className="px-4 py-3">
                                        <button onClick={() => handleSort("name")} className="flex items-center gap-1 hover:text-white transition cursor-pointer">
                                            Name <span className={getSortIcon("name")}>▼</span>
                                        </button>
                                    </th>
                                    <th className="px-4 py-3 text-right">
                                        <button onClick={() => handleSort("finalValue")} className="flex items-center gap-1 justify-end hover:text-white transition cursor-pointer">
                                            Simulated Final <span className={getSortIcon("finalValue")}>▼</span>
                                        </button>
                                    </th>
                                    <th className="px-4 py-3 text-right">
                                        <button onClick={() => handleSort("cagr_pct")} className="flex items-center gap-1 justify-end hover:text-white transition cursor-pointer">
                                            CAGR % <span className={getSortIcon("cagr_pct")}>▼</span>
                                        </button>
                                    </th>
                                    <th className="px-4 py-3 text-right">
                                        <button onClick={() => handleSort("volatility_pct")} className="flex items-center gap-1 justify-end hover:text-white transition cursor-pointer">
                                            Volatility % <span className={getSortIcon("volatility_pct")}>▼</span>
                                        </button>
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-[var(--color-border)]">
                                {sortedStocks.map((stock, idx) => (
                                    <tr
                                        key={stock.id}
                                        className="hover:bg-white/5 transition-colors duration-150 cursor-pointer"
                                    >
                                        <td className="px-4 py-3 text-[var(--color-text-muted)] font-mono">{idx + 1}</td>
                                        <td className="px-4 py-3 font-mono text-[var(--color-cta)]">{stock.id}</td>
                                        <td className="px-4 py-3 font-medium text-white">{stock.name}</td>
                                        <td className="px-4 py-3 text-right font-bold text-[var(--color-primary)]">
                                            {formatCurrency(stock.finalValue || 0)}
                                        </td>
                                        <td className="px-4 py-3 text-right">
                                            <span className={`font-bold ${stock.cagr_pct > 20 ? "text-[var(--color-success)]" :
                                                stock.cagr_pct > 10 ? "text-[var(--color-warning)]" :
                                                    "text-[var(--color-text-muted)]"
                                                }`}>
                                                {stock.cagr_pct?.toFixed(2)}%
                                            </span>
                                        </td>
                                        <td className="px-4 py-3 text-right font-mono text-[var(--color-text-muted)]">
                                            {stock.volatility_pct?.toFixed(2)}%
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        <div className="p-4 text-center text-xs text-[var(--color-text-muted)] border-t border-[var(--color-border)]">
                            Showing top {sortedStocks.length} of {stocks.length} filtered results
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
