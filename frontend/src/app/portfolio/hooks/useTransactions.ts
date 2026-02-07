import { useState } from "react";
import { IPortfolioService, Transaction, Dividend } from "../../../services/portfolioService";

interface NewTransaction {
    type: "buy" | "sell";
    shares: number;
    price: number;
    date: string;
}

export function useTransactions(service: IPortfolioService | null, onRefreshTarget: (id: string) => void) {
    // Transaction Form State
    const [showTxForm, setShowTxForm] = useState<string | null>(null);
    const [editingTxId, setEditingTxId] = useState<string | null>(null);
    const [newTx, setNewTx] = useState<NewTransaction>({
        type: "buy",
        shares: 0,
        price: 0,
        date: new Date().toISOString().split("T")[0],
    });

    // Transaction History State
    const [showTxHistory, setShowTxHistory] = useState<string | null>(null);
    const [txHistory, setTxHistory] = useState<Transaction[]>([]);

    // Dividend History State
    const [showDivHistory, setShowDivHistory] = useState<{ targetId: string; stockId: string; stockName: string } | null>(null);
    const [divHistory, setDivHistory] = useState<Dividend[]>([]);
    const [historyLoading, setHistoryLoading] = useState(false);

    // Actions
    const fetchTxHistory = async (targetId: string) => {
        if (!service) return;
        const data = await service.getTransactions(targetId);
        setTxHistory(data);
        setShowTxHistory(targetId);
    };

    const saveTransaction = async (targetId: string) => {
        if (!service) return;
        const txData = editingTxId
            ? { id: editingTxId, ...newTx }
            : { target_id: targetId, ...newTx };

        if (await service.saveTransaction(txData)) {
            setShowTxForm(null);
            setEditingTxId(null);
            setNewTx({ type: "buy", shares: 0, price: 0, date: new Date().toISOString().split("T")[0] });

            // Refresh history if open
            if (showTxHistory) fetchTxHistory(showTxHistory);

            // Refresh target summary
            onRefreshTarget(targetId);
            return true;
        }
        return false;
    };

    const deleteTransaction = async (txId: string) => {
        if (!service || !confirm("Delete transaction?")) return;
        if (await service.deleteTransaction(txId)) {
            if (showTxHistory) {
                fetchTxHistory(showTxHistory);
                onRefreshTarget(showTxHistory);
            }
            return true;
        }
        return false;
    };

    const fetchDivHistory = async (targetId: string, stockId: string, stockName: string) => {
        if (!service) return;
        setHistoryLoading(true);
        try {
            const data = await service.getDividends(targetId);
            setDivHistory(data);
            setShowDivHistory({ targetId, stockId, stockName });
        } finally {
            setHistoryLoading(false);
        }
    };

    return {
        showTxForm,
        setShowTxForm,
        editingTxId,
        setEditingTxId,
        newTx,
        setNewTx,
        showTxHistory,
        setShowTxHistory,
        txHistory,
        fetchTxHistory,
        saveTransaction,
        deleteTransaction,
        // Dividend Logic
        showDivHistory,
        setShowDivHistory,
        divHistory,
        fetchDivHistory,
        historyLoading
    };
}
