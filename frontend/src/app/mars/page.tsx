import dynamic from 'next/dynamic';

// Dynamic import for ECharts to avoid SSR issues
const ReactECharts = dynamic(() => import('echarts-for-react'), { ssr: false });

interface Stock {
    id: string;
    name: string;
    price: number;
    cagr_pct: number;
    cagr_std: number;
    valid_years: number;
    volatility_pct?: number;
    finalValue?: number;
    history?: { year: number; value: number; dividend: number }[];
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

    // Selected Stock for Modal
    const [selectedStock, setSelectedStock] = useState<Stock | null>(null);

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
                // Backend now calculates finalValue, so we just use it directly
                // But if backend doesn't, we can fallback or just adopt backend's exact value.
                // The verification showed backend calculates it.
                // However, we need to map history if available.
                setStocks(data);
            }
        } catch (err) {
            console.error("Failed to fetch stocks:", err);
            setStocks([]);
        }
        setLoading(false);
        setIsCalculating(false);
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

    // Calculate Total ROI for Modal
    const calculateTotalROI = (finalValue: number) => {
        const years = currentYear - sim.startYear;
        const totalInvested = sim.principal + (sim.contribution * years);
        if (totalInvested <= 0) return 0;
        return ((finalValue - totalInvested) / totalInvested) * 100;
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
                                        onClick={() => setSelectedStock(stock)}
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

            {/* Stock Detail Modal */}
            {selectedStock && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
                    <div className="glass-card w-full max-w-4xl max-h-[90vh] overflow-y-auto rounded-xl border border-[var(--color-border)] shadow-2xl relative">
                        {/* Close Button */}
                        <button
                            onClick={() => setSelectedStock(null)}
                            className="absolute top-4 right-4 p-2 bg-white/10 hover:bg-white/20 rounded-full transition text-[var(--color-text-muted)] hover:text-white"
                        >
                            ✕
                        </button>

                        <div className="p-6 md:p-8">
                            <h2 className="text-2xl font-bold mb-10 flex items-center gap-3">
                                <span>Result:</span>
                                <span className="text-[var(--color-cta)]">{selectedStock.name}</span>
                                <span className="text-[var(--color-cta)] opacity-75">({selectedStock.id})</span>
                            </h2>

                            {/* Stats Grid */}
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                                <div className="bg-black/30 p-4 rounded-lg border border-[var(--color-border)]">
                                    <div className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Amount Inv.</div>
                                    <div className="text-xl font-bold text-white">
                                        ${sim.principal.toLocaleString()} + ${sim.contribution.toLocaleString()}/yr
                                    </div>
                                </div>
                                <div className="bg-black/30 p-4 rounded-lg border border-[var(--color-border)]">
                                    <div className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Total Years</div>
                                    <div className="text-xl font-bold text-white">
                                        {selectedStock.valid_years} Years
                                    </div>
                                </div>
                                <div className="bg-black/30 p-4 rounded-lg border border-[var(--color-border)]">
                                    <div className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Yearly ROI (CAGR)</div>
                                    <div className="text-xl font-bold text-[var(--color-success)]">
                                        {selectedStock.cagr_pct.toFixed(2)}%
                                    </div>
                                </div>
                            </div>

                            {/* Strategy Table */}
                            <div className="mb-8 rounded-lg overflow-hidden border border-[var(--color-border)]">
                                <div className="grid grid-cols-4 bg-[var(--color-primary)] text-black font-bold text-sm py-3 px-4">
                                    <div>Strategy</div>
                                    <div className="text-center">Buy At Yearly Opening</div>
                                    <div className="text-center opacity-50">Buy At Yearly Highest (N/A)</div>
                                    <div className="text-center opacity-50">Buy At Yearly Lowest (N/A)</div>
                                </div>
                                <div className="divide-y divide-[var(--color-border)]">
                                    <div className="grid grid-cols-4 py-4 px-4 bg-black/20 hover:bg-white/5 transition">
                                        <div className="font-bold text-white">Final Value</div>
                                        <div className="text-center font-bold text-[var(--color-cta)] text-xl">
                                            {formatCurrency(selectedStock.finalValue || 0)}
                                        </div>
                                        <div className="text-center text-[var(--color-text-muted)]">-</div>
                                        <div className="text-center text-[var(--color-text-muted)]">-</div>
                                    </div>
                                    <div className="grid grid-cols-4 py-4 px-4 bg-black/20 hover:bg-white/5 transition">
                                        <div className="font-bold text-white">Total ROI</div>
                                        <div className="text-center font-bold text-[var(--color-success)] text-lg">
                                            {calculateTotalROI(selectedStock.finalValue || 0).toFixed(2)}%
                                        </div>
                                        <div className="text-center text-[var(--color-text-muted)]">-</div>
                                        <div className="text-center text-[var(--color-text-muted)]">-</div>
                                    </div>
                                </div>
                            </div>

                            {/* Chart Section */}
                            <div className="bg-black/30 p-4 rounded-xl border border-[var(--color-border)]">
                                <div className="flex justify-between items-center mb-4">
                                    <h3 className="font-bold text-white">Stock Market Value (Wealth Path)</h3>
                                    <div className="flex gap-2">
                                        <button className="px-3 py-1 bg-[var(--color-cta)] text-black font-bold text-xs rounded">Wealth</button>
                                        <button className="px-3 py-1 bg-white/10 text-[var(--color-text-muted)] hover:text-white text-xs rounded transition">Dividend</button>
                                    </div>
                                </div>

                                {selectedStock.history && selectedStock.history.length > 0 ? (
                                    <ReactECharts
                                        option={{
                                            backgroundColor: 'transparent',
                                            tooltip: {
                                                trigger: 'axis',
                                                backgroundColor: 'rgba(0,0,0,0.8)',
                                                borderColor: '#333',
                                                textStyle: { color: '#fff' },
                                                formatter: (params: any) => {
                                                    const p = params[0];
                                                    return `${p.name}<br/>Value: $${Number(p.value).toLocaleString()}`;
                                                }
                                            },
                                            grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
                                            xAxis: {
                                                type: 'category',
                                                boundaryGap: false,
                                                data: selectedStock.history.map(d => d.year),
                                                axisLine: { lineStyle: { color: '#666' } },
                                                axisLabel: { color: '#888' }
                                            },
                                            yAxis: {
                                                type: 'value',
                                                splitLine: { lineStyle: { color: '#333' } },
                                                axisLabel: { color: '#888', formatter: (val: number) => `$${(val / 1000000).toFixed(0)}M` }
                                            },
                                            series: [{
                                                data: selectedStock.history.map(d => d.value),
                                                type: 'line',
                                                smooth: true,
                                                lineStyle: { color: '#00eeee', width: 3 },
                                                areaStyle: {
                                                    color: {
                                                        type: 'linear',
                                                        x: 0, y: 0, x2: 0, y2: 1,
                                                        colorStops: [{ offset: 0, color: 'rgba(0, 238, 238, 0.5)' }, { offset: 1, color: 'rgba(0, 238, 238, 0)' }]
                                                    }
                                                },
                                                symbol: 'circle',
                                                symbolSize: 6,
                                                itemStyle: { color: '#00eeee', borderColor: '#fff', borderWidth: 2 }
                                            }]
                                        }}
                                        style={{ height: '400px', width: '100%' }}
                                    />
                                ) : (
                                    <div className="h-[400px] flex items-center justify-center text-[var(--color-text-muted)]">
                                        No historical data available
                                    </div>
                                )}
                            </div>

                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
