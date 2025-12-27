
"use client";

import React, { useEffect, useState, useRef } from 'react';
import ReactECharts from 'echarts-for-react';
import { motion } from 'framer-motion';

// Types
interface RaceEntry {
    id: string;
    name: string;
    roi: number;
}

interface YearData {
    year: number;
    entries: RaceEntry[];
}

interface RaceChartProps {
    data: YearData[];
}

const RaceChart: React.FC<RaceChartProps> = ({ data }) => {
    const [currentYearIndex, setCurrentYearIndex] = useState(0);
    const [isPlaying, setIsPlaying] = useState(false);
    const intervalRef = useRef<NodeJS.Timeout | null>(null);

    // Cyberpunk Colors
    const colors = [
        '#00f3ff', // Cyan
        '#bc13fe', // Purple
        '#f0f',    // Magenta
        '#ff9500', // Orange
        '#0f0',    // Green
        '#ff0055', // Red
    ];

    const currentData = data[currentYearIndex] || { year: 2006, entries: [] };

    // Sort and Take Top 15 for display
    const topEntries = [...currentData.entries]
        .sort((a, b) => b.roi - a.roi)
        .slice(0, 15)
        .reverse(); // ECharts Y-axis is bottom-up for category by default? No, usually top-down inverted.

    // Playback Logic
    useEffect(() => {
        if (isPlaying) {
            intervalRef.current = setInterval(() => {
                setCurrentYearIndex(prev => {
                    if (prev >= data.length - 1) {
                        setIsPlaying(false);
                        return prev;
                    }
                    return prev + 1;
                });
            }, 1000); // 1.5s per year
        } else if (intervalRef.current) {
            clearInterval(intervalRef.current);
        }
        return () => {
            if (intervalRef.current) clearInterval(intervalRef.current);
        };
    }, [isPlaying, data.length]);

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
                formatter: (n: number) => `${n}%`,
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
                value: e.roi,
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
                formatter: '{c}%',
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
                    <h2 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-500">
                        {currentData.year}
                    </h2>
                    <span className="text-zinc-400 text-sm">Martian ROI Race</span>
                </div>

                <div className="flex gap-2">
                    <button
                        onClick={() => setIsPlaying(!isPlaying)}
                        className={`px-6 py-2 rounded-full font-bold transition-all ${isPlaying
                                ? 'bg-red-500/20 text-red-400 border border-red-500/50 hover:bg-red-500/30'
                                : 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50 hover:bg-cyan-500/30'
                            }`}
                    >
                        {isPlaying ? 'PAUSE' : 'PLAY'}
                    </button>
                    <button
                        onClick={() => setCurrentYearIndex(0)}
                        className="px-4 py-2 rounded-full bg-zinc-800 text-zinc-400 hover:bg-zinc-700 transition-all"
                    >
                        RESET
                    </button>

                    {/* Slider */}
                    <input
                        type="range"
                        min={0}
                        max={data.length - 1}
                        value={currentYearIndex}
                        onChange={(e) => {
                            setIsPlaying(false);
                            setCurrentYearIndex(Number(e.target.value));
                        }}
                        className="w-48 accent-cyan-500"
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
