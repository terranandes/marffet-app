"use client";

import { useEffect } from "react";
import { useLanguage } from "@/lib/i18n/LanguageContext";

export default function GlobalError({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    const { t } = useLanguage();

    useEffect(() => {
        // Log the error to an error reporting service natively for now
        console.error("Global Error Caught by Boundary:", error);
    }, [error]);

    return (
        <div className="min-h-[70vh] flex flex-col items-center justify-center p-6 text-center animate-fade-in">
            <div className="w-24 h-24 rounded-full bg-red-900/20 border border-red-500/30 flex items-center justify-center mb-6 shadow-[0_0_30px_rgba(239,68,68,0.2)]">
                <span className="text-4xl">⚠️</span>
            </div>
            <h2 className="text-2xl font-bold text-white mb-3">
                System Render Error
            </h2>
            <p className="text-zinc-400 max-w-md mx-auto mb-8">
                An unexpected condition crashed this view. This can happen during mobile switching or heavy calculation.
            </p>
            <div className="flex gap-4 items-center">
                <button
                    onClick={() => reset()}
                    className="px-6 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 font-bold rounded-xl text-white shadow-lg hover:shadow-cyan-500/20 transition-all border border-transparent hover:border-cyan-400/30"
                >
                    Recover System
                </button>
                <button
                    onClick={() => window.location.href = '/'}
                    className="px-6 py-3 bg-zinc-800 font-bold rounded-xl text-white hover:bg-zinc-700 transition-all border border-zinc-700"
                >
                    Go Dashboard
                </button>
            </div>
        </div>
    );
}
