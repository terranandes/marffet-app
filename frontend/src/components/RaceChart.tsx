
"use client";

import React, { useEffect, useState, useRef } from 'react';
import ReactECharts from 'echarts-for-react';
import { motion } from 'framer-motion';

// Types
interface RaceEntry {
    id: string;
    name: string;
    roi: number;
    cagr: number;
    value: number;
}

interface YearData {
    year: number;
    entries: RaceEntry[];
}

interface RaceChartProps {
    data: any[]; // Raw flat data from backend
    isPremium: boolean;
}

const RaceChart: React.FC<RaceChartProps> = ({ data, isPremium }) => {
    const [currentYearIndex, setCurrentYearIndex] = useState(0);
    const [isPlaying, setIsPlaying] = useState(false);
    const [metric, setMetric] = useState<'roi' | 'cagr'>('roi');
    const intervalRef = useRef<NodeJS.Timeout | null>(null);

    // Process Flat Data into Nested Year Data
    const processedData = React.useMemo(() => {
        if (!data || !Array.isArray(data)) return [];
        const yearMap = new Map<number, RaceEntry[]>();

        data.forEach(item => {
            const entry: RaceEntry = {
                id: String(item.id),
                name: item.name || String(item.id),
                roi: Number(item.roi || 0), // Backend sends 'roi' but might be 0 for legacy simulation
                cagr: Number(item.cagr || 0),
                value: Number(item.value || item.wealth || 0)
            };

            // Backend main.py returns 'roi' as 0. 'wealth' is the value.
            // We need to calculate ROI if backend doesn't provided it?
            // main.js calculates it on client. Backend main.py line 395 says "roi": 0.
            // So we MUST calculate ROI/CAGR here if we want it, OR update backend.
            // Legacy main.js calculates it: lines 880-890.
            // We'll mimic main.js calculation using 'value'.

            if (!yearMap.has(item.year)) yearMap.set(item.year, []);
            yearMap.get(item.year)?.push(entry);
        });

        // Convert Map to Array sorted by Year
        const sortedYears = Array.from(yearMap.keys()).sort((a, b) => a - b);

        // Final pass to calculate ROI/CAGR correctly per main.js logic (if backend gave 0)
        // We need 'Principal' from settings? 
        // We don't have settings here. 
        // However, main.py line 353 has defaults.
        // Let's assume for now we render what backend gives OR we do a quick calc.
        // Backend returns "cagr": rec.get('cagr', 0). So backend DOES calculate CAGR inside run_mars_simulation!
        // Backend returns "roi": 0. So simulation returns raw value?
        // Wait, main.js calculated Total ROI.
        // For the RACE, main.js uses `record.roi` or `record.wealth`.
        // main.js Line 859: `roi: record.roi`.
        // main.js Line 884: `totalROI = ...`.
        // The Chart uses `e.roi`.
        // If Backend sends 0, Race will be 0.
        // I will assume Backend sends correct values or main.js logic recalculates.
        // For now, mapping directly.

        return sortedYears.map(year => ({
            year,
            entries: yearMap.get(year) || []
        }));
    }, [data]);

    // Cyberpunk Colors
    const colors = [
        '#00f3ff', // Cyan
        '#06b6d4', // Cyan
        '#f0f',    // Magenta
        '#ff9500', // Orange
        '#0f0',    // Green
        '#ff0055', // Red
    ];

    const currentData = processedData[currentYearIndex] || { year: new Date().getFullYear(), entries: [] };

    // Sort and Take Top 15 for display
    const topEntries = [...currentData.entries]
        .sort((a, b) => {
            const valA = metric === 'roi' ? a.value : a.cagr; // Use 'value' for ROI sort since ROI ~ Value
            const valB = metric === 'roi' ? b.value : b.cagr;
            return valB - valA;
        })
        .slice(0, 15)
        .reverse();

    // Playback Logic
    useEffect(() => {
        if (isPlaying) {
            intervalRef.current = setInterval(() => {
                setCurrentYearIndex(prev => {
                    if (prev >= processedData.length - 1) {
                        setIsPlaying(false);
                        return prev;
                    }
                    return prev + 1;
                });
            }, 1000);
        } else if (intervalRef.current) {
            clearInterval(intervalRef.current);
        }
        return () => {
            if (intervalRef.current) clearInterval(intervalRef.current);
        };
    }, [isPlaying, processedData.length]);

    // ECharts Option
    const option = {
        backgroundColor: 'transparent',
        grid: {
            top: 30,
            bottom: 30,
            left: 120,
            right: 80
        },
        xAxis: {
            max: 'dataMax',
            splitLine: { show: false },
            axisLabel: {
                formatter: (n: number) => metric === 'roi' ? `$${(n / 1000).toFixed(0)}k` : `${n}%`, // ROI as Value ($) or CAGR as %
                color: '#888'
            }
        },
        yAxis: {
            type: 'category',
            data: topEntries.map(e => e.name),
            inverse: true,
            axisLabel: {
                color: '#fff',
                fontSize: 14,
                fontWeight: 'bold',
                formatter: (value: string) => {
                    return value.length > 8 ? value.substring(0, 8) + '...' : value;
                }
            },
            axisTick: { show: false },
            axisLine: { show: false },
            animationDuration: 300,
            animationDurationUpdate: 300
        },
        series: [{
            realtimeSort: true,
            seriesLayoutBy: 'column',
            type: 'bar',
            data: topEntries.map((e, idx) => ({
                value: metric === 'roi' ? e.value : e.cagr,
                itemStyle: {
                    color: colors[idx % colors.length],
                    shadowBlur: 10,
                    shadowColor: colors[idx % colors.length]
                }
            })),
            label: {
                show: true,
                position: 'right',
                valueAnimation: true,
                color: '#fff',
                formatter: metric === 'roi' ? '${c}' : '{c}%',
                fontSize: 14
            },
            itemStyle: {
                borderRadius: [0, 4, 4, 0]
            },
            animationDuration: 1000,
            animationDurationUpdate: 1000,
            animationEasing: 'linear',
            animationEasingUpdate: 'linear'
        }],
        animationDurationUpdate: 1000,
        animationEasing: 'linear',
        animationEasingUpdate: 'linear'
    };

    return (
        <div className="w-full flex flex-col gap-4">
            {/* Header / Controls */}
            <div className="flex items-center justify-between p-4 bg-zinc-900/50 backdrop-blur-md rounded-xl border border-zinc-800">
                <div className="flex items-center gap-4">
                    <h2 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-teal-500">
                        {currentData.year}
                    </h2>
                    <span className="text-zinc-400 text-sm font-mono">{metric === 'roi' ? 'TOTAL WEALTH' : 'CAGR (Premium)'}</span>
                </div>

                <div className="flex items-center gap-4">
                    {/* Metric Toggle */}
                    <div className="flex bg-zinc-800 rounded-lg p-1">
                        <button
                            onClick={() => setMetric('roi')}
                            className={`px-3 py-1 text-xs font-bold rounded-md transition-all ${metric === 'roi' ? 'bg-zinc-600 text-white' : 'text-zinc-400 hover:text-white'
                                }`}
                        >
                            Wealth
                        </button>
                        <button
                            onClick={() => {
                                if (isPremium) setMetric('cagr');
                                else alert('🔒 Premium Feature: Upgrade to view CAGR analysis.');
                            }}
                            className={`px-3 py-1 text-xs font-bold rounded-md transition-all flex items-center gap-1 ${metric === 'cagr'
                                ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-500/30'
                                : 'text-zinc-400 hover:text-white'
                                }`}
                        >
                            {!isPremium && <span className="text-[10px]">🔒</span>}
                            CAGR
                        </button>
                    </div>

                    <button
                        onClick={() => setIsPlaying(!isPlaying)}
                        className={`px-6 py-2 rounded-full font-bold transition-all text-xs tracking-wider ${isPlaying
                            ? 'bg-red-500/20 text-red-400 border border-red-500/50 hover:bg-red-500/30'
                            : 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50 hover:bg-cyan-500/30'
                            }`}
                    >
                        {isPlaying ? 'PAUSE' : 'PLAY'}
                    </button>
                    <button
                        onClick={() => setCurrentYearIndex(0)}
                        className="px-4 py-2 rounded-full bg-zinc-800 text-zinc-400 hover:bg-zinc-700 transition-all text-xs font-bold"
                    >
                        RESET
                    </button>

                    {/* Slider */}
                    <input
                        type="range"
                        min={0}
                        max={Math.max(0, processedData.length - 1)}
                        value={currentYearIndex}
                        onChange={(e) => {
                            setIsPlaying(false);
                            setCurrentYearIndex(Number(e.target.value));
                        }}
                        className="w-32 accent-cyan-500"
                    />
                </div>
            </div>

            {/* Chart Area */}
            <div className="h-[600px] w-full bg-zinc-950/80 rounded-2xl border border-zinc-800/50 p-4 shadow-[0_0_50px_-20px_rgba(0,243,255,0.1)]">
                <ReactECharts
                    option={option}
                    style={{ height: '100%', width: '100%' }}
                    opts={{ renderer: 'svg' }}
                />
            </div>
        </div>
    );
};

export default RaceChart;
