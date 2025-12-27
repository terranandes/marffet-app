"use client";

import { useEffect, useState } from "react";

interface Stock {
    id: string;
    name: string;
    price: number;
    cagr_pct: number;
    cagr_std: number;
    valid_years: number;
}

export default function MarsPage() {
    const [stocks, setStocks] = useState<Stock[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch("http://localhost:8000/api/stocks")
            .then((res) => res.json())
            .then((data) => {
                setStocks(data);
                setLoading(false);
            })
            .catch((err) => {
                console.error("Failed to fetch stocks:", err);
                setLoading(false);
            });
    }, []);

    return (
        <div className="max-w-6xl mx-auto">
            <header className="mb-10">
                <h1 className="text-3xl font-bold mb-2 bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
                    Mars Strategy
                </h1>
                <p className="text-zinc-400">
                    Low Volatility Portfolio Selection via Gaussian Filtering
                </p>
            </header>

            {loading ? (
                <div className="text-center py-20 animate-pulse text-zinc-500">
                    Loading Market Data...
                </div>
            ) : (
                <div className="overflow-x-auto rounded-xl border border-zinc-800 shadow-2xl bg-zinc-900/50 backdrop-blur-sm">
                    <table className="w-full text-left text-sm text-zinc-300">
                        <thead className="bg-zinc-900 uppercase text-xs text-zinc-500 tracking-wider">
                            <tr>
                                <th className="px-6 py-4">Stock</th>
                                <th className="px-6 py-4 text-right">Price</th>
                                <th className="px-6 py-4 text-right">CAGR (%)</th>
                                <th className="px-6 py-4 text-right">Vol (Std)</th>
                                <th className="px-6 py-4 text-center">Years</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-zinc-800">
                            {stocks.slice(0, 100).map((stock) => (
                                <tr
                                    key={stock.id}
                                    className="hover:bg-zinc-800/50 transition-colors duration-150"
                                >
                                    <td className="px-6 py-4 font-medium text-white">
                                        <div className="flex flex-col">
                                            <span className="text-base">{stock.name}</span>
                                            <span className="text-xs text-zinc-500">{stock.id}</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-right font-mono">
                                        {stock.price?.toFixed(2)}
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        <span
                                            className={`font-bold ${stock.cagr_pct > 20
                                                    ? "text-green-400"
                                                    : stock.cagr_pct > 10
                                                        ? "text-yellow-400"
                                                        : "text-zinc-400"
                                                }`}
                                        >
                                            {stock.cagr_pct?.toFixed(1)}%
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-right font-mono text-zinc-400">
                                        {stock.cagr_std?.toFixed(2)}
                                    </td>
                                    <td className="px-6 py-4 text-center text-zinc-500">
                                        {stock.valid_years}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    <div className="p-4 text-center text-xs text-zinc-600 border-t border-zinc-800">
                        Showing top 100 of {stocks.length} filtered results.
                    </div>
                </div>
            )}
        </div>
    );
}
