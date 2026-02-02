import { useState } from "react";
import { Dividend } from "../services/portfolioService";

// Types
interface StockDetailModalProps {
    isOpen: boolean;
    onClose: () => void;
    stockId: string;
    stockName: string;
    dividends: Dividend[];
    loading: boolean;
}

type Tab = "history" | "compound_interest";
type CompoundSubTab = "single" | "comparison";

export default function StockDetailModal({
    isOpen,
    onClose,
    stockId,
    stockName,
    dividends,
    loading
}: StockDetailModalProps) {
    const [activeTab, setActiveTab] = useState<Tab>("history");
    const [compoundSubTab, setCompoundSubTab] = useState<CompoundSubTab>("single");

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm" onClick={onClose}>
            <div
                className="bg-[var(--color-background)] border border-[var(--color-border)] rounded-xl shadow-2xl w-full max-w-5xl h-[90vh] flex flex-col overflow-hidden animate-in fade-in zoom-in duration-200"
                onClick={(e) => e.stopPropagation()}
            >

                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-[var(--color-border)] bg-zinc-900/50">
                    <div>
                        <h2 className="text-xl font-bold text-white flex items-center gap-2">
                            <span className="bg-blue-600 text-xs px-2 py-1 rounded text-white">{stockId}</span>
                            {stockName}
                        </h2>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-zinc-700 rounded-full transition-colors text-zinc-400 hover:text-white"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* Top Level Tabs */}
                <div className="flex border-b border-[var(--color-border)] bg-zinc-900/30">
                    <button
                        onClick={() => setActiveTab("history")}
                        className={`flex-1 py-3 text-sm font-medium transition-colors border-b-2 ${activeTab === "history"
                                ? "border-blue-500 text-blue-400 bg-blue-500/10"
                                : "border-transparent text-zinc-400 hover:text-white hover:bg-zinc-700/50"
                            }`}
                    >
                        💰 My Dividends
                    </button>
                    <button
                        onClick={() => setActiveTab("compound_interest")}
                        className={`flex-1 py-3 text-sm font-medium transition-colors border-b-2 ${activeTab === "compound_interest"
                                ? "border-amber-500 text-amber-400 bg-amber-500/10"
                                : "border-transparent text-zinc-400 hover:text-white hover:bg-zinc-700/50"
                            }`}
                    >
                        📈 Compound Interest
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-auto bg-[var(--color-background)] relative flex flex-col">

                    {/* Tab 1: History */}
                    {activeTab === "history" && (
                        <div className="p-0 flex-1 overflow-auto">
                            {loading ? (
                                <div className="flex justify-center py-20">
                                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
                                </div>
                            ) : dividends.length === 0 ? (
                                <div className="text-center py-20 text-zinc-500">
                                    No dividend history available.
                                </div>
                            ) : (
                                <div className="overflow-x-auto">
                                    <table className="w-full text-sm text-left">
                                        <thead className="bg-zinc-900 text-zinc-400 uppercase text-xs sticky top-0">
                                            <tr>
                                                <th className="px-4 py-3">Ex-Date</th>
                                                <th className="px-4 py-3 text-right">Shares</th>
                                                <th className="px-4 py-3 text-right">$/Share</th>
                                                <th className="px-4 py-3 text-right">Total Cash</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-[var(--color-border)]">
                                            {dividends.map((div) => (
                                                <tr key={div.id} className="hover:bg-zinc-800/50 transition-colors">
                                                    <td className="px-4 py-3 font-mono text-zinc-300">{div.ex_date}</td>
                                                    <td className="px-4 py-3 font-mono text-zinc-300 text-right">{div.shares_held}</td>
                                                    <td className="px-4 py-3 font-mono text-zinc-500 text-right">${div.amount_per_share?.toFixed(4)}</td>
                                                    <td className="px-4 py-3 font-mono text-[var(--color-warning)] font-bold text-right">
                                                        ${div.total_cash?.toLocaleString()}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                        <tfoot className="bg-zinc-900 sticky bottom-0 border-t border-[var(--color-border)]">
                                            <tr>
                                                <td colSpan={3} className="px-4 py-3 text-right font-bold text-zinc-400">Total Received:</td>
                                                <td className="px-4 py-3 text-right font-bold text-[var(--color-warning)]">
                                                    ${dividends.reduce((sum, d) => sum + (d.total_cash || 0), 0).toLocaleString()}
                                                </td>
                                            </tr>
                                        </tfoot>
                                    </table>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Tab 2: Compound Interest (Nested) */}
                    {activeTab === "compound_interest" && (
                        <div className="flex flex-col h-full w-full">
                            {/* Sub Navigation */}
                            <div className="flex justify-center p-2 bg-zinc-900">
                                <div className="flex bg-zinc-800 p-1 rounded-lg">
                                    <button
                                        onClick={() => setCompoundSubTab("single")}
                                        className={`px-6 py-1.5 text-xs font-medium rounded-md transition-all ${compoundSubTab === "single"
                                                ? "bg-amber-500 text-black shadow-lg"
                                                : "text-zinc-400 hover:text-white hover:bg-zinc-700"
                                            }`}
                                    >
                                        Single
                                    </button>
                                    <button
                                        onClick={() => setCompoundSubTab("comparison")}
                                        className={`px-6 py-1.5 text-xs font-medium rounded-md transition-all ${compoundSubTab === "comparison"
                                                ? "bg-purple-500 text-white shadow-lg"
                                                : "text-zinc-400 hover:text-white hover:bg-zinc-700"
                                            }`}
                                    >
                                        Comparison
                                    </button>
                                </div>
                            </div>

                            {/* Iframe Content */}
                            <div className="flex-1 bg-white relative">
                                {compoundSubTab === "single" ? (
                                    <iframe
                                        src={`https://moneycome.in/tool/compound_interest?stkCode=${stockId}`}
                                        className="w-full h-full border-0 absolute inset-0"
                                        title="MoneyCome Compound Interest Single"
                                        sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
                                    />
                                ) : (
                                    <iframe
                                        src={`https://moneycome.in/tool/compound_interest_comparison?stkCodes=${stockId},0050&startYear=2006&endYear=2026`}
                                        className="w-full h-full border-0 absolute inset-0"
                                        title="MoneyCome Compound Interest Comparison"
                                        sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
                                    />
                                )}
                            </div>
                        </div>
                    )}

                </div>
            </div>
        </div>
    );
}
