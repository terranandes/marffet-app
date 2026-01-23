
"use client";

import React, { useEffect, useState } from 'react';
import RaceChart from '@/components/RaceChart';

export default function VisualizationPage() {
    const [user, setUser] = useState<any>(null);

    useEffect(() => {
        const fetchData = async () => {
            // Fetch User Status
            try {
                const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
                const userRes = await fetch(`${API_URL}/auth/me`, { credentials: "include" });
                if (userRes.ok) {
                    const userData = await userRes.json();
                    setUser(userData);
                }
            } catch (e) { console.error("Auth check failed", e); }

            try {
                // Settings from Mars Page
                let params = "";
                const saved = localStorage.getItem("mars_sim_settings");
                if (saved) {
                    const sim = JSON.parse(saved);
                    params = `?start_year=${sim.startYear}&principal=${sim.principal}&contribution=${sim.contribution}`;
                } else {
                    // Default fallback if no settings found
                    params = "?start_year=2006&principal=1000000&contribution=60000";
                }

                const res = await fetch(`/api/race-data${params}`);
                if (!res.ok) throw new Error("Failed to fetch");
                const json = await res.json();
                setData(json);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    // Helper to check premium
    const isPremium = user?.is_admin || (user?.subscription_tier && user.subscription_tier > 0);

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
                            <RaceChart data={data} isPremium={!!isPremium} />
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
