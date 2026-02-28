"use client";

interface SkeletonProps {
    className?: string;
    variant?: "text" | "circle" | "rect" | "chart" | "table-row";
    count?: number;
}

export function Skeleton({ className = "", variant = "rect", count = 1 }: SkeletonProps) {
    const baseClass = "animate-pulse bg-zinc-800/60 rounded";

    const variantClass = {
        text: "h-4 w-3/4 rounded",
        circle: "h-10 w-10 rounded-full",
        rect: "h-20 w-full rounded-lg",
        chart: "h-64 w-full rounded-lg",
        "table-row": "h-10 w-full rounded",
    }[variant];

    return (
        <>
            {Array.from({ length: count }).map((_, i) => (
                <div key={i} className={`${baseClass} ${variantClass} ${className}`} />
            ))}
        </>
    );
}

export function TableSkeleton({ rows = 8, cols = 6 }: { rows?: number; cols?: number }) {
    return (
        <div className="space-y-2 p-4">
            {/* Header */}
            <div className="grid gap-3" style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}>
                {Array.from({ length: cols }).map((_, i) => (
                    <div key={i} className="animate-pulse bg-zinc-700/50 h-8 rounded" />
                ))}
            </div>
            {/* Rows */}
            {Array.from({ length: rows }).map((_, r) => (
                <div key={r} className="grid gap-3" style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}>
                    {Array.from({ length: cols }).map((_, c) => (
                        <div key={c} className="animate-pulse bg-zinc-800/40 h-10 rounded" />
                    ))}
                </div>
            ))}
        </div>
    );
}

export function ChartSkeleton({ height = "h-64" }: { height?: string }) {
    return (
        <div className={`animate-pulse bg-zinc-800/40 ${height} w-full rounded-lg flex items-end justify-center gap-1 p-6`}>
            {Array.from({ length: 12 }).map((_, i) => (
                <div
                    key={i}
                    className="bg-zinc-700/50 rounded-t w-full"
                    style={{ height: `${20 + Math.sin(i * 0.8) * 30 + 25}%` }}
                />
            ))}
        </div>
    );
}

export function LeaderboardSkeleton({ rows = 10 }: { rows?: number }) {
    return (
        <div className="space-y-3 p-4">
            {Array.from({ length: rows }).map((_, i) => (
                <div key={i} className="flex items-center gap-4 animate-pulse">
                    <div className="bg-zinc-700/50 h-8 w-8 rounded-full" />
                    <div className="flex-1 space-y-2">
                        <div className="bg-zinc-800/40 h-4 w-1/3 rounded" />
                        <div className="bg-zinc-800/40 h-3 w-full rounded" />
                    </div>
                    <div className="bg-zinc-800/40 h-6 w-16 rounded" />
                </div>
            ))}
        </div>
    );
}

export function CardGridSkeleton({ count = 4 }: { count?: number }) {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-4">
            {Array.from({ length: count }).map((_, i) => (
                <div key={i} className="animate-pulse bg-zinc-800/40 rounded-xl p-6 space-y-3">
                    <div className="bg-zinc-700/50 h-6 w-1/2 rounded" />
                    <div className="bg-zinc-700/40 h-4 w-3/4 rounded" />
                    <div className="bg-zinc-700/30 h-32 w-full rounded-lg" />
                </div>
            ))}
        </div>
    );
}
