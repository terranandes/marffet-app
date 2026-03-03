"use client";

import dynamic from 'next/dynamic';
import { useState, useEffect, useMemo } from "react";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import { STORAGE_KEYS } from "@/lib/constants";

// Dynamic import for ECharts to avoid SSR issues
const ReactECharts = dynamic(() => import('echarts-for-react'), { ssr: false });

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
    const { t } = useLanguage();
    const currentYear = new Date().getFullYear();

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
    const [isPremium, setIsPremium] = useState(false);

    useEffect(() => {
        setIsPremium(localStorage.getItem(STORAGE_KEYS.PREMIUM) === "true");
    }, []);

    const fetchSimulation = async () => {
        setLoading(true);
        setError(null);
        setResults([]);

        try {
            const stockCodes = settings.mode === "single"
                ? [settings.stockCode]
                : [settings.stock1, settings.stock2, settings.stock3].filter(s => s.trim() !== "");

            const fetchPromises = stockCodes.map(async (code) => {
                const url = `/api/results/detail?stock_id=${code}&start_year=${settings.startYear}&principal=${settings.principal}&contribution=${settings.contribution}`;
                const res = await fetch(url);
                if (!res.ok) throw new Error(`Failed to fetch ${code}`);
                const data = await res.json();

                const nameRes = await fetch(`/api/results?start_year=${settings.startYear}&principal=${settings.principal}&contribution=${settings.contribution}`);
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

    const getLastHistory = (strategy: StrategyResult | undefined) => {
        if (!strategy?.history?.length) return null;
        return strategy.history[strategy.history.length - 1];
    };

    const getTotalDividends = (strategy: StrategyResult | undefined) => {
        if (!strategy?.history?.length) return 0;
        return strategy.history.reduce((sum, h) => sum + (h.dividend || 0), 0);
    };

    // Wealth Chart
    const wealthChartOption = useMemo(() => {
        if (results.length === 0) return {};

        const colors = ["#00ffc3", "#ff6b6b", "#ffd700", "#a29bfe", "#fd79a8", "#45b7d1"];
        const series: object[] = [];
        let xAxisData: number[] = [];

        if (settings.mode === "single" && results[0]) {
            const res = results[0];
            xAxisData = res.BAO?.history?.map(h => h.year) || [];
            series.push(
                { name: t('Compound.BuyOpening'), type: "line", data: res.BAO?.history?.map(h => h.value) || [], smooth: true, lineStyle: { width: 2 }, itemStyle: { color: "#00ffc3" } },
                { name: t('Compound.BuyHighest'), type: "line", data: res.BAH?.history?.map(h => h.value) || [], smooth: true, lineStyle: { width: 2, type: "dashed" }, itemStyle: { color: "#ff6b6b" } },
                { name: t('Compound.BuyLowest'), type: "line", data: res.BAL?.history?.map(h => h.value) || [], smooth: true, lineStyle: { width: 2, type: "dashed" }, itemStyle: { color: "#4ecdc4" } }
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
            title: { text: settings.mode === "single" ? t('Compound.StockMarketValue') : `${t('Compound.Comparison')} - ${t('Compound.StockMarketValue')}`, left: "center", textStyle: { color: "#aaa", fontSize: 14 } },
            tooltip: { trigger: "axis", backgroundColor: "#1a1a2e", borderColor: "#333", textStyle: { color: "#fff" } },
            legend: { data: settings.mode === "single" ? [{ name: t('Compound.BuyOpening'), icon: "path://M0,3 L26,3 L26,7 L0,7 Z" }, { name: t('Compound.BuyHighest'), icon: "path://M0,3 L6,3 L6,7 L0,7 Z M10,3 L16,3 L16,7 L10,7 Z M20,3 L26,3 L26,7 L20,7 Z" }, { name: t('Compound.BuyLowest'), icon: "path://M0,3 L6,3 L6,7 L0,7 Z M10,3 L16,3 L16,7 L10,7 Z M20,3 L26,3 L26,7 L20,7 Z" }] : undefined, textStyle: { color: "#888" }, top: 30 },
            grid: { left: "8%", right: "5%", bottom: "10%", top: "20%", containLabel: true },
            xAxis: { type: "category", data: xAxisData, axisLine: { lineStyle: { color: "#444" } }, axisLabel: { color: "#888" } },
            yAxis: { type: "value", axisLine: { lineStyle: { color: "#444" } }, axisLabel: { color: "#888", formatter: (v: number) => v >= 1e6 ? `${(v / 1e6).toFixed(0)}M` : v.toLocaleString() }, splitLine: { lineStyle: { color: "#333" } } },
            series
        };
    }, [results, settings.mode]);

    // Dividend Chart
    const dividendChartOption = useMemo(() => {
        if (results.length === 0) return {};

        const colors = ["#00ffc3", "#ff6b6b", "#ffd700", "#a29bfe", "#fd79a8", "#45b7d1"];
        const series: object[] = [];
        let xAxisData: number[] = [];

        if (settings.mode === "single" && results[0]) {
            const res = results[0];
            xAxisData = res.BAO?.history?.map(h => h.year) || [];
            series.push(
                { name: t('Compound.BuyOpening'), type: "line", data: res.BAO?.history?.map(h => h.dividend) || [], smooth: true, areaStyle: { opacity: 0.3 }, itemStyle: { color: "#00ffc3" } },
                { name: t('Compound.BuyHighest'), type: "line", data: res.BAH?.history?.map(h => h.dividend) || [], smooth: true, lineStyle: { type: "dashed" }, itemStyle: { color: "#ff6b6b" } },
                { name: t('Compound.BuyLowest'), type: "line", data: res.BAL?.history?.map(h => h.dividend) || [], smooth: true, lineStyle: { type: "dashed" }, itemStyle: { color: "#4ecdc4" } }
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
            title: { text: t('Compound.YearlyCashDiv'), left: "center", textStyle: { color: "#aaa", fontSize: 14 } },
            tooltip: { trigger: "axis", backgroundColor: "#1a1a2e", borderColor: "#333", textStyle: { color: "#fff" } },
            legend: { data: settings.mode === "single" ? [{ name: t('Compound.BuyOpening'), icon: "path://M0,3 L26,3 L26,7 L0,7 Z" }, { name: t('Compound.BuyHighest'), icon: "path://M0,3 L6,3 L6,7 L0,7 Z M10,3 L16,3 L16,7 L10,7 Z M20,3 L26,3 L26,7 L20,7 Z" }, { name: t('Compound.BuyLowest'), icon: "path://M0,3 L6,3 L6,7 L0,7 Z M10,3 L16,3 L16,7 L10,7 Z M20,3 L26,3 L26,7 L20,7 Z" }] : undefined, textStyle: { color: "#888" }, top: 30 },
            grid: { left: "8%", right: "5%", bottom: "10%", top: "20%", containLabel: true },
            xAxis: { type: "category", data: xAxisData, axisLine: { lineStyle: { color: "#444" } }, axisLabel: { color: "#888" } },
            yAxis: { type: "value", axisLine: { lineStyle: { color: "#444" } }, axisLabel: { color: "#888", formatter: (v: number) => v >= 1e6 ? `${(v / 1e6).toFixed(1)}M` : v.toLocaleString() }, splitLine: { lineStyle: { color: "#333" } } },
            series
        };
    }, [results, settings.mode]);

    // Skeleton chart years for display
    const skeletonYears = Array.from({ length: 21 }, (_, i) => settings.startYear + i);

    return (
        <div className="flex flex-col lg:flex-row gap-6 min-h-[calc(100vh-100px)]">
            {/* Sidebar */}
            <aside className="w-full lg:w-72 flex-shrink-0 space-y-4">
                <div className="md:hidden flex items-center justify-between p-4 glass-card rounded-xl cursor-pointer" onClick={() => setShowSettings(!showSettings)}>
                    <span className="font-bold text-[var(--color-primary)] uppercase text-xs">{t('Compound.Settings')}</span>
                    <span className={`transition-transform ${showSettings ? 'rotate-180' : ''}`}>▼</span>
                </div>

                <div className={`${showSettings ? 'block' : 'hidden'} md:block glass-card p-5 rounded-xl`}>
                    <h3 className="hidden md:block text-[var(--color-primary)] font-bold mb-4 uppercase text-xs border-b border-[var(--color-border)] pb-2">{t('Compound.Configuration')}</h3>
                    <div className="space-y-4">
                        {/* Mode */}
                        <div>
                            <label className="block text-xs text-[var(--color-text-muted)] mb-1">{t('Compound.Mode')}</label>
                            <div className="flex bg-black/50 rounded p-1 border border-[var(--color-border)]">
                                <button onClick={() => setSettings({ ...settings, mode: "single" })} className={`flex-1 py-1.5 text-xs font-bold rounded transition ${settings.mode === "single" ? "bg-[var(--color-cta)] text-black" : "text-zinc-400 hover:text-white"}`}>{t('Compound.Single')}</button>
                                <button
                                    onClick={() => isPremium ? setSettings({ ...settings, mode: "comparison" }) : null}
                                    disabled={!isPremium}
                                    className={`flex-1 py-1.5 text-xs font-bold rounded transition ${!isPremium ? "text-zinc-600 cursor-not-allowed" : settings.mode === "comparison" ? "bg-amber-500 text-black" : "text-zinc-400 hover:text-white"}`}
                                    title={!isPremium ? "Premium feature" : ""}
                                >{isPremium ? t('Compound.Comparison') : `🔒 ${t('Compound.Comparison')}`}</button>
                            </div>
                        </div>

                        {/* Stock Inputs */}
                        {settings.mode === "single" ? (
                            <div>
                                <label className="block text-xs text-[var(--color-text-muted)] mb-1">{t('Compound.StockCode')}</label>
                                <input type="text" value={settings.stockCode} onChange={(e) => setSettings({ ...settings, stockCode: e.target.value })} className="w-full bg-black/50 border border-[var(--color-border)] rounded px-3 py-2 text-sm font-mono focus:border-[var(--color-cta)] outline-none transition" />
                            </div>
                        ) : (
                            <div className="space-y-2">
                                {[["stock1", t('Compound.Stock1')], ["stock2", t('Compound.Stock2')], ["stock3", t('Compound.Stock3')]].map(([key, label]) => (
                                    <div key={key}>
                                        <label className="block text-xs text-[var(--color-text-muted)] mb-1">{label}</label>
                                        <input type="text" value={settings[key as keyof CompoundSettings] as string} onChange={(e) => setSettings({ ...settings, [key]: e.target.value })} className="w-full bg-black/50 border border-[var(--color-border)] rounded px-3 py-2 text-sm font-mono focus:border-cyan-500 outline-none transition" />
                                    </div>
                                ))}
                            </div>
                        )}

                        {/* Date + Capital */}
                        <div className="pt-2 border-t border-[var(--color-border)] space-y-3">
                            <div className="grid grid-cols-2 gap-2">
                                <div><label className="block text-xs text-[var(--color-text-muted)] mb-1">{t('Compound.StartYear')}</label><input type="number" value={settings.startYear} onChange={(e) => setSettings({ ...settings, startYear: Number(e.target.value) })} className="w-full bg-black/50 border border-[var(--color-border)] rounded px-2 py-2 text-sm font-mono" /></div>
                                <div><label className="block text-xs text-[var(--color-text-muted)] mb-1">{t('Compound.EndYear')}</label><input type="number" value={settings.endYear} onChange={(e) => setSettings({ ...settings, endYear: Number(e.target.value) })} className="w-full bg-black/50 border border-[var(--color-border)] rounded px-2 py-2 text-sm font-mono" /></div>
                            </div>
                            <div><label className="block text-xs text-[var(--color-text-muted)] mb-1">{t('Compound.InitialCapital')}</label><input type="number" step={10000} value={settings.principal} onChange={(e) => setSettings({ ...settings, principal: Number(e.target.value) })} className="w-full bg-black/50 border border-[var(--color-border)] rounded px-3 py-2 text-sm font-mono" /></div>
                            <div><label className="block text-xs text-[var(--color-text-muted)] mb-1">{t('Compound.AnnualContribution')}</label><input type="number" step={10000} value={settings.contribution} onChange={(e) => setSettings({ ...settings, contribution: Number(e.target.value) })} className="w-full bg-black/50 border border-[var(--color-border)] rounded px-3 py-2 text-sm font-mono" /></div>
                        </div>

                        <button onClick={fetchSimulation} disabled={loading} className={`w-full font-bold py-2.5 rounded mt-4 cursor-pointer transition ${settings.mode === "single" ? "bg-[var(--color-cta)] text-black hover:brightness-110" : "bg-amber-500 text-black hover:brightness-110"} disabled:opacity-50`}>
                            {loading ? t('Compound.Calculating') : settings.mode === "single" ? t('Compound.Calculate') : t('Compound.Compare')}
                        </button>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <div className="flex-1 glass-card rounded-xl border border-[var(--color-border)] overflow-hidden">
                <header className="p-4 border-b border-[var(--color-border)] bg-black/20 flex justify-between items-center">
                    <h1 className="text-xl font-bold flex items-center gap-2">
                        {settings.mode === "single" ? (
                            <><span className="text-2xl">📈</span><span className="text-[var(--color-cta)]">{t('Compound.Title').replace('📈 ', '')}</span></>
                        ) : (
                            <><span className="text-2xl">⚖️</span><span className="text-amber-400">{t('Compound.ComparisonTitle').replace('⚖️ ', '')}</span></>
                        )}
                    </h1>
                </header>

                <div className="p-4 min-h-[600px] overflow-auto">
                    {error && <div className="text-red-400 text-center py-8">{error}</div>}
                    {loading && <div className="flex items-center justify-center h-64"><span className="text-[var(--color-cta)] text-xl animate-pulse">{t('Compound.Calculating')}</span></div>}

                    {/* Skeleton State - Mode Specific */}
                    {!loading && results.length === 0 && !error && (
                        <div className="space-y-8">
                            <div>
                                <h2 className="text-lg font-bold text-[var(--color-text)] mb-4 border-b border-[var(--color-border)] pb-2">{t('Compound.Result')}</h2>

                                {/* Single Mode Skeleton */}
                                {settings.mode === "single" && (
                                    <div className="space-y-4">
                                        <div className="text-sm text-[var(--color-text-muted)] space-y-1 mb-4">
                                            <p>• {t('Compound.StockName')}: <span className="text-zinc-500">---</span></p>
                                            <p>• {t('Compound.AmountOfInv')}: <span className="text-zinc-500">${settings.principal.toLocaleString()}</span></p>
                                            <p>• {t('Compound.YearRange')}: <span className="text-zinc-500">{settings.startYear} ~ {settings.endYear}</span></p>
                                        </div>
                                        <div className="overflow-x-auto">
                                            <table className="w-full text-sm border-collapse opacity-60">
                                                <thead>
                                                    <tr className="bg-black/30">
                                                        <th className="border border-[var(--color-border)] p-2 text-left"></th>
                                                        <th className="border border-[var(--color-border)] p-2 text-center bg-cyan-900/30 text-cyan-400">{t('Compound.BuyOpening')}</th>
                                                        <th className="border border-[var(--color-border)] p-2 text-center bg-red-900/30 text-red-400">{t('Compound.BuyHighest')}</th>
                                                        <th className="border border-[var(--color-border)] p-2 text-center bg-green-900/30 text-green-400">{t('Compound.BuyLowest')}</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <tr><td className="border border-[var(--color-border)] p-2 text-[var(--color-text-muted)]">{t('Compound.FinalValue')}</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-600">---</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-600">---</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-600">---</td></tr>
                                                    <tr><td className="border border-[var(--color-border)] p-2 text-[var(--color-text-muted)]">{t('Compound.TotalCashDiv')}</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-600">---</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-600">---</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-600">---</td></tr>
                                                    <tr><td className="border border-[var(--color-border)] p-2 text-[var(--color-text-muted)]">{t('Compound.ROI')}</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-600">---</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-600">---</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-600">---</td></tr>
                                                    <tr><td className="border border-[var(--color-border)] p-2 text-[var(--color-text-muted)]">{t('Compound.YearlyROI')}</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-600">---</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-600">---</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-600">---</td></tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                )}

                                {/* Comparison Mode Skeleton */}
                                {settings.mode === "comparison" && (
                                    <div className="overflow-x-auto">
                                        <table className="w-full text-sm border-collapse opacity-60">
                                            <thead>
                                                <tr className="bg-black/30">
                                                    <th className="border border-[var(--color-border)] p-2 text-left text-[var(--color-text-muted)]">{t('Compound.StockName')}</th>
                                                    <th className="border border-[var(--color-border)] p-2 text-center bg-cyan-900/30 text-cyan-400">{settings.stock1 || t('Compound.Stock1')}</th>
                                                    <th className="border border-[var(--color-border)] p-2 text-center bg-red-900/30 text-red-400">{settings.stock2 || t('Compound.Stock2')}</th>
                                                    <th className="border border-[var(--color-border)] p-2 text-center bg-green-900/30 text-green-400">{settings.stock3 || t('Compound.Stock3')}</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <tr><td className="border border-[var(--color-border)] p-2 text-[var(--color-text-muted)]">{t('Compound.StockCode')}</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-500">{settings.stock1}</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-500">{settings.stock2}</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-500">{settings.stock3}</td></tr>
                                                <tr><td className="border border-[var(--color-border)] p-2 text-[var(--color-text-muted)]">{t('Compound.AmountOfInv')}</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-600">${settings.principal.toLocaleString()}</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-600">${settings.principal.toLocaleString()}</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-600">${settings.principal.toLocaleString()}</td></tr>
                                                <tr><td className="border border-[var(--color-border)] p-2 text-[var(--color-text-muted)]">{t('Compound.YearRange')}</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-600">{settings.startYear} ~ {settings.endYear}</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-600">{settings.startYear} ~ {settings.endYear}</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-600">{settings.startYear} ~ {settings.endYear}</td></tr>
                                                <tr><td className="border border-[var(--color-border)] p-2 text-[var(--color-text-muted)]">{t('Compound.FinalValue')}</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-600">---</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-600">---</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-600">---</td></tr>
                                                <tr><td className="border border-[var(--color-border)] p-2 text-[var(--color-text-muted)]">{t('Compound.TotalCashDiv')}</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-600">---</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-600">---</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-600">---</td></tr>
                                                <tr><td className="border border-[var(--color-border)] p-2 text-[var(--color-text-muted)]">{t('Compound.ROI')}</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-600">---</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-600">---</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-600">---</td></tr>
                                                <tr><td className="border border-[var(--color-border)] p-2 text-[var(--color-text-muted)]">{t('Compound.YearlyROI')}</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-600">---</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-600">---</td><td className="border border-[var(--color-border)] p-2 text-center text-zinc-600">---</td></tr>
                                            </tbody>
                                        </table>
                                    </div>
                                )}
                            </div>

                            {/* Skeleton Stock Market Value Chart */}
                            <div className="bg-black/20 rounded-xl p-4 border border-[var(--color-border)]">
                                <h3 className="text-sm font-medium text-[var(--color-text-muted)] text-center mb-4">{t('Compound.StockMarketValue')}</h3>
                                <div className="h-64 flex items-end justify-around px-4 opacity-40">
                                    {[40, 42, 38, 45, 55, 52, 60, 65, 58, 70, 68, 78, 72, 85, 90, 82, 95, 105, 98, 115].map((h, i) => (
                                        <div key={i} className="w-2 bg-gradient-to-t from-cyan-500/50 to-cyan-400/20 rounded-t" style={{ height: `${h * 2}px` }} />
                                    ))}
                                </div>
                                <div className="flex justify-between text-xs text-[var(--color-text-muted)] mt-2 px-4">
                                    <span>{settings.startYear}</span>
                                    <span>{Math.floor((settings.startYear + settings.endYear) / 2)}</span>
                                    <span>{settings.endYear}</span>
                                </div>
                            </div>

                            {/* Skeleton Dividend Chart */}
                            <div className="bg-black/20 rounded-xl p-4 border border-[var(--color-border)]">
                                <h3 className="text-sm font-medium text-[var(--color-text-muted)] text-center mb-4">{t('Compound.YearlyCashDiv')}</h3>
                                <div className="h-48 flex items-end justify-around px-4 opacity-40">
                                    {[10, 12, 14, 16, 20, 22, 28, 32, 38, 45, 50, 58, 62, 72, 80, 88, 95, 105, 100, 115].map((h, i) => (
                                        <div key={i} className="w-2 bg-gradient-to-t from-green-500/50 to-green-400/20 rounded-t" style={{ height: `${h * 1.2}px` }} />
                                    ))}
                                </div>
                                <div className="flex justify-between text-xs text-[var(--color-text-muted)] mt-2 px-4">
                                    <span>{settings.startYear}</span>
                                    <span>{Math.floor((settings.startYear + settings.endYear) / 2)}</span>
                                    <span>{settings.endYear}</span>
                                </div>
                            </div>

                            <p className="text-center text-[var(--color-text-muted)] text-sm">
                                {t('Compound.ClickToCalculate', {
                                    action: settings.mode === "single"
                                        ? t('Compound.Calculate')
                                        : t('Compound.Compare')
                                })}
                            </p>

                            {/* Formula Hints - MoneyCome Rules */}
                            <div className="mt-6 pt-4 border-t border-[var(--color-border)] text-xs text-[var(--color-text-muted)] space-y-2">
                                {settings.mode === "single" ? (
                                    <>
                                        <p className="opacity-70">📐 <strong>{t('Compound.SimulationRules')}</strong></p>
                                        <ul className="list-disc list-inside opacity-60 space-y-0.5 pl-2">
                                            <li><strong>{t('Compound.TotalInvRule').split('=')[0]}</strong>={(t('Compound.TotalInvRule').split('=').slice(1).join('='))}</li>
                                            <li><strong>{t('Compound.BAORule').split(':')[0]}</strong>:{(t('Compound.BAORule').split(':').slice(1).join(':'))}</li>
                                            <li><strong>{t('Compound.BAHRule').split(':')[0]}</strong>:{(t('Compound.BAHRule').split(':').slice(1).join(':'))}</li>
                                            <li><strong>{t('Compound.BALRule').split(':')[0]}</strong>:{(t('Compound.BALRule').split(':').slice(1).join(':'))}</li>
                                            <li><strong>{t('Compound.ROIRule').split('=')[0]}</strong>={(t('Compound.ROIRule').split('=').slice(1).join('='))}</li>
                                            <li><strong>{t('Compound.CAGRRule').split('=')[0]}</strong>={(t('Compound.CAGRRule').split('=').slice(1).join('='))}</li>
                                            <li><strong>{t('Compound.CashDivRule').split('=')[0]}</strong>={(t('Compound.CashDivRule').split('=').slice(1).join('='))}</li>
                                            <li><strong>{t('Compound.DivReinvestRule').split('=')[0]}</strong>={(t('Compound.DivReinvestRule').split('=').slice(1).join('='))}</li>
                                        </ul>
                                    </>
                                ) : (
                                    <>
                                        <p className="opacity-70">📐 <strong>{t('Compound.ComparisonRules')}</strong></p>
                                        <ul className="list-disc list-inside opacity-60 space-y-0.5 pl-2">
                                            <li>{t('Compound.ComparisonRule1')}</li>
                                            <li>{t('Compound.ComparisonRule2')}</li>
                                            <li><strong>{t('Compound.CashDivRule').split('=')[0]}</strong>={(t('Compound.CashDivRule').split('=').slice(1).join('='))}</li>
                                            <li><strong>{t('Compound.DivReinvestRule').split('=')[0]}</strong>={(t('Compound.DivReinvestRule').split('=').slice(1).join('='))}</li>
                                        </ul>
                                    </>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Results with Data */}
                    {results.length > 0 && (
                        <div className="space-y-8">
                            <div>
                                <h2 className="text-lg font-bold text-[var(--color-text)] mb-4 border-b border-[var(--color-border)] pb-2">{t('Compound.Result')}</h2>

                                {/* Single Mode Results */}
                                {settings.mode === "single" && results[0] && (
                                    <div className="space-y-4">
                                        <div className="text-sm text-[var(--color-text-muted)] space-y-1 mb-4">
                                            <p>• {t('Compound.StockName')}: <strong className="text-[var(--color-text)]">{results[0].name}({results[0].code})</strong></p>
                                            <p>• {t('Compound.TotalInv')}: <strong className="text-[var(--color-text)]">${(settings.principal + (settings.endYear - settings.startYear + 1) * settings.contribution).toLocaleString()}</strong></p>
                                            <p>• {t('Compound.YearRange')}: <strong className="text-[var(--color-text)]">{settings.startYear} ~ {settings.endYear}</strong></p>
                                        </div>
                                        <div className="overflow-x-auto">
                                            <table className="w-full text-sm border-collapse">
                                                <thead>
                                                    <tr className="bg-black/30">
                                                        <th className="border border-[var(--color-border)] p-2 text-left"></th>
                                                        <th className="border border-[var(--color-border)] p-2 text-center bg-cyan-900/30 text-cyan-400">{t('Compound.BuyOpening')}</th>
                                                        <th className="border border-[var(--color-border)] p-2 text-center bg-red-900/30 text-red-400">{t('Compound.BuyHighest')}</th>
                                                        <th className="border border-[var(--color-border)] p-2 text-center bg-green-900/30 text-green-400">{t('Compound.BuyLowest')}</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <tr><td className="border border-[var(--color-border)] p-2 text-[var(--color-text-muted)]">{t('Compound.FinalValue')}</td>
                                                        <td className="border border-[var(--color-border)] p-2 text-center font-bold text-cyan-400">${(results[0].BAO?.finalValue || 0).toLocaleString()}</td>
                                                        <td className="border border-[var(--color-border)] p-2 text-center text-[var(--color-text)]">${(results[0].BAH?.finalValue || 0).toLocaleString()}</td>
                                                        <td className="border border-[var(--color-border)] p-2 text-center text-[var(--color-text)]">${(results[0].BAL?.finalValue || 0).toLocaleString()}</td>
                                                    </tr>
                                                    <tr><td className="border border-[var(--color-border)] p-2 text-[var(--color-text-muted)]">{t('Compound.TotalCashDiv')}</td>
                                                        <td className="border border-[var(--color-border)] p-2 text-center text-[var(--color-text)]">${getTotalDividends(results[0].BAO).toLocaleString()}</td>
                                                        <td className="border border-[var(--color-border)] p-2 text-center text-[var(--color-text)]">${getTotalDividends(results[0].BAH).toLocaleString()}</td>
                                                        <td className="border border-[var(--color-border)] p-2 text-center text-[var(--color-text)]">${getTotalDividends(results[0].BAL).toLocaleString()}</td>
                                                    </tr>
                                                    <tr><td className="border border-[var(--color-border)] p-2 text-[var(--color-text-muted)]">{t('Compound.ROI')}</td>
                                                        <td className="border border-[var(--color-border)] p-2 text-center font-bold text-cyan-400">{((getLastHistory(results[0].BAO)?.roi || 0)).toFixed(1)}%</td>
                                                        <td className="border border-[var(--color-border)] p-2 text-center text-blue-400">{((getLastHistory(results[0].BAH)?.roi || 0)).toFixed(1)}%</td>
                                                        <td className="border border-[var(--color-border)] p-2 text-center text-[var(--color-text)]">{((getLastHistory(results[0].BAL)?.roi || 0)).toFixed(1)}%</td>
                                                    </tr>
                                                    <tr><td className="border border-[var(--color-border)] p-2 text-[var(--color-text-muted)]">{t('Compound.YearlyROI')}</td>
                                                        <td className="border border-[var(--color-border)] p-2 text-center text-[var(--color-text)]">{((getLastHistory(results[0].BAO)?.cagr || 0)).toFixed(1)}%</td>
                                                        <td className="border border-[var(--color-border)] p-2 text-center text-[var(--color-text)]">{((getLastHistory(results[0].BAH)?.cagr || 0)).toFixed(1)}%</td>
                                                        <td className="border border-[var(--color-border)] p-2 text-center text-[var(--color-text)]">{((getLastHistory(results[0].BAL)?.cagr || 0)).toFixed(1)}%</td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                )}

                                {/* Comparison Mode Results */}
                                {settings.mode === "comparison" && results.length > 0 && (
                                    <div className="overflow-x-auto">
                                        <table className="w-full text-sm border-collapse">
                                            <thead>
                                                <tr className="bg-black/30">
                                                    <th className="border border-[var(--color-border)] p-2 text-left text-[var(--color-text-muted)]">{t('Compound.StockName')}</th>
                                                    {results.map((r, idx) => (
                                                        <th key={r.code} className={`border border-[var(--color-border)] p-2 text-center ${idx === 0 ? "bg-cyan-900/30 text-cyan-400" : idx === 1 ? "bg-red-900/30 text-red-400" : "bg-green-900/30 text-green-400"}`}>{r.name}</th>
                                                    ))}
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <tr><td className="border border-[var(--color-border)] p-2 text-[var(--color-text-muted)]">{t('Compound.StockCode')}</td>{results.map(r => <td key={r.code} className="border border-[var(--color-border)] p-2 text-center text-[var(--color-text)]">{r.code}</td>)}</tr>
                                                <tr><td className="border border-[var(--color-border)] p-2 text-[var(--color-text-muted)]">{t('Compound.AmountOfInv')}</td>{results.map(r => <td key={r.code} className="border border-[var(--color-border)] p-2 text-center text-[var(--color-text)]">${settings.principal.toLocaleString()}</td>)}</tr>
                                                <tr><td className="border border-[var(--color-border)] p-2 text-[var(--color-text-muted)]">{t('Compound.YearRange')}</td>{results.map(r => <td key={r.code} className="border border-[var(--color-border)] p-2 text-center text-[var(--color-text)]">{settings.startYear} ~ {settings.endYear}</td>)}</tr>
                                                <tr><td className="border border-[var(--color-border)] p-2 text-[var(--color-text-muted)]">{t('Compound.FinalValue')}</td>{results.map((r, idx) => <td key={r.code} className={`border border-[var(--color-border)] p-2 text-center font-bold ${idx === 0 ? "text-cyan-400" : idx === 1 ? "text-red-400" : "text-green-400"}`}>${(r.BAO?.finalValue || 0).toLocaleString()}</td>)}</tr>
                                                <tr><td className="border border-[var(--color-border)] p-2 text-[var(--color-text-muted)]">{t('Compound.TotalCashDiv')}</td>{results.map(r => <td key={r.code} className="border border-[var(--color-border)] p-2 text-center text-[var(--color-text)]">${getTotalDividends(r.BAO).toLocaleString()}</td>)}</tr>
                                                <tr><td className="border border-[var(--color-border)] p-2 text-[var(--color-text-muted)]">{t('Compound.ROI')}</td>{results.map((r, idx) => <td key={r.code} className={`border border-[var(--color-border)] p-2 text-center font-bold ${idx === 0 ? "text-cyan-400" : ""}`}>{((getLastHistory(r.BAO)?.roi || 0)).toFixed(1)}%</td>)}</tr>
                                                <tr><td className="border border-[var(--color-border)] p-2 text-[var(--color-text-muted)]">{t('Compound.YearlyROI')}</td>{results.map(r => <td key={r.code} className="border border-[var(--color-border)] p-2 text-center text-[var(--color-text)]">{((getLastHistory(r.BAO)?.cagr || 0)).toFixed(1)}%</td>)}</tr>
                                            </tbody>
                                        </table>
                                    </div>
                                )}
                            </div>

                            {/* Charts */}
                            <div className="bg-black/20 rounded-xl p-4 border border-[var(--color-border)]">
                                <ReactECharts option={wealthChartOption} style={{ height: "350px" }} notMerge={true} />
                            </div>
                            <div className="bg-black/20 rounded-xl p-4 border border-[var(--color-border)]">
                                <ReactECharts option={dividendChartOption} style={{ height: "350px" }} notMerge={true} />
                            </div>

                            {/* Formula Hints - MoneyCome Rules */}
                            <div className="mt-2 pt-4 border-t border-[var(--color-border)] text-xs text-[var(--color-text-muted)] space-y-2">
                                {settings.mode === "single" ? (
                                    <>
                                        <p className="opacity-70">📐 <strong>{t('Compound.SimulationRules')}</strong></p>
                                        <ul className="list-disc list-inside opacity-60 space-y-0.5 pl-2">
                                            <li><strong>{t('Compound.TotalInvRule').split('=')[0]}</strong>={(t('Compound.TotalInvRule').split('=').slice(1).join('='))}</li>
                                            <li><strong>{t('Compound.BAORule').split(':')[0]}</strong>:{(t('Compound.BAORule').split(':').slice(1).join(':'))}</li>
                                            <li><strong>{t('Compound.BAHRule').split(':')[0]}</strong>:{(t('Compound.BAHRule').split(':').slice(1).join(':'))}</li>
                                            <li><strong>{t('Compound.BALRule').split(':')[0]}</strong>:{(t('Compound.BALRule').split(':').slice(1).join(':'))}</li>
                                            <li><strong>{t('Compound.ROIRule').split('=')[0]}</strong>={(t('Compound.ROIRule').split('=').slice(1).join('='))}</li>
                                            <li><strong>{t('Compound.CAGRRule').split('=')[0]}</strong>={(t('Compound.CAGRRule').split('=').slice(1).join('='))}</li>
                                            <li><strong>{t('Compound.CashDivRule').split('=')[0]}</strong>={(t('Compound.CashDivRule').split('=').slice(1).join('='))}</li>
                                            <li><strong>{t('Compound.DivReinvestRule').split('=')[0]}</strong>={(t('Compound.DivReinvestRule').split('=').slice(1).join('='))}</li>
                                        </ul>
                                    </>
                                ) : (
                                    <>
                                        <p className="opacity-70">📐 <strong>{t('Compound.ComparisonRules')}</strong></p>
                                        <ul className="list-disc list-inside opacity-60 space-y-0.5 pl-2">
                                            <li>{t('Compound.ComparisonRule1')}</li>
                                            <li>{t('Compound.ComparisonRule2')}</li>
                                            <li><strong>{t('Compound.CashDivRule').split('=')[0]}</strong>={(t('Compound.CashDivRule').split('=').slice(1).join('='))}</li>
                                            <li><strong>{t('Compound.DivReinvestRule').split('=')[0]}</strong>={(t('Compound.DivReinvestRule').split('=').slice(1).join('='))}</li>
                                        </ul>
                                    </>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
