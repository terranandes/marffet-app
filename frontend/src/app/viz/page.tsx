
"use client";

import React, { useEffect, useState } from 'react';
import RaceChart from '@/components/RaceChart';

export default function VisualizationPage() {
    const [data, setData] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Fetch Race Data from Backend
        // URL: http://localhost:8000/api/race-data (Assuming proxy or CORS)
        // Next.js Dev Setups usually need explicit absolute URL or proxy.
        // We'll try relative if rewrites are set, or absolute.
        const fetchData = async () => {
            try {
                const res = await fetch('/api/race-data');
                if (!res.ok) throw new Error("Failed to fetch");
                const json = await res.json();
                setData(json);
            } catch (err) {
                console.error(err);
                // Fallback / Initial State?
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    return (
        <main className="min-h-screen bg-[#050505] text-white p-8">
            <header className="mb-12 cursor-default">
                <h1 className="text-5xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 mb-2">
                    MARS VISUALIZATION
                </h1>
                <p className="text-zinc-500 text-lg font-mono uppercase tracking-widest">
                    Time-Series ROI Analysis /// Project Martian
                </p>
            </header>

            <section className="w-full max-w-7xl mx-auto">
                {loading ? (
                    <div className="flex items-center justify-center h-96">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-500"></div>
                    </div>
                ) : (
                    <div className="bg-zinc-900/30 backdrop-blur-sm border border-zinc-800 rounded-3xl p-6 shadow-2xl">
                        {data.length > 0 ? (
                            <RaceChart data={data} />
                        ) : (
                            <div className="text-center py-20 text-zinc-500">
                                No Race Data Available. <br />
                                <span className="text-xs text-zinc-700">Ensure Backend is running and 'stock_list' exists.</span>
                            </div>
                        )}
                    </div>
                )}
            </section>
        </main>
    );
}
