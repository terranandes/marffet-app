import React, { useState } from "react";
import { Group } from "../../../services/portfolioService";
import { useLanguage } from "@/lib/i18n/LanguageContext";

interface GroupSelectorProps {
    groups: Group[];
    selectedGroupId: string | null;
    onSelect: (id: string) => void;
    onDelete: (id: string) => void;
    showAddForm: boolean;
    onCreate: (name: string) => void;
    loading: boolean;
}

export function GroupSelector({
    groups,
    selectedGroupId,
    onSelect,
    onDelete,
    showAddForm,
    onCreate,
    loading
}: GroupSelectorProps) {
    const { t } = useLanguage();
    const [newGroupName, setNewGroupName] = useState("");

    const handleCreate = () => {
        onCreate(newGroupName);
        setNewGroupName("");
    };

    return (
        <div className="glass-card px-5 pb-5 rounded-xl -mt-4 pt-0 border-t-0 rounded-t-none">
            {/* Add Group Form */}
            {showAddForm && (
                <div className="mb-4 p-3 bg-black/30 rounded-lg flex gap-2">
                    <input
                        type="text"
                        value={newGroupName}
                        onChange={(e) => setNewGroupName(e.target.value)}
                        placeholder={t('Portfolio.GroupNamePlaceholder') || "Group name..."}
                        className="bg-black/50 border border-[var(--color-border)] rounded px-3 py-2 text-sm flex-1 focus:border-[var(--color-cta)] outline-none"
                        onKeyDown={(e) => e.key === "Enter" && handleCreate()}
                    />
                    <button
                        onClick={handleCreate}
                        className="bg-[var(--color-cta)] text-black px-4 py-2 rounded text-sm font-bold cursor-pointer"
                    >
                        {t('Portfolio.CreateBtn') || "Create"}
                    </button>
                </div>
            )}

            {/* Group Tabs */}
            <div className="flex gap-2 overflow-x-auto pb-2 flex-nowrap lg:flex-wrap no-scrollbar">
                {groups.map((group) => (
                    <button
                        key={group.id}
                        onClick={() => onSelect(group.id)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium border transition cursor-pointer whitespace-nowrap shrink-0 ${selectedGroupId === group.id
                            ? "bg-[var(--color-cta)] text-black border-[var(--color-cta)]"
                            : "border-[var(--color-border)] hover:border-[var(--color-cta)]"
                            }`}
                    >
                        {group.name}
                        <span
                            onClick={(e) => {
                                e.stopPropagation();
                                onDelete(group.id);
                            }}
                            className="ml-2 text-[var(--color-danger)] hover:text-red-300 cursor-pointer"
                        >
                            ×
                        </span>
                    </button>
                ))}
                {groups.length === 0 && !loading && (
                    <span className="text-[var(--color-text-muted)] text-sm">
                        {t('Portfolio.NoGroupsYet') || "No groups yet. Create one to start tracking!"}
                    </span>
                )}
            </div>
        </div>
    );
}
