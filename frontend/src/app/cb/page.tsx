"use client";

import { useEffect, useState } from "react";

interface CBSignal {
    stock_id: string;
    cb_id: string;
    premium_rate: number;
    signal: string;
    action_detail: string;
}

export default function CBPage() {
    const [signals, setSignals] = useState<CBSignal[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Mock Data for now, waiting for backend implementation
        // Format matches the JSON schema defined in implementation_plan.md
        const mockData: CBSignal[] = [
            {
                stock_id: "2330",
                cb_id: "23301",
                premium_rate: -1.5,
                signal: "Arbitrage",
                action_detail: "Buy CB, Sell Stock"
            },
            {
                stock_id: "2609",
                cb_id: "26091",
                premium_rate: 2.1,
                signal: "Buy",
                action_detail: "Consider Buy CB"
            },
            {
                stock_id: "2603",
                cb_id: "26034",
                premium_rate: 8.5,
                signal: "Hold",
                action_detail: "Hold Position"
            },
            {
                stock_id: "2317",
                cb_id: "23171",
                premium_rate: 35.0,
                signal: "Sell",
                action_detail: "Immediately Sell CB"
            }
        ];

        setTimeout(() => {
            setSignals(mockData);
            setLoading(false);
        }, 800);
    }, []);

    const getSignalColor = (signal: string) => {
        switch (signal) {
            case "Arbitrage": return "text-purple-400 bg-purple-400/10 border-purple-400/20";
            case "Buy": return "text-green-400 bg-green-400/10 border-green-400/20";
            case "Hold": return "text-zinc-400 bg-zinc-800 border-zinc-700";
            case "Sell": return "text-red-400 bg-red-400/10 border-red-400/20";
            default: return "text-zinc-500";
        }
    };

    return (
        <div className="max-w-6xl mx-auto">
            <header className="mb-10">
                <h1 className="text-3xl font-bold mb-2 bg-gradient-to-r from-emerald-400 to-green-600 bg-clip-text text-transparent">
                    CB Strategy
                </h1>
                <p className="text-zinc-400">
                    Convertible Bond Arbitrage & Hedging Signals (Premium Rate Analysis)
                </p>
            </header>

            {loading ? (
                <div className="text-center py-20 animate-pulse text-zinc-500">
                    Loading Strategy Signals...
                </div>
            ) : (
                <div className="grid gap-4">
                    {/* Summary Metrics or Cards could go here */}

                    <div className="overflow-x-auto rounded-xl border border-zinc-800 shadow-2xl bg-zinc-900/50 backdrop-blur-sm">
                        <table className="w-full text-left text-sm text-zinc-300">
                            <thead className="bg-zinc-900 uppercase text-xs text-zinc-500 tracking-wider">
                                <tr>
                                    <th className="px-6 py-4">Stock</th>
                                    <th className="px-6 py-4">CB Code</th>
                                    <th className="px-6 py-4 text-right">Premium (%)</th>
                                    <th className="px-6 py-4 text-center">Signal</th>
                                    <th className="px-6 py-4">Action Detail</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-zinc-800">
                                {signals.map((item) => (
                                    <tr
                                        key={item.cb_id}
                                        className="hover:bg-zinc-800/50 transition-colors duration-150"
                                    >
                                        <td className="px-6 py-4 font-bold text-white">
                                            {item.stock_id}
                                        </td>
                                        <td className="px-6 py-4 font-mono text-zinc-400">
                                            {item.cb_id}
                                        </td>
                                        <td className="px-6 py-4 text-right font-mono">
                                            <span className={item.premium_rate < 0 ? "text-purple-400" : "text-zinc-300"}>
                                                {item.premium_rate.toFixed(2)}%
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-center">
                                            <span className={`px-3 py-1 rounded-full text-xs border ${getSignalColor(item.signal)}`}>
                                                {item.signal}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-zinc-400">
                                            {item.action_detail}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
}
