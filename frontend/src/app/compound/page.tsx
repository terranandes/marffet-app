"use client";

import { useState, useEffect } from "react";

interface CompoundSettings {
    mode: "single" | "comparison";
    // Single Mode
    stockCode: string; // Default 2330
    // Comparison Mode
    stock1: string; // Default 0050
    stock2: string; // Default 2330
    stock3: string; // Default 2383

    // Shared Settings
    startYear: number;
    endYear: number;
    principal: number;
    contribution: number;
}

export default function CompoundPage() {
    const currentYear = new Date().getFullYear();

    // State
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

    // Current URL for iframe
    const [iframeUrl, setIframeUrl] = useState("");

    // Mobile Settings Toggle
    const [showSettings, setShowSettings] = useState(false);

    // Initial Load
    useEffect(() => {
        updateUrl();
    }, []);

    // Update URL based on settings
    const updateUrl = () => {
        const queryParams = new URLSearchParams({
            startYear: settings.startYear.toString(),
            endYear: settings.endYear.toString(),
            principal: settings.principal.toString(),
            contribution: settings.contribution.toString()
        });

        if (settings.mode === "single") {
            // Append stockCode
            queryParams.append("stkCode", settings.stockCode);
            setIframeUrl(`https://moneycome.in/tool/compound_interest?${queryParams.toString()}`);
        } else {
            // Filter out empty stocks
            const stocks = [settings.stock1, settings.stock2, settings.stock3].filter(s => s.trim() !== "").join(",");
            queryParams.append("stkCodes", stocks);
            setIframeUrl(`https://moneycome.in/tool/compound_interest_comparison?${queryParams.toString()}`);
        }
    };

    return (
        <div className="flex flex-col lg:flex-row gap-6 h-[calc(100vh-100px)]">
            {/* Sidebar - Settings */}
            <aside className="w-full lg:w-72 flex-shrink-0 space-y-4">
                {/* Mobile Toggle Header */}
                <div
                    className="md:hidden flex items-center justify-between p-4 glass-card rounded-xl cursor-pointer active:scale-95 transition-transform"
                    onClick={() => setShowSettings(!showSettings)}
                >
                    <span className="font-bold text-[var(--color-primary)] uppercase text-xs tracking-wider">
                        ⚙️ Calculator Settings
                    </span>
                    <span className={`transform transition-transform ${showSettings ? 'rotate-180' : ''}`}>
                        ▼
                    </span>
                </div>

                <div className={`${showSettings ? 'block' : 'hidden'} md:block glass-card p-5 rounded-xl h-fit`}>
                    <h3 className="hidden md:block text-[var(--color-primary)] font-bold mb-4 uppercase text-xs tracking-wider border-b border-[var(--color-border)] pb-2">
                        Configuration
                    </h3>

                    <div className="space-y-4">
                        {/* Mode Selector */}
                        <div>
                            <label className="block text-xs text-[var(--color-text-muted)] mb-1">Mode</label>
                            <div className="flex bg-black/50 rounded p-1 border border-[var(--color-border)]">
                                <button
                                    onClick={() => setSettings({ ...settings, mode: "single" })}
                                    className={`flex-1 py-1.5 text-xs font-bold rounded transition ${settings.mode === "single" ? "bg-[var(--color-cta)] text-black" : "text-zinc-400 hover:text-white"}`}
                                >
                                    Single
                                </button>
                                <button
                                    onClick={() => setSettings({ ...settings, mode: "comparison" })}
                                    className={`flex-1 py-1.5 text-xs font-bold rounded transition ${settings.mode === "comparison" ? "bg-purple-500 text-white" : "text-zinc-400 hover:text-white"}`}
                                >
                                    Comparison
                                </button>
                            </div>
                        </div>

                        {settings.mode === "single" ? (
                            /* Single Mode Inputs */
                            <div>
                                <label className="block text-xs text-[var(--color-text-muted)] mb-1">
                                    Stock Code
                                </label>
                                <input
                                    type="text"
                                    value={settings.stockCode}
                                    onChange={(e) => setSettings({ ...settings, stockCode: e.target.value })}
                                    className="w-full bg-black/50 border border-[var(--color-border)] rounded px-3 py-2 text-sm focus:border-[var(--color-cta)] outline-none transition font-mono"
                                    placeholder="e.g. 2330"
                                />
                            </div>
                        ) : (
                            /* Comparison Mode Inputs */
                            <div className="space-y-3">
                                <div>
                                    <label className="block text-xs text-[var(--color-text-muted)] mb-1">Stock 1</label>
                                    <input
                                        type="text"
                                        value={settings.stock1}
                                        onChange={(e) => setSettings({ ...settings, stock1: e.target.value })}
                                        className="w-full bg-black/50 border border-[var(--color-border)] rounded px-3 py-2 text-sm focus:border-purple-500 outline-none transition font-mono"
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs text-[var(--color-text-muted)] mb-1">Stock 2</label>
                                    <input
                                        type="text"
                                        value={settings.stock2}
                                        onChange={(e) => setSettings({ ...settings, stock2: e.target.value })}
                                        className="w-full bg-black/50 border border-[var(--color-border)] rounded px-3 py-2 text-sm focus:border-purple-500 outline-none transition font-mono"
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs text-[var(--color-text-muted)] mb-1">Stock 3 (Optional)</label>
                                    <input
                                        type="text"
                                        value={settings.stock3}
                                        onChange={(e) => setSettings({ ...settings, stock3: e.target.value })}
                                        className="w-full bg-black/50 border border-[var(--color-border)] rounded px-3 py-2 text-sm focus:border-purple-500 outline-none transition font-mono"
                                    />
                                </div>
                            </div>
                        )}

                        {/* Shared Simulation Settings */}
                        <div className="pt-2 border-t border-[var(--color-border)] space-y-3">
                            <div className="grid grid-cols-2 gap-2">
                                <div>
                                    <label className="block text-xs text-[var(--color-text-muted)] mb-1">Start Year</label>
                                    <input
                                        type="number"
                                        value={settings.startYear}
                                        onChange={(e) => setSettings({ ...settings, startYear: Number(e.target.value) })}
                                        className="w-full bg-black/50 border border-[var(--color-border)] rounded px-2 py-2 text-sm focus:border-blue-500 outline-none transition font-mono"
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs text-[var(--color-text-muted)] mb-1">End Year</label>
                                    <input
                                        type="number"
                                        value={settings.endYear}
                                        onChange={(e) => setSettings({ ...settings, endYear: Number(e.target.value) })}
                                        className="w-full bg-black/50 border border-[var(--color-border)] rounded px-2 py-2 text-sm focus:border-blue-500 outline-none transition font-mono"
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="block text-xs text-[var(--color-text-muted)] mb-1">
                                    Initial Capital ($)
                                </label>
                                <input
                                    type="number"
                                    step={10000}
                                    value={settings.principal}
                                    onChange={(e) => setSettings({ ...settings, principal: Number(e.target.value) })}
                                    className="w-full bg-black/50 border border-[var(--color-border)] rounded px-3 py-2 text-sm focus:border-blue-500 outline-none transition font-mono"
                                />
                            </div>

                            <div>
                                <label className="block text-xs text-[var(--color-text-muted)] mb-1">
                                    Annual Contribution ($)
                                </label>
                                <input
                                    type="number"
                                    step={10000}
                                    value={settings.contribution}
                                    onChange={(e) => setSettings({ ...settings, contribution: Number(e.target.value) })}
                                    className="w-full bg-black/50 border border-[var(--color-border)] rounded px-3 py-2 text-sm focus:border-blue-500 outline-none transition font-mono"
                                />
                            </div>
                        </div>

                        <button
                            onClick={updateUrl}
                            className={`w-full font-bold py-2 rounded transition cursor-pointer mt-4 ${settings.mode === "single"
                                ? "bg-[var(--color-cta)]/10 border border-[var(--color-cta)] text-[var(--color-cta)] hover:bg-[var(--color-cta)] hover:text-black"
                                : "bg-purple-500/10 border border-purple-500 text-purple-400 hover:bg-purple-500 hover:text-white"
                                }`}
                        >
                            {settings.mode === "single" ? "Calculate ROI" : "Compare Assets"}
                        </button>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <div className="flex-1 flex flex-col h-full glass-card rounded-xl overflow-hidden border border-[var(--color-border)]">
                <header className="p-4 border-b border-[var(--color-border)] bg-black/20 flex justify-between items-center">
                    <h1 className="text-xl font-bold flex items-center gap-2">
                        {settings.mode === "single" ? (
                            <>
                                <span className="text-2xl">📈</span>
                                <span className="text-[var(--color-cta)]">Compound Interest</span>
                            </>
                        ) : (
                            <>
                                <span className="text-2xl">⚖️</span>
                                <span className="text-purple-400">Asset Comparison</span>
                            </>
                        )}
                    </h1>
                    <div className="text-xs text-[var(--color-text-muted)] flex items-center gap-1">
                        Powered by <span className="font-bold text-white">MoneyCome</span>
                    </div>
                </header>

                <div className="flex-1 bg-white relative">
                    <iframe
                        key={iframeUrl} // Force reload on URL change
                        src={iframeUrl}
                        className="w-full h-full border-0 absolute inset-0"
                        title="MoneyCome Compound Interest"
                        sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
                    />
                </div>
            </div>
        </div>
    );
}
