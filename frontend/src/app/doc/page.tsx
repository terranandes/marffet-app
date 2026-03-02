"use client";

import Link from "next/link";

export default function DocPage() {
    return (
        <div className="min-h-screen bg-[#0e1117] text-gray-300 font-sans p-8">
            <div className="max-w-4xl mx-auto">
                {/* Header */}
                <div className="flex items-center justify-between mb-12 border-b border-white/10 pb-6">
                    <h1 className="text-4xl font-bold text-white tracking-tight">
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
                            Marffet
                        </span>{" "}
                        Investment System
                    </h1>
                    <Link
                        href="/"
                        className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg transition border border-white/10 text-sm font-bold"
                    >
                        ← Back to App
                    </Link>
                </div>

                {/* Content */}
                <div className="prose prose-invert max-w-none prose-headings:text-cyan-400 prose-a:text-cyan-400 hover:prose-a:text-cyan-300 prose-strong:text-white">
                    <div className="mb-8 p-6 bg-white/5 border border-cyan-500/20 rounded-2xl">
                        <p className="text-xl text-white font-medium leading-relaxed m-0">
                            <strong>Project Marffet</strong> (Martian + Buffet) is a high-performance investment simulation and tracking tool designed to prove the "Top 50 Past Performers" strategy.
                        </p>
                    </div>

                    <h2>🌟 Key Features</h2>

                    <div className="grid md:grid-cols-2 gap-6 my-8 not-prose">
                        <div className="p-6 bg-zinc-900/50 border border-white/10 rounded-xl">
                            <h3 className="text-xl font-bold text-cyan-400 mb-2">1. Mars Strategy</h3>
                            <ul className="space-y-2 text-sm text-gray-400">
                                <li>Is History cyclical? The philosophy is simple: Winners keep winning.</li>
                                <li>Backtest the "Top 50 Strategy" over 20+ years of TW market data.</li>
                                <li>Customizable simulation parameters.</li>
                            </ul>
                        </div>
                        <div className="p-6 bg-zinc-900/50 border border-white/10 rounded-xl">
                            <h3 className="text-xl font-bold text-yellow-500 mb-2">2. Bar Chart Race</h3>
                            <ul className="space-y-2 text-sm text-gray-400">
                                <li>Visual proof of compounding wealth.</li>
                                <li>Watch "Boring" stocks overtake volatile ones over time.</li>
                                <li>Dynamic, animated visualization.</li>
                            </ul>
                        </div>
                        <div className="p-6 bg-zinc-900/50 border border-white/10 rounded-xl">
                            <h3 className="text-xl font-bold text-amber-400 mb-2">3. Portfolio & Leaderboard</h3>
                            <ul className="space-y-2 text-sm text-gray-400">
                                <li>Track your real holdings.</li>
                                <li>Compare ROI with others on the Global Leaderboard.</li>
                                <li>Group assets into custom categories.</li>
                            </ul>
                        </div>
                        <div className="p-6 bg-zinc-900/50 border border-white/10 rounded-xl">
                            <h3 className="text-xl font-bold text-teal-400 mb-2">4. AI Copilot</h3>
                            <ul className="space-y-2 text-sm text-gray-400">
                                <li>Get instant analysis on your wealth distribution.</li>
                                <li>Powered by Google Gemini models.</li>
                                <li>Ask custom questions about your strategy.</li>
                            </ul>
                        </div>
                    </div>

                    <h2>🚀 Getting Started</h2>

                    <h3>Access the App</h3>
                    <ul>
                        <li>Sign in securely with your <strong>Google Account</strong>.</li>
                        <li>Use <strong>Guest Mode</strong> to explore without saving data.</li>
                    </ul>

                    <h3>First Steps</h3>
                    <ol>
                        <li><strong>Login</strong>: Use your Google Account.</li>
                        <li><strong>Explore</strong>: Go to "Mars Strategy" to see the backtest results.</li>
                        <li><strong>Settings</strong>: Customize your profile, nickname, and default landing page.</li>
                    </ol>
                </div>

                {/* Footer */}
                <div className="mt-20 pt-8 border-t border-white/10 text-center">
                    <p className="text-zinc-500 italic text-sm">
                        *Built with ❤️ by the Marffet AI Team.*
                    </p>
                </div>
            </div>
        </div>
    );
}
