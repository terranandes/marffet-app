import React from "react";
import { Dividend } from "../../../services/portfolioService";
import { useLanguage } from "@/lib/i18n/LanguageContext";

interface DividendHistoryModalProps {
    data: { targetId: string; stockId: string; stockName: string } | null;
    onClose: () => void;
    dividends: Dividend[];
    loading: boolean;
}

export function DividendHistoryModal({
    data,
    onClose,
    dividends,
    loading
}: DividendHistoryModalProps) {
    const { t } = useLanguage();
    if (!data) return null;

    const formatCurrency = (val: number) => {
        return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(val);
    };

    return (
        <div
            className="fixed inset-0 bg-black/80 flex items-center justify-center z-50"
            onClick={onClose}
        >
            <div
                className="bg-[#1a1a2e] p-6 rounded-xl border border-white/20 w-full max-w-2xl max-h-[80vh] overflow-auto"
                onClick={(e) => e.stopPropagation()}
            >
                <div className="flex justify-between items-center mb-4">
                    <div>
                        <h3 className="text-xl font-bold flex items-center gap-2">
                            💰 Dividend History
                            <span className="text-sm bg-black/30 px-2 py-1 rounded text-[var(--color-text-muted)] font-normal">
                                {data.stockName} ({data.stockId})
                            </span>
                        </h3>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-[var(--color-text-muted)] hover:text-white text-2xl leading-none"
                    >
                        &times;
                    </button>
                </div>

                {loading ? (
                    <div className="text-center py-12">
                        <div className="animate-spin text-4xl mb-2">⏳</div>
                        <div className="text-[var(--color-text-muted)]">{t('Portfolio.LoadingDividends')}</div>
                    </div>
                ) : dividends.length === 0 ? (
                    <div className="text-center py-8 bg-black/20 rounded-lg">
                        <div className="text-4xl mb-2">📭</div>
                        <p className="text-[var(--color-text-muted)]">{t('Portfolio.NoDividends')}</p>
                        <p className="text-xs text-[var(--color-text-muted)] mt-1 opacity-70">
                            {/* Keep standard string for now, or add "Try clicking sync" to translation file */}
                            (Try clicking "Sync Dividends" at the top to fetch latest data)
                        </p>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="text-left text-[var(--color-text-muted)] text-xs uppercase border-b border-white/10">
                                    <th className="p-3">{t('Portfolio.ExDate')}</th>
                                    <th className="p-3">{t('Portfolio.PaymentDate')}</th>
                                    <th className="p-3 text-right">{t('Portfolio.CashDiv')}</th>
                                    <th className="p-3 text-right">{t('Portfolio.StockDiv')}</th>
                                    <th className="p-3 text-right">{t('Portfolio.HeldShares')}</th>
                                    <th className="p-3 text-right">{t('Portfolio.TotalCash')}</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {dividends.map((div, idx) => (
                                    <tr key={idx} className="hover:bg-white/5 transition">
                                        <td className="p-3 font-mono text-xs">{div.date}</td>
                                        <td className="p-3 font-mono text-xs text-[var(--color-text-muted)]">
                                            {div.payment_date || "-"}
                                        </td>
                                        <td className="p-3 text-right font-mono text-yellow-500">
                                            {div.cash_dividend > 0 ? `$${div.cash_dividend}` : "-"}
                                        </td>
                                        <td className="p-3 text-right font-mono text-blue-400">
                                            {div.stock_dividend > 0 ? `${div.stock_dividend}` : "-"}
                                        </td>
                                        <td className="p-3 text-right font-mono text-gray-400">
                                            {Math.floor(div.held_shares)}
                                        </td>
                                        <td className="p-3 text-right font-mono font-bold text-[var(--color-success)]">
                                            ${formatCurrency(div.amount)}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                            <tfoot className="border-t border-white/20 bg-white/5">
                                <tr>
                                    <td colSpan={5} className="p-3 text-right font-bold uppercase text-xs tracking-wider">
                                        Total Receipt
                                    </td>
                                    <td className="p-3 text-right font-mono font-bold text-[var(--color-warning)] text-lg">
                                        ${formatCurrency(dividends.reduce((acc, curr) => acc + curr.amount, 0))}
                                    </td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                )}

                <div className="mt-6 flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-6 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition font-medium"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
}
