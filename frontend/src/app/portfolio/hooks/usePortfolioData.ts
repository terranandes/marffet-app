import { useState, useRef, useEffect, useCallback } from "react";
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
    const [groups, setGroups] = useState<Group[]>([]);
    const [selectedGroupId, setSelectedGroupId] = useState<string | null>(null);
    const [targets, setTargets] = useState<Target[]>([]);
    const [loading, setLoading] = useState(true);
    const [isGuest, setIsGuest] = useState(false);
    const [service, setService] = useState<IPortfolioService | null>(null);

    // Stats
    const [groupStats, setGroupStats] = useState({
        marketValue: 0,
        realized: 0,
        unrealized: 0,
        unrealizedPct: 0,
    });

    const [dividendCash, setDividendCash] = useState({ total_cash: 0, dividend_count: 0 });
    const [syncing, setSyncing] = useState(false);

    // Request tracking
    const fetchRequestIdRef = useRef(0);
    const API_BASE = "";

    // Initialize Service
    useEffect(() => {
        const initService = async () => {
            try {
                const res = await fetch(`${API_BASE}/api/portfolio/targets?group_id=auth_check`, { credentials: "include" });
                if (res.status === 401 || res.status === 403) {
                    console.log("Unauthorized, using Guest Mode");
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

    const fetchGroups = useCallback(async () => {
        if (!service) return;
        setLoading(true);
        const data = await service.getGroups();
        setGroups(data);
        if (data.length > 0 && !selectedGroupId) {
            setSelectedGroupId(data[0].id);
        }
        setLoading(false);
    }, [service, selectedGroupId]);

    const fetchTargets = useCallback(async () => {
        if (!service || !selectedGroupId) return;
        const requestId = ++fetchRequestIdRef.current;
        setLoading(true);
        const data = await service.getTargets(selectedGroupId);

        if (requestId !== fetchRequestIdRef.current) {
            console.log(`[Portfolio] Discarding stale response for request ${requestId}`);
            return;
        }

        setTargets(data);
        setLoading(false);

        let marketValue = 0;
        let realized = 0;
        let unrealized = 0;
        let totalCost = 0;

        data.forEach((t) => {
            marketValue += t.summary?.market_value || 0;
            realized += t.summary?.realized_pnl || 0;
            unrealized += t.summary?.unrealized_pnl || 0;
            totalCost += (t.summary?.avg_cost || 0) * (t.summary?.total_shares || 0);
        });

        setGroupStats({
            marketValue,
            realized,
            unrealized,
            unrealizedPct: totalCost > 0 ? (unrealized / totalCost) * 100 : 0,
        });
    }, [service, selectedGroupId]);

    const fetchDividends = useCallback(async () => {
        if (!service) return;
        const data = await service.getDividendStats();
        setDividendCash(data);
    }, [service]);

    useEffect(() => {
        if (service) {
            fetchGroups();
            fetchDividends();
        }
    }, [service, fetchGroups, fetchDividends]);

    useEffect(() => {
        if (service && selectedGroupId) {
            fetchTargets();
        }
    }, [service, selectedGroupId, fetchTargets]);

    // Actions
    const createGroup = async (name: string) => {
        if (!service || !name.trim()) return;
        if (await service.createGroup(name)) {
            fetchGroups();
            return true;
        }
        return false;
    };

    const deleteGroup = async (groupId: string) => {
        if (!service) return;
        if (await service.deleteGroup(groupId)) {
            if (selectedGroupId === groupId) setSelectedGroupId(null);
            fetchGroups();
            return true;
        }
        return false;
    };

    const addTarget = async (targetId: string, name: string) => {
        if (!service || !selectedGroupId || !targetId.trim()) return;
        if (await service.addTarget(selectedGroupId, targetId, name.trim() || "")) {
            fetchTargets();
            return true;
        }
        return false;
    };

    const deleteTarget = async (targetId: string) => {
        if (!service) return;
        if (await service.deleteTarget(targetId)) {
            fetchTargets();
            return true;
        }
        return false;
    };

    const syncDividends = async () => {
        if (!service) return;
        setSyncing(true);
        await service.syncDividends();
        await fetchTargets();
        fetchDividends();
        setSyncing(false);
    };

    // Helper to refresh only one target's summary (Performance)
    const refreshSingleTarget = async (targetId: string) => {
        if (!service) return;
        const target = targets.find(t => t.id === targetId);
        const currentPrice = target?.livePrice?.price;
        const newSummary = await service.getTargetSummary(targetId, currentPrice);

        if (newSummary) {
            setTargets(prev => prev.map(t =>
                t.id === targetId ? { ...t, summary: newSummary } : t
            ));
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
        fetchTargets // exposed for manual refresh
    };
}
