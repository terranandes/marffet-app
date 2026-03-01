import React from "react";

interface TransactionFormModalProps {
    isOpen: boolean;
    onClose: () => void;
    isEditing: boolean;
    txData: {
        type: "buy" | "sell";
        shares: number;
        price: number;
        date: string;
    };
    onChange: (data: any) => void;
    onSave: () => void;
}

export function TransactionFormModal({
    isOpen,
    onClose,
    isEditing,
    txData,
    onChange,
    onSave
}: TransactionFormModalProps) {
    if (!isOpen) return null;

    return (
        <div
            className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-[60]"
            onClick={onClose}
        >
            <div
                className="bg-black/60 backdrop-blur-2xl p-6 rounded-2xl border border-white/10 w-full max-w-md shadow-2xl"
                onClick={(e) => e.stopPropagation()}
            >
                <h3 className="text-xl font-bold mb-6 flex items-center gap-2 text-white">
                    <span className="text-[var(--color-cta)]">{isEditing ? "✏️" : "+"}</span>
                    {isEditing ? "Edit Transaction" : "New Transaction"}
                </h3>

                <div className="space-y-4">
                    {/* Type Selector */}
                    <div className="flex gap-2 p-1 bg-black/40 rounded-lg">
                        <button
                            onClick={() => onChange({ ...txData, type: "buy" })}
                            className={`flex-1 py-2 rounded-md text-sm font-bold transition ${txData.type === "buy"
                                ? "bg-red-500/20 text-red-500 border border-red-500/50"
                                : "text-[var(--color-text-muted)] hover:text-white"
                                }`}
                        >
                            BUY
                        </button>
                        <button
                            onClick={() => onChange({ ...txData, type: "sell" })}
                            className={`flex-1 py-2 rounded-md text-sm font-bold transition ${txData.type === "sell"
                                ? "bg-green-500/20 text-green-500 border border-green-500/50"
                                : "text-[var(--color-text-muted)] hover:text-white"
                                }`}
                        >
                            SELL
                        </button>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider block mb-1">
                                Shares
                            </label>
                            <input
                                type="number"
                                value={txData.shares || ""}
                                onChange={(e) => onChange({ ...txData, shares: parseFloat(e.target.value) })}
                                className="w-full bg-black/50 border border-[var(--color-border)] rounded px-3 py-2 focus:border-[var(--color-cta)] outline-none font-mono text-lg"
                                placeholder="0"
                            />
                        </div>
                        <div>
                            <label className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider block mb-1">
                                Date
                            </label>
                            <input
                                type="date"
                                value={txData.date}
                                onChange={(e) => onChange({ ...txData, date: e.target.value })}
                                style={{ colorScheme: "dark" }}
                                className="w-full bg-black/50 border border-[var(--color-border)] rounded px-3 py-2 text-white focus:border-[var(--color-cta)] outline-none text-sm h-[40px]"
                            />
                        </div>
                    </div>

                    <div>
                        <label className="text-xs text-[var(--color-text-muted)] uppercase tracking-wider block mb-1">
                            Price per Share
                        </label>
                        <div className="relative">
                            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-muted)]">$</span>
                            <input
                                type="number"
                                value={txData.price || ""}
                                onChange={(e) => onChange({ ...txData, price: parseFloat(e.target.value) })}
                                className="w-full bg-black/50 border border-[var(--color-border)] rounded pl-6 pr-3 py-2 focus:border-[var(--color-cta)] outline-none font-mono text-lg"
                                placeholder="0.00"
                            />
                        </div>
                    </div>

                    <div className="pt-4 flex justify-end gap-3">
                        <button
                            onClick={onClose}
                            className="px-4 py-2 text-[var(--color-text-muted)] hover:text-white transition"
                        >
                            Cancel
                        </button>
                        <button
                            onClick={onSave}
                            className="bg-[var(--color-cta)] text-black px-6 py-2 rounded font-bold hover:bg-white transition"
                        >
                            Save
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
