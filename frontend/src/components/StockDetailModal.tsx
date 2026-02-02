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


// Types
interface StockDetailModalProps {
    isOpen: boolean;
    onClose: () => void;
    stockId: string;
    stockName: string;
    dividends: Dividend[];
    loading: boolean;
}

export default function StockDetailModal({
    isOpen,
    onClose,
    stockId,
    stockName,
    dividends,
    loading
}: StockDetailModalProps) {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm" onClick={onClose}>
            <div
                className="bg-[var(--color-background)] border border-[var(--color-border)] rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden animate-in fade-in zoom-in duration-200"
                onClick={(e) => e.stopPropagation()}
            >

                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-[var(--color-border)] bg-zinc-900/50">
                    <div>
                        <h2 className="text-xl font-bold text-white flex items-center gap-2">
                            <span className="bg-blue-600 text-xs px-2 py-1 rounded text-white">{stockId}</span>
                            {stockName}
                        </h2>
                        <span className="text-xs text-zinc-500">Dividend Receipt History</span>
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

                {/* Content */}
                <div className="p-0 flex-1 overflow-auto bg-[var(--color-background)]">
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
            </div>
        </div>
    );
}
