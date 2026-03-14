import { useState, useEffect, useCallback, useMemo } from "react";
import useSWR from "swr";
import { PortfolioFactory, IPortfolioService, Group, Target, Dividend } from "../../../services/portfolioService";

interface PortfolioDataState {
    groups: Group[];
    selectedGroupId: string | null;
    targets: Target[];
    loading: boolean;
    groupStats: {
        marketValue: number;
        realized: number;
        unrealized: number;
        unrealizedPct: number;
    };
    dividendCash: { total_cash: number; dividend_count: number };
    syncing: boolean;
    isGuest: boolean;
    service: IPortfolioService | null;
}

export function usePortfolioData() {
    const [selectedGroupId, setSelectedGroupId] = useState<string | null>(null);
    const [isGuest, setIsGuest] = useState(false);
    const [service, setService] = useState<IPortfolioService | null>(null);
    const [syncing, setSyncing] = useState(false);

    const API_BASE = "";

    // Initialize Service
    useEffect(() => {
        const initService = async () => {
            const isGuestModeLocal = localStorage.getItem("marffet_guest_mode") === "true";
            if (isGuestModeLocal) {
                console.log("Guest Mode Active (LocalStorage Bypass)");
                setService(PortfolioFactory.getService(false));
                setIsGuest(true);
                return;
            }

            try {
                const res = await fetch(`${API_BASE}/api/portfolio/targets?group_id=auth_check`, { credentials: "include" });
                if (res.status === 401 || res.status === 403) {
                    console.log("Unauthorized, falling back to Guest Mode");
                    setService(PortfolioFactory.getService(false));
                    setIsGuest(true);
                } else {
                    setService(PortfolioFactory.getService(true));
                }
            } catch (e) {
                console.log("API Unreachable, using Guest Mode");
                setService(PortfolioFactory.getService(false));
                setIsGuest(true);
            }
        };
        initService();
    }, []);

    // SWR Fetchers wrapped around OOP Service
    const fetchGroupsWithService = useCallback(() => service ? service.getGroups() : Promise.resolve([]), [service]);
    const fetchTargetsWithService = useCallback(() => (service && selectedGroupId) ? service.getTargets(selectedGroupId) : Promise.resolve([]), [service, selectedGroupId]);
    const fetchDividendsWithService = useCallback(() => service ? service.getDividendStats() : Promise.resolve({ total_cash: 0, dividend_count: 0 }), [service]);

    // Setup SWR caching
    const { data: groups = [], mutate: mutateGroups } = useSWR<Group[]>(
        service ? "portfolio-groups" : null,
        fetchGroupsWithService,
        { keepPreviousData: true, fallbackData: [] }
    );

    const { data: targets = [], mutate: mutateTargets, isValidating: targetsLoading } = useSWR<Target[]>(
        (service && selectedGroupId) ? `portfolio-targets-${selectedGroupId}` : null,
        fetchTargetsWithService,
        { keepPreviousData: true, fallbackData: [] }
    );

    const { data: dividendCash = { total_cash: 0, dividend_count: 0 }, mutate: mutateDividends } = useSWR<{ total_cash: number; dividend_count: number }>(
        service ? "portfolio-dividends" : null,
        fetchDividendsWithService,
        { keepPreviousData: true, fallbackData: { total_cash: 0, dividend_count: 0 } }
    );

    // Initial group selection
    useEffect(() => {
        if (groups.length > 0 && !selectedGroupId) {
            setSelectedGroupId(groups[0].id);
        }
    }, [groups, selectedGroupId]);

    const loading = (!service && !isGuest) || (!targets && targetsLoading);

    // Stats: Computed dynamically based on targets instead of stored in state 
    // to ensure they reflect live updates when single targets are refreshed.
    const groupStats = useMemo(() => {
        let marketValue = 0;
        let realized = 0;
        let unrealized = 0;
        let totalCost = 0;

        targets.forEach((t) => {
            marketValue += t.summary?.market_value || 0;
            realized += t.summary?.realized_pnl || 0;
            unrealized += t.summary?.unrealized_pnl || 0;
            totalCost += (t.summary?.avg_cost || 0) * (t.summary?.total_shares || 0);
        });

        return {
            marketValue,
            realized,
            unrealized,
            unrealizedPct: totalCost > 0 ? (unrealized / totalCost) * 100 : 0,
        };
    }, [targets]);

    // Actions map directly to cache mutations
    const createGroup = async (name: string) => {
        if (!service || !name.trim()) return;
        if (await service.createGroup(name)) {
            mutateGroups();
            return true;
        }
        return false;
    };

    const deleteGroup = async (groupId: string) => {
        if (!service) return;
        if (await service.deleteGroup(groupId)) {
            if (selectedGroupId === groupId) setSelectedGroupId(null);
            mutateGroups();
            return true;
        }
        return false;
    };

    const addTarget = async (targetId: string, name: string) => {
        if (!service || !selectedGroupId || !targetId.trim()) return;
        if (await service.addTarget(selectedGroupId, targetId, name.trim() || "")) {
            mutateTargets();
            return true;
        }
        return false;
    };

    const deleteTarget = async (targetId: string) => {
        if (!service) return;
        if (await service.deleteTarget(targetId)) {
            mutateTargets();
            return true;
        }
        return false;
    };

    const syncDividends = async () => {
        if (!service) return;
        setSyncing(true);
        try {
            await service.syncDividends();
            await mutateTargets();
            await mutateDividends();
        } finally {
            setSyncing(false);
        }
    };


    // Helper to refresh only one target's summary (Performance)
    const refreshSingleTarget = async (targetId: string) => {
        if (!service) return;
        const target = targets.find(t => t.id === targetId);
        const currentPrice = target?.livePrice?.price;
        const newSummary = await service.getTargetSummary(targetId, currentPrice);

        if (newSummary) {
            mutateTargets(prev => {
                if (!prev) return prev;
                return prev.map(t =>
                    t.id === targetId ? { ...t, summary: newSummary } : t
                );
            }, false); // don't revalidate immediately
        }
    };

    return {
        groups,
        selectedGroupId,
        setSelectedGroupId,
        targets,
        loading,
        groupStats,
        dividendCash,
        syncing,
        isGuest,
        service,
        createGroup,
        deleteGroup,
        addTarget,
        deleteTarget,
        syncDividends,
        refreshSingleTarget,
        fetchTargets: mutateTargets // exposed for manual refresh
    };
}
