"use client";

import React, { useEffect, useState } from 'react';

interface CacheStatus {
    ready: boolean;
    years: number;
    oldest: string;
    newest: string;
}

const DataTimestamp: React.FC = () => {
    const [status, setStatus] = useState<CacheStatus | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStatus = async () => {
            try {
                // Use relative path to leverage Next.js rewrites
                const res = await fetch('/api/health/cache');
                if (res.ok) {
                    const data = await res.json();
                    setStatus(data);
                }
            } catch (error) {
                console.error("Failed to fetch cache status", error);
            } finally {
                setLoading(false);
            }
        };

        fetchStatus();
        const interval = setInterval(fetchStatus, 30000); // 30s refresh
        return () => clearInterval(interval);
    }, []);

    if (loading) return <div className="text-xs text-center text-zinc-600 animate-pulse mt-2">Loading data status...</div>;

    // If not ready, show warming up message
    if (!status || !status.ready) {
        return (
            <div className="flex items-center justify-center gap-2 mt-2">
                <div className="w-2 h-2 rounded-full bg-yellow-500 animate-ping"></div>
                <div className="text-xs text-yellow-500 font-medium">Warming up data...</div>
            </div>
        );
    }

    return (
        <div className="flex flex-col items-center gap-1 mt-2">
            <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]"></div>
                <div className="text-xs text-zinc-400">Data as of: <span className="text-zinc-300 font-mono">{status.newest}</span></div>
            </div>
        </div>
    );
};

export default DataTimestamp;
