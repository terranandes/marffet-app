"use client";

import { usePortfolioData } from "./hooks/usePortfolioData";
import { useTransactions } from "./hooks/useTransactions";
import { PortfolioHeader } from "./components/PortfolioHeader";
import { GroupSelector } from "./components/GroupSelector";
import { StatsSummary } from "./components/StatsSummary";
import { TargetList } from "./components/TargetList";
import { TargetCardList } from "./components/TargetCardList";
import { TransactionFormModal } from "./components/TransactionFormModal";
import { TransactionHistoryModal } from "./components/TransactionHistoryModal";
import { DividendHistoryModal } from "./components/DividendHistoryModal";
import { useState } from "react";

export default function PortfolioPage() {
    const {
        groups, selectedGroupId, setSelectedGroupId,
        targets, loading, groupStats, dividendCash,
        syncing, isGuest, service,
        createGroup, deleteGroup, addTarget, deleteTarget,
        syncDividends, refreshSingleTarget
    } = usePortfolioData();

    const {
        showTxForm, setShowTxForm,
        editingTxId, setEditingTxId,
        newTx, setNewTx,
        showTxHistory, setShowTxHistory,
        txHistory, fetchTxHistory,
        saveTransaction, deleteTransaction,
        showDivHistory, setShowDivHistory,
        divHistory, fetchDivHistory, historyLoading
    } = useTransactions(service, refreshSingleTarget);

    const [showAddGroup, setShowAddGroup] = useState(false);

    return (
        <div className="max-w-6xl mx-auto space-y-6">
            <PortfolioHeader
                isGuest={isGuest}
                dividendCash={dividendCash}
                syncing={syncing}
                onSync={syncDividends}
                showAddGroup={showAddGroup}
                onToggleAddGroup={() => setShowAddGroup(!showAddGroup)}
            />

            <GroupSelector
                groups={groups}
                selectedGroupId={selectedGroupId}
                onSelect={setSelectedGroupId}
                onDelete={deleteGroup}
                showAddForm={showAddGroup}
                onCreate={(name) => { createGroup(name); setShowAddGroup(false); }}
                loading={loading}
            />

            {selectedGroupId && (
                <div className="glass-card p-5 rounded-xl">
                    <StatsSummary stats={groupStats} />

                    <TargetList
                        targets={targets}
                        onAddTransaction={(id) => {
                            setShowTxForm(id);
                            setEditingTxId(null);
                        }}
                        onShowHistory={fetchTxHistory}
                        onDelete={deleteTarget}
                        onShowDividends={fetchDivHistory}
                        onAddTarget={addTarget}
                    />

                    <TargetCardList
                        targets={targets}
                        onAddTransaction={(id) => {
                            setShowTxForm(id);
                            setEditingTxId(null);
                        }}
                        onShowHistory={fetchTxHistory}
                        onDelete={deleteTarget}
                        onShowDividends={fetchDivHistory}
                    />
                </div>
            )}

            {!selectedGroupId && !loading && groups.length === 0 && (
                <div className="glass-card p-8 text-center">
                    <p className="text-6xl mb-4">📊</p>
                    <h2 className="text-2xl font-bold mb-2">Start Your Portfolio</h2>
                    <p className="text-[var(--color-text-muted)]">
                        Create a group above to start tracking your investments.
                    </p>
                </div>
            )}

            <TransactionFormModal
                isOpen={!!showTxForm}
                onClose={() => setShowTxForm(null)}
                isEditing={!!editingTxId}
                txData={newTx}
                onChange={setNewTx}
                onSave={() => showTxForm && saveTransaction(showTxForm)}
            />

            <TransactionHistoryModal
                isOpen={!!showTxHistory}
                onClose={() => setShowTxHistory(null)}
                transactions={txHistory}
                onAdd={() => {
                    if (showTxHistory) {
                        setShowTxForm(showTxHistory);
                        setEditingTxId(null);
                    }
                }}
                onEdit={(tx) => {
                    setEditingTxId(tx.id);
                    setNewTx({
                        type: tx.type,
                        shares: tx.shares,
                        price: tx.price,
                        date: tx.date
                    });
                    setShowTxForm(tx.target_id);
                }}
                onDelete={deleteTransaction}
            />

            <DividendHistoryModal
                data={showDivHistory}
                onClose={() => setShowDivHistory(null)}
                dividends={divHistory}
                loading={historyLoading}
            />
        </div>
    );
}
