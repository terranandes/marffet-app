import React from "react";
import { Transaction } from "../../../services/portfolioService";
import { useLanguage } from "@/lib/i18n/LanguageContext";

interface TransactionHistoryModalProps {
    isOpen: boolean;
    onClose: () => void;
    transactions: Transaction[];
    onAdd: () => void;
    onEdit: (tx: Transaction) => void;
    onDelete: (id: string) => void;
}

export function TransactionHistoryModal({
    isOpen,
    onClose,
    transactions,
    onAdd,
    onEdit,
    onDelete
}: TransactionHistoryModalProps) {
    const { t } = useLanguage();
    if (!isOpen) return null;

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
                    <h3 className="text-xl font-bold flex items-center gap-2">
                        📜 {t('Portfolio.History')}
                    </h3>
                    <button
                        onClick={onAdd}
                        className="bg-[var(--color-cta)]/20 border border-[var(--color-cta)] text-[var(--color-cta)] px-3 py-1.5 rounded text-sm hover:bg-[var(--color-cta)] hover:text-black transition cursor-pointer"
                    >
                        + Add
                    </button>
                </div>

                {transactions.length === 0 ? (
                    <p className="text-[var(--color-text-muted)] text-center py-8">
                        {t('Portfolio.NoTransactionsYet')}
                    </p>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm min-w-[500px]">
                            <thead>
                                <tr className="text-left text-[var(--color-text-muted)] text-xs uppercase border-b border-white/10">
                                    <th className="p-2">{t('Portfolio.Date')}</th>
                                    <th className="p-2">{t('Portfolio.Type')}</th>
                                    <th className="p-2 text-right">{t('Portfolio.Shares')}</th>
                                    <th className="p-2 text-right">{t('Portfolio.Price')}</th>
                                    <th className="p-2 text-right">{t('Portfolio.Total')}</th>
                                    <th className="p-2 text-center">{t('Portfolio.Actions')}</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {transactions.map((tx) => (
                                    <tr key={tx.id} className="hover:bg-white/5">
                                        <td className="p-2 font-mono text-xs">{tx.date}</td>
                                        <td className={`p-2 font-bold ${tx.type === 'buy' ? 'text-red-400' : 'text-green-400'}`}>
                                            {tx.type.toUpperCase()}
                                        </td>
                                        <td className="p-2 font-mono text-right">{tx.shares}</td>
                                        <td className="p-2 font-mono text-right">${tx.price}</td>
                                        <td className="p-2 font-mono text-right font-bold">
                                            ${(tx.shares * tx.price).toLocaleString()}
                                        </td>
                                        <td className="p-2 text-center">
                                            <button
                                                onClick={() => onEdit(tx)}
                                                className="text-[var(--color-cta)] hover:text-white hover:bg-[var(--color-cta)]/30 px-2 py-1 rounded transition-all duration-150 cursor-pointer hover:scale-110"
                                                title="Edit transaction"
                                            >
                                                ✏️
                                            </button>
                                            <button
                                                onClick={() => onDelete(tx.id)}
                                                className="text-red-400 hover:text-white hover:bg-red-500/30 px-2 py-1 rounded transition-all duration-150 cursor-pointer hover:scale-110"
                                                title="Delete transaction"
                                            >
                                                🗑
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
                <div className="mt-4 flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 border border-white/20 rounded hover:bg-white/10 transition cursor-pointer"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
}
