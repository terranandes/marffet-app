"use client";

import { useState, useMemo } from "react";
import ReactECharts from "echarts-for-react";

interface CompoundSettings {
    mode: "single" | "comparison";
    stockCode: string;
    stock1: string;
    stock2: string;
    stock3: string;
    startYear: number;
    endYear: number;
    principal: number;
    contribution: number;
}

interface HistoryPoint {
    year: number;
    value: number;
    dividend: number;
    invested: number;
    roi: number;
    cagr: number;
}

interface StrategyResult {
    finalValue: number;
    totalCost: number;
    history: HistoryPoint[];
}

interface StockResult {
    name: string;
    code: string;
    BAO: StrategyResult;
    BAH: StrategyResult;
    BAL: StrategyResult;
}

export default function CompoundPage() {
    const currentYear = new Date().getFullYear();
    const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

    const [settings, setSettings] = useState<CompoundSettings>({
        mode: "single",
        stockCode: "2330",
        stock1: "0050",
        stock2: "2330",
        stock3: "2383",
        startYear: 2006,
        endYear: currentYear,
        principal: 1000000,
        contribution: 60000
    });

    const [results, setResults] = useState<StockResult[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [showSettings, setShowSettings] = useState(false);

    const fetchSimulation = async () => {
        setLoading(true);
        setError(null);
        setResults([]);

        try {
            const stockCodes = settings.mode === "single"
                ? [settings.stockCode]
                : [settings.stock1, settings.stock2, settings.stock3].filter(s => s.trim() !== "");

            const fetchPromises = stockCodes.map(async (code) => {
                const url = `${API_BASE}/api/results/detail?stock_id=${code}&start_year=${settings.startYear}&principal=${settings.principal}&contribution=${settings.contribution}`;
                const res = await fetch(url);
                if (!res.ok) throw new Error(`Failed to fetch ${code}`);
                const data = await res.json();

                // Get stock name
                const nameRes = await fetch(`${API_BASE}/api/results?start_year=${settings.startYear}&principal=${settings.principal}&contribution=${settings.contribution}`);
                const nameData = await nameRes.json();
                const stockInfo = nameData?.stocks?.find((s: { id: string }) => s.id === code);

                return {
                    code,
                    name: stockInfo?.name || code,
                    BAO: data.BAO,
                    BAH: data.BAH,
                    BAL: data.BAL
                };
            });

            const allResults = await Promise.all(fetchPromises);
            setResults(allResults);
        } catch (e) {
            setError(e instanceof Error ? e.message : "Failed to load data");
        } finally {
            setLoading(false);
        }
    };

    // Helper to get last history point
    const getLastHistory = (strategy: StrategyResult | undefined) => {
        if (!strategy?.history?.length) return null;
        return strategy.history[strategy.history.length - 1];
    };

    // Helper to calculate total dividends
    const getTotalDividends = (strategy: StrategyResult | undefined) => {
        if (!strategy?.history?.length) return 0;
        return strategy.history.reduce((sum, h) => sum + (h.dividend || 0), 0);
    };

    // Helper to calculate total shares (rough estimate based on value/avg price)
    const getTotalQty = (strategy: StrategyResult | undefined) => {
        const last = getLastHistory(strategy);
        if (!last || !strategy?.finalValue) return 0;
        // Rough estimate (would need actual share tracking for precision)
        return Math.round(strategy.finalValue / 100); // Placeholder
    };

    // Wealth Chart (Single Mode: 3 strategies, Comparison Mode: 1 strategy per stock)
    const wealthChartOption = useMemo(() => {
        if (results.length === 0) return {};

        const colors = ["#00ffc3", "#ff6b6b", "#4ecdc4", "#ffe66d", "#a29bfe", "#fd79a8"];
        const series: object[] = [];
        let xAxisData: number[] = [];

        if (settings.mode === "single" && results[0]) {
            const res = results[0];
            xAxisData = res.BAO?.history?.map(h => h.year) || [];
            series.push(
                { name: "Buy At Yearly Opening", type: "line", data: res.BAO?.history?.map(h => h.value) || [], smooth: true, lineStyle: { width: 2 }, itemStyle: { color: "#00ffc3" } },
                { name: "Buy At Yearly Highest", type: "line", data: res.BAH?.history?.map(h => h.value) || [], smooth: true, lineStyle: { width: 2, type: "dashed" }, itemStyle: { color: "#ff6b6b" } },
                { name: "Buy At Yearly Lowest", type: "line", data: res.BAL?.history?.map(h => h.value) || [], smooth: true, lineStyle: { width: 2, type: "dashed" }, itemStyle: { color: "#4ecdc4" } }
            );
        } else {
            results.forEach((res, idx) => {
                if (res.BAO?.history) {
                    if (xAxisData.length === 0) xAxisData = res.BAO.history.map(h => h.year);
                    series.push({
                        name: `${res.name}(${res.code})`,
                        type: "line",
                        data: res.BAO.history.map(h => h.value),
                        smooth: true,
                        lineStyle: { width: 2 },
                        itemStyle: { color: colors[idx % colors.length] }
                    });
                }
            });
        }

        return {
            backgroundColor: "transparent",
            title: { text: "Stock Market Value", left: "center", textStyle: { color: "#333", fontSize: 14 } },
            tooltip: { trigger: "axis", backgroundColor: "#fff", borderColor: "#ddd", textStyle: { color: "#333" } },
            legend: { textStyle: { color: "#666" }, top: 30 },
            grid: { left: "8%", right: "5%", bottom: "10%", top: "20%", containLabel: true },
            xAxis: { type: "category", data: xAxisData, axisLine: { lineStyle: { color: "#ccc" } }, axisLabel: { color: "#666" } },
            yAxis: { type: "value", axisLine: { lineStyle: { color: "#ccc" } }, axisLabel: { color: "#666", formatter: (v: number) => v >= 1e6 ? `${(v / 1e6).toFixed(0)}M` : v.toLocaleString() }, splitLine: { lineStyle: { color: "#eee" } } },
            series
        };
    }, [results, settings.mode]);

    // Dividend Chart
    const dividendChartOption = useMemo(() => {
        if (results.length === 0) return {};

        const colors = ["#00ffc3", "#ff6b6b", "#4ecdc4", "#ffe66d", "#a29bfe", "#fd79a8"];
        const series: object[] = [];
        let xAxisData: number[] = [];

        if (settings.mode === "single" && results[0]) {
            const res = results[0];
            xAxisData = res.BAO?.history?.map(h => h.year) || [];
            series.push(
                { name: "Buy At Yearly Opening", type: "line", data: res.BAO?.history?.map(h => h.dividend) || [], smooth: true, areaStyle: { opacity: 0.3 }, itemStyle: { color: "#00ffc3" } },
                { name: "Buy At Yearly Highest", type: "line", data: res.BAH?.history?.map(h => h.dividend) || [], smooth: true, lineStyle: { type: "dashed" }, itemStyle: { color: "#ff6b6b" } },
                { name: "Buy At Yearly Lowest", type: "line", data: res.BAL?.history?.map(h => h.dividend) || [], smooth: true, lineStyle: { type: "dashed" }, itemStyle: { color: "#4ecdc4" } }
            );
        } else {
            results.forEach((res, idx) => {
                if (res.BAO?.history) {
                    if (xAxisData.length === 0) xAxisData = res.BAO.history.map(h => h.year);
                    series.push({
                        name: `${res.name}(${res.code})`,
                        type: "line",
                        data: res.BAO.history.map(h => h.dividend),
                        smooth: true,
                        areaStyle: { opacity: 0.2 },
                        itemStyle: { color: colors[idx % colors.length] }
                    });
                }
            });
        }

        return {
            backgroundColor: "transparent",
            title: { text: "Yearly Cash Div. Received", left: "center", textStyle: { color: "#333", fontSize: 14 } },
            tooltip: { trigger: "axis", backgroundColor: "#fff", borderColor: "#ddd", textStyle: { color: "#333" } },
            legend: { textStyle: { color: "#666" }, top: 30 },
            grid: { left: "8%", right: "5%", bottom: "10%", top: "20%", containLabel: true },
            xAxis: { type: "category", data: xAxisData, axisLine: { lineStyle: { color: "#ccc" } }, axisLabel: { color: "#666" } },
            yAxis: { type: "value", axisLine: { lineStyle: { color: "#ccc" } }, axisLabel: { color: "#666", formatter: (v: number) => v >= 1e6 ? `${(v / 1e6).toFixed(1)}M` : v.toLocaleString() }, splitLine: { lineStyle: { color: "#eee" } } },
            series
        };
    }, [results, settings.mode]);

    return (
        <div className="flex flex-col lg:flex-row gap-6 min-h-[calc(100vh-100px)]">
            {/* Sidebar */}
            <aside className="w-full lg:w-72 flex-shrink-0 space-y-4">
                <div className="md:hidden flex items-center justify-between p-4 glass-card rounded-xl cursor-pointer" onClick={() => setShowSettings(!showSettings)}>
                    <span className="font-bold text-[var(--color-primary)] uppercase text-xs">⚙️ Settings</span>
                    <span className={`transition-transform ${showSettings ? 'rotate-180' : ''}`}>▼</span>
                </div>

                <div className={`${showSettings ? 'block' : 'hidden'} md:block glass-card p-5 rounded-xl`}>
                    <h3 className="hidden md:block text-[var(--color-primary)] font-bold mb-4 uppercase text-xs border-b border-[var(--color-border)] pb-2">Configuration</h3>
                    <div className="space-y-4">
                        {/* Mode */}
                        <div>
                            <label className="block text-xs text-[var(--color-text-muted)] mb-1">Mode</label>
                            <div className="flex bg-black/50 rounded p-1 border border-[var(--color-border)]">
                                <button onClick={() => setSettings({ ...settings, mode: "single" })} className={`flex-1 py-1.5 text-xs font-bold rounded ${settings.mode === "single" ? "bg-[var(--color-cta)] text-black" : "text-zinc-400"}`}>Single</button>
                                <button onClick={() => setSettings({ ...settings, mode: "comparison" })} className={`flex-1 py-1.5 text-xs font-bold rounded ${settings.mode === "comparison" ? "bg-purple-500 text-white" : "text-zinc-400"}`}>Comparison</button>
                            </div>
                        </div>

                        {/* Stock Inputs */}
                        {settings.mode === "single" ? (
                            <div>
                                <label className="block text-xs text-[var(--color-text-muted)] mb-1">Stock Code</label>
                                <input type="text" value={settings.stockCode} onChange={(e) => setSettings({ ...settings, stockCode: e.target.value })} className="w-full bg-black/50 border border-[var(--color-border)] rounded px-3 py-2 text-sm font-mono" />
                            </div>
                        ) : (
                            <div className="space-y-2">
                                {[["stock1", "Stock 1"], ["stock2", "Stock 2"], ["stock3", "Stock 3 (Opt)"]].map(([key, label]) => (
                                    <div key={key}>
                                        <label className="block text-xs text-[var(--color-text-muted)] mb-1">{label}</label>
                                        <input type="text" value={settings[key as keyof CompoundSettings] as string} onChange={(e) => setSettings({ ...settings, [key]: e.target.value })} className="w-full bg-black/50 border border-[var(--color-border)] rounded px-3 py-2 text-sm font-mono" />
                                    </div>
                                ))}
                            </div>
                        )}

                        {/* Date + Capital */}
                        <div className="pt-2 border-t border-[var(--color-border)] space-y-3">
                            <div className="grid grid-cols-2 gap-2">
                                <div><label className="block text-xs text-[var(--color-text-muted)] mb-1">Start Year</label><input type="number" value={settings.startYear} onChange={(e) => setSettings({ ...settings, startYear: Number(e.target.value) })} className="w-full bg-black/50 border border-[var(--color-border)] rounded px-2 py-2 text-sm font-mono" /></div>
                                <div><label className="block text-xs text-[var(--color-text-muted)] mb-1">End Year</label><input type="number" value={settings.endYear} onChange={(e) => setSettings({ ...settings, endYear: Number(e.target.value) })} className="w-full bg-black/50 border border-[var(--color-border)] rounded px-2 py-2 text-sm font-mono" /></div>
                            </div>
                            <div><label className="block text-xs text-[var(--color-text-muted)] mb-1">Initial Capital ($)</label><input type="number" step={10000} value={settings.principal} onChange={(e) => setSettings({ ...settings, principal: Number(e.target.value) })} className="w-full bg-black/50 border border-[var(--color-border)] rounded px-3 py-2 text-sm font-mono" /></div>
                            <div><label className="block text-xs text-[var(--color-text-muted)] mb-1">Annual Contribution ($)</label><input type="number" step={10000} value={settings.contribution} onChange={(e) => setSettings({ ...settings, contribution: Number(e.target.value) })} className="w-full bg-black/50 border border-[var(--color-border)] rounded px-3 py-2 text-sm font-mono" /></div>
                        </div>

                        <button onClick={fetchSimulation} disabled={loading} className={`w-full font-bold py-2.5 rounded mt-4 ${settings.mode === "single" ? "bg-[var(--color-cta)] text-black" : "bg-purple-500 text-white"} disabled:opacity-50`}>
                            {loading ? "Calculating..." : settings.mode === "single" ? "Calculate" : "Compare"}
                        </button>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <div className="flex-1 glass-card rounded-xl border border-[var(--color-border)] overflow-hidden">
                <header className="p-4 border-b border-[var(--color-border)] bg-black/20">
                    <h1 className="text-xl font-bold">{settings.mode === "single" ? <span className="text-[var(--color-cta)]">📈 Compound Interest</span> : <span className="text-purple-400">⚖️ Asset Comparison</span>}</h1>
                </header>

                <div className="p-4 bg-white text-gray-800 min-h-[600px] overflow-auto">
                    {error && <div className="text-red-500 text-center py-8">{error}</div>}
                    {loading && <div className="flex items-center justify-center h-64"><span className="text-blue-500 text-xl animate-pulse">⏳ Calculating...</span></div>}

                    {!loading && results.length === 0 && !error && (
                        <div className="space-y-8">
                            {/* Skeleton Result Section */}
                            <div>
                                <h2 className="text-lg font-bold text-gray-700 mb-4 border-b pb-2">Result</h2>
                                <div className="text-sm text-gray-400 space-y-1 mb-4">
                                    <p>• Stock Name: <span className="text-gray-300">---</span></p>
                                    <p>• Amount of Inv.: <span className="text-gray-300">${settings.principal.toLocaleString()}</span></p>
                                    <p>• Year: <span className="text-gray-300">{settings.startYear} ~ {settings.endYear}</span></p>
                                </div>

                                {/* Skeleton Table */}
                                <div className="overflow-x-auto">
                                    <table className="w-full text-sm border-collapse opacity-50">
                                        <thead>
                                            <tr className="bg-blue-50">
                                                <th className="border p-2 text-left"></th>
                                                <th className="border p-2 text-center bg-cyan-50">Buy At Yearly Opening</th>
                                                <th className="border p-2 text-center bg-red-50">Buy At Yearly Highest</th>
                                                <th className="border p-2 text-center bg-green-50">Buy At Yearly Lowest</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr><td className="border p-2 font-medium">Final Value</td><td className="border p-2 text-center text-gray-300">---</td><td className="border p-2 text-center text-gray-300">---</td><td className="border p-2 text-center text-gray-300">---</td></tr>
                                            <tr><td className="border p-2 font-medium">Total Cash (Div)</td><td className="border p-2 text-center text-gray-300">---</td><td className="border p-2 text-center text-gray-300">---</td><td className="border p-2 text-center text-gray-300">---</td></tr>
                                            <tr><td className="border p-2 font-medium">ROI</td><td className="border p-2 text-center text-gray-300">---</td><td className="border p-2 text-center text-gray-300">---</td><td className="border p-2 text-center text-gray-300">---</td></tr>
                                            <tr><td className="border p-2 font-medium">Yearly ROI (CAGR)</td><td className="border p-2 text-center text-gray-300">---</td><td className="border p-2 text-center text-gray-300">---</td><td className="border p-2 text-center text-gray-300">---</td></tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>

                            {/* Skeleton Stock Market Value Chart */}
                            <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                                <h3 className="text-sm font-medium text-gray-500 text-center mb-4">Stock Market Value</h3>
                                <div className="h-64 flex items-end justify-around px-8 opacity-30">
                                    {[40, 55, 45, 60, 75, 70, 85, 90, 82, 95, 88, 100, 92, 105, 115, 110, 125, 130, 120, 135].map((h, i) => (
                                        <div key={i} className="w-3 bg-gradient-to-t from-cyan-300 to-cyan-100 rounded-t" style={{ height: `${h * 2}px` }} />
                                    ))}
                                </div>
                                <div className="flex justify-between text-xs text-gray-400 mt-2 px-4">
                                    <span>{settings.startYear}</span>
                                    <span>{Math.floor((settings.startYear + settings.endYear) / 2)}</span>
                                    <span>{settings.endYear}</span>
                                </div>
                            </div>

                            {/* Skeleton Dividend Chart */}
                            <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                                <h3 className="text-sm font-medium text-gray-500 text-center mb-4">Yearly Cash Div. Received</h3>
                                <div className="h-48 flex items-end justify-around px-8 opacity-30">
                                    {[10, 12, 15, 18, 20, 25, 30, 35, 45, 55, 60, 70, 75, 85, 95, 100, 110, 120, 115, 125].map((h, i) => (
                                        <div key={i} className="w-3 bg-gradient-to-t from-green-300 to-green-100 rounded-t" style={{ height: `${h * 1.2}px` }} />
                                    ))}
                                </div>
                                <div className="flex justify-between text-xs text-gray-400 mt-2 px-4">
                                    <span>{settings.startYear}</span>
                                    <span>{Math.floor((settings.startYear + settings.endYear) / 2)}</span>
                                    <span>{settings.endYear}</span>
                                </div>
                            </div>

                            <p className="text-center text-gray-400 text-sm">👆 Click <strong>Calculate</strong> to generate your wealth projection</p>
                        </div>
                    )}

                    {results.length > 0 && (
                        <div className="space-y-8">
                            {/* Result Section */}
                            <div>
                                <h2 className="text-lg font-bold text-gray-700 mb-4 border-b pb-2">Result</h2>

                                {/* Single Mode: Show stock info + strategy comparison */}
                                {settings.mode === "single" && results[0] && (
                                    <div className="space-y-4">
                                        <div className="text-sm text-gray-600 space-y-1">
                                            <p>• Stock Name: <strong>{results[0].name}({results[0].code})</strong></p>
                                            <p>• Amount of Inv.: <strong>${settings.principal.toLocaleString()}</strong></p>
                                            <p>• Year: <strong>{settings.startYear} ~ {settings.endYear}</strong></p>
                                        </div>

                                        {/* Strategy Comparison Table */}
                                        <div className="overflow-x-auto">
                                            <table className="w-full text-sm border-collapse">
                                                <thead>
                                                    <tr className="bg-blue-50">
                                                        <th className="border p-2 text-left"></th>
                                                        <th className="border p-2 text-center bg-cyan-100">Buy At Yearly Opening</th>
                                                        <th className="border p-2 text-center bg-red-100">Buy At Yearly Highest</th>
                                                        <th className="border p-2 text-center bg-green-100">Buy At Yearly Lowest</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <tr><td className="border p-2 font-medium">Final Value</td>
                                                        <td className="border p-2 text-center font-bold text-cyan-600">${(results[0].BAO?.finalValue || 0).toLocaleString()}</td>
                                                        <td className="border p-2 text-center">${(results[0].BAH?.finalValue || 0).toLocaleString()}</td>
                                                        <td className="border p-2 text-center">${(results[0].BAL?.finalValue || 0).toLocaleString()}</td>
                                                    </tr>
                                                    <tr><td className="border p-2 font-medium">Total Cash (Div)</td>
                                                        <td className="border p-2 text-center">${getTotalDividends(results[0].BAO).toLocaleString()}</td>
                                                        <td className="border p-2 text-center">${getTotalDividends(results[0].BAH).toLocaleString()}</td>
                                                        <td className="border p-2 text-center">${getTotalDividends(results[0].BAL).toLocaleString()}</td>
                                                    </tr>
                                                    <tr><td className="border p-2 font-medium">ROI</td>
                                                        <td className="border p-2 text-center font-bold text-cyan-600">{((getLastHistory(results[0].BAO)?.roi || 0)).toFixed(1)}%</td>
                                                        <td className="border p-2 text-center text-blue-600">{((getLastHistory(results[0].BAH)?.roi || 0)).toFixed(1)}%</td>
                                                        <td className="border p-2 text-center">{((getLastHistory(results[0].BAL)?.roi || 0)).toFixed(1)}%</td>
                                                    </tr>
                                                    <tr><td className="border p-2 font-medium">Yearly ROI (CAGR)</td>
                                                        <td className="border p-2 text-center">{((getLastHistory(results[0].BAO)?.cagr || 0)).toFixed(1)}%</td>
                                                        <td className="border p-2 text-center">{((getLastHistory(results[0].BAH)?.cagr || 0)).toFixed(1)}%</td>
                                                        <td className="border p-2 text-center">{((getLastHistory(results[0].BAL)?.cagr || 0)).toFixed(1)}%</td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                )}

                                {/* Comparison Mode: Multi-stock table */}
                                {settings.mode === "comparison" && results.length > 0 && (
                                    <div className="overflow-x-auto">
                                        <table className="w-full text-sm border-collapse">
                                            <thead>
                                                <tr className="bg-blue-50">
                                                    <th className="border p-2 text-left">Stock Name</th>
                                                    {results.map((r, idx) => (
                                                        <th key={r.code} className={`border p-2 text-center ${idx === 0 ? "bg-cyan-100" : idx === 1 ? "bg-red-100" : "bg-green-100"}`}>{r.name}</th>
                                                    ))}
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <tr><td className="border p-2 font-medium">Stock Code</td>{results.map(r => <td key={r.code} className="border p-2 text-center">{r.code}</td>)}</tr>
                                                <tr><td className="border p-2 font-medium">Amount of Inv.</td>{results.map(r => <td key={r.code} className="border p-2 text-center">${settings.principal.toLocaleString()}</td>)}</tr>
                                                <tr><td className="border p-2 font-medium">Year</td>{results.map(r => <td key={r.code} className="border p-2 text-center">{settings.startYear} ~ {settings.endYear}</td>)}</tr>
                                                <tr><td className="border p-2 font-medium">Final Value</td>{results.map((r, idx) => <td key={r.code} className={`border p-2 text-center font-bold ${idx === 0 ? "text-cyan-600" : idx === 1 ? "text-red-500" : "text-green-600"}`}>${(r.BAO?.finalValue || 0).toLocaleString()}</td>)}</tr>
                                                <tr><td className="border p-2 font-medium">Total Cash (Div)</td>{results.map(r => <td key={r.code} className="border p-2 text-center">${getTotalDividends(r.BAO).toLocaleString()}</td>)}</tr>
                                                <tr><td className="border p-2 font-medium">ROI</td>{results.map((r, idx) => <td key={r.code} className={`border p-2 text-center font-bold ${idx === 0 ? "text-cyan-600" : ""}`}>{((getLastHistory(r.BAO)?.roi || 0)).toFixed(1)}%</td>)}</tr>
                                                <tr><td className="border p-2 font-medium">Yearly ROI (CAGR)</td>{results.map(r => <td key={r.code} className="border p-2 text-center">{((getLastHistory(r.BAO)?.cagr || 0)).toFixed(1)}%</td>)}</tr>
                                            </tbody>
                                        </table>
                                    </div>
                                )}
                            </div>

                            {/* Stock Market Value Chart */}
                            <div>
                                <ReactECharts option={wealthChartOption} style={{ height: "350px" }} notMerge={true} />
                            </div>

                            {/* Dividend Chart */}
                            <div>
                                <ReactECharts option={dividendChartOption} style={{ height: "350px" }} notMerge={true} />
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
