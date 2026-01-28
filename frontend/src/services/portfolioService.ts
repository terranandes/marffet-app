import { v4 as uuidv4 } from 'uuid';

// Types (Mirrors backend Types)
export interface Group {
    id: string;
    name: string;
}

export interface Target {
    id: string;
    group_id: string;
    stock_id: string;
    stock_name: string;
    summary?: {
        total_shares: number;
        avg_cost: number;
        market_value: number;
        realized_pnl: number;
        unrealized_pnl: number;
        unrealized_pnl_pct: number;
        total_dividend_cash: number;
    };
    livePrice?: {
        price: number;
        change: number;
        change_pct: number;
    };
}

export interface Transaction {
    id: string;
    target_id: string;
    type: "buy" | "sell";
    shares: number;
    price: number;
    date: string;
    fee?: number;
}

export interface Dividend {
    id: string;
    target_id: string;
    ex_date: string;
    shares_held: number;
    amount_per_share: number;
    total_cash: number;
}

// Interface
export interface IPortfolioService {
    isGuest: boolean;
    getGroups(): Promise<Group[]>;
    createGroup(name: string): Promise<Group | null>;
    deleteGroup(id: string): Promise<boolean>;

    getTargets(groupId: string): Promise<Target[]>;
    addTarget(groupId: string, stockId: string, name: string): Promise<Target | null>;
    deleteTarget(id: string): Promise<boolean>;

    getTransactions(targetId: string): Promise<Transaction[]>;
    saveTransaction(t: Partial<Transaction> & { target_id?: string }): Promise<boolean>;
    deleteTransaction(id: string): Promise<boolean>;

    getDividends(targetId: string): Promise<Dividend[]>;
    getDividendStats(): Promise<{ total_cash: number; dividend_count: number }>;
    syncDividends(): Promise<boolean>;

    // New granular update method
    getTargetSummary(targetId: string, currentPrice?: number): Promise<any>;
}

const API_BASE = "";

// Price cache with TTL
interface PriceCache {
    data: Record<string, { price: number; change: number; change_pct: number }>;
    timestamp: number;
}
let priceCache: PriceCache | null = null;
const PRICE_CACHE_TTL = 5 * 60 * 1000; // 5 minutes

// 1. API Implementation (Registered User)
class ApiPortfolioService implements IPortfolioService {
    isGuest = false;

    async getGroups(): Promise<Group[]> {
        try {
            const res = await fetch(`${API_BASE}/api/portfolio/groups`, { credentials: "include" });
            if (res.ok) return await res.json();
        } catch { }
        return [];
    }

    async createGroup(name: string): Promise<Group | null> {
        try {
            const res = await fetch(`${API_BASE}/api/portfolio/groups`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ name }),
            });
            if (res.ok) return await res.json();
        } catch { }
        return null;
    }

    async deleteGroup(id: string): Promise<boolean> {
        try {
            const res = await fetch(`${API_BASE}/api/portfolio/groups/${id}`, {
                method: "DELETE",
                credentials: "include"
            });
            return res.ok;
        } catch { return false; }
    }

    // Explicitly fetch summary for one target (updates main view without full reload)
    async getTargetSummary(targetId: string, currentPrice?: number): Promise<any> {
        try {
            const url = currentPrice
                ? `${API_BASE}/api/portfolio/targets/${targetId}/summary?current_price=${currentPrice}`
                : `${API_BASE}/api/portfolio/targets/${targetId}/summary`;

            const res = await fetch(url, { credentials: "include" });
            if (res.ok) return await res.json();
        } catch { }
        return null;
    }

    async getTargets(groupId: string): Promise<Target[]> {
        try {
            const res = await fetch(`${API_BASE}/api/portfolio/groups/${groupId}/targets`, { credentials: "include" });
            if (!res.ok) return [];

            const targets: Target[] = await res.json();
            if (targets.length === 0) return [];

            // Use cached prices if still valid
            const now = Date.now();
            const stockIds = targets.map(t => t.stock_id).join(',');
            let livePrices: Record<string, { price: number; change: number; change_pct: number }> = {};

            if (priceCache && (now - priceCache.timestamp) < PRICE_CACHE_TTL) {
                // Use cache
                livePrices = priceCache.data;
                console.log('[Portfolio] Using cached prices');
            } else if (stockIds) {
                // Fetch fresh prices
                try {
                    const pRes = await fetch(`${API_BASE}/api/portfolio/prices?stock_ids=${stockIds}`, { credentials: "include" });
                    if (pRes.ok) {
                        livePrices = await pRes.json();
                        priceCache = { data: livePrices, timestamp: now };
                        console.log('[Portfolio] Fetched fresh prices');
                    }
                } catch { }
            }

            // Fetch summaries in PARALLEL (not sequential!)
            await Promise.all(targets.map(async (t) => {
                t.livePrice = livePrices[t.stock_id] || null;
                const price = t.livePrice?.price;
                const url = price
                    ? `${API_BASE}/api/portfolio/targets/${t.id}/summary?current_price=${price}`
                    : `${API_BASE}/api/portfolio/targets/${t.id}/summary`;

                try {
                    const sRes = await fetch(url, { credentials: "include" });
                    if (sRes.ok) t.summary = await sRes.json();
                } catch { }
            }));

            return targets;
        } catch { return []; }
    }

    async addTarget(groupId: string, stockId: string, name: string): Promise<Target | null> {
        try {
            const res = await fetch(`${API_BASE}/api/portfolio/targets`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({
                    group_id: groupId,
                    stock_id: stockId,
                    stock_name: name || null,
                }),
            });
            if (res.ok) return await res.json(); // Actually returns {status, id...} or Target? Check BE.
            // BE returns {id: ..., stock_id...} usually.
            // Let's assume generic success here.
            return null; // Trigger refresh
        } catch { return null; }
    }

    async deleteTarget(id: string): Promise<boolean> {
        try {
            const res = await fetch(`${API_BASE}/api/portfolio/targets/${id}`, {
                method: "DELETE",
                credentials: "include"
            });
            return res.ok;
        } catch { return false; }
    }

    async getTransactions(targetId: string): Promise<Transaction[]> {
        try {
            const res = await fetch(`${API_BASE}/api/portfolio/targets/${targetId}/transactions`, { credentials: "include" });
            if (res.ok) return await res.json();
        } catch { }
        return [];
    }

    async saveTransaction(t: Partial<Transaction> & { target_id?: string }): Promise<boolean> {
        try {
            const isEdit = !!t.id;
            const url = isEdit
                ? `${API_BASE}/api/portfolio/transactions/${t.id}`
                : `${API_BASE}/api/portfolio/targets/${t.target_id}/transactions`;
            const method = isEdit ? "PUT" : "POST";

            const res = await fetch(url, {
                method,
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify(t),
            });
            return res.ok;
        } catch { return false; }
    }

    async deleteTransaction(id: string): Promise<boolean> {
        try {
            const res = await fetch(`${API_BASE}/api/portfolio/transactions/${id}`, {
                method: "DELETE",
                credentials: "include"
            });
            return res.ok;
        } catch { return false; }
    }

    async getDividends(targetId: string): Promise<Dividend[]> {
        try {
            const res = await fetch(`${API_BASE}/api/portfolio/targets/${targetId}/dividends`, { credentials: "include" });
            if (res.ok) return await res.json();
        } catch { }
        return [];
    }

    async getDividendStats(): Promise<{ total_cash: number; dividend_count: number }> {
        try {
            const res = await fetch(`${API_BASE}/api/portfolio/dividends/total`, { credentials: "include" });
            if (res.ok) return await res.json();
        } catch { }
        return { total_cash: 0, dividend_count: 0 };
    }

    async syncDividends(): Promise<boolean> {
        try {
            const res = await fetch(`${API_BASE}/api/portfolio/dividends/sync`, {
                method: "POST",
                credentials: "include"
            });
            return res.ok;
        } catch { return false; }
    }
}

// 2. Guest Implementation (LocalStorage)
const STORAGE_KEY = "martian_guest_data";

interface GuestData {
    groups: Group[];
    targets: Target[];
    transactions: Transaction[];
}

class GuestPortfolioService implements IPortfolioService {
    isGuest = true;

    private loadData(): GuestData {
        if (typeof window === "undefined") return { groups: [], targets: [], transactions: [] };
        const raw = localStorage.getItem(STORAGE_KEY);
        if (!raw) return { groups: [], targets: [], transactions: [] };
        try { return JSON.parse(raw); } catch { return { groups: [], targets: [], transactions: [] }; }
    }

    private saveData(data: GuestData) {
        if (typeof window !== "undefined") {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
        }
    }

    async getGroups(): Promise<Group[]> {
        return this.loadData().groups;
    }

    async createGroup(name: string): Promise<Group | null> {
        const data = this.loadData();
        const newGroup = { id: uuidv4(), name };
        data.groups.push(newGroup);
        this.saveData(data);
        return newGroup;
    }

    async deleteGroup(id: string): Promise<boolean> {
        const data = this.loadData();
        data.groups = data.groups.filter(g => g.id !== id);
        // Cascade delete targets?
        const groupTargets = data.targets.filter(t => t.group_id === id);
        const targetIds = groupTargets.map(t => t.id);
        data.targets = data.targets.filter(t => t.group_id !== id);
        data.transactions = data.transactions.filter(tx => !targetIds.includes(tx.target_id));
        this.saveData(data);
        return true;
    }

    async getTargets(groupId: string): Promise<Target[]> {
        const data = this.loadData();
        let targets = data.targets.filter(t => t.group_id === groupId);
        if (targets.length === 0) return [];

        // Fetch Live Prices (Public API)
        const stockIds = targets.map(t => t.stock_id).join(',');
        let livePrices: any = {};
        if (stockIds) {
            try {
                // Use Public endpoint if possible, or same endpoint?
                // backend /api/portfolio/prices is technically open? No, depends on Auth middleware.
                // We'll try fetching. If 401, we might need a public price proxy.
                // Actually /api/portfolio/prices DOES NOT have Depends(get_current_user) in main.py? 
                // Let's check main.py... It's just @app.get... def api_live_prices(stock_ids: str):
                // It does NOT have dependency. So it IS public! Perfect.
                const pRes = await fetch(`${API_BASE}/api/portfolio/prices?stock_ids=${stockIds}`);
                if (pRes.ok) livePrices = await pRes.json();
            } catch { }
        }

        // Calculate "Lite" Stats Client-Side
        for (const t of targets) {
            t.livePrice = livePrices[t.stock_id] || null;
            const currentPrice = t.livePrice?.price || 0;

            // Calc Holdings from TX
            const txs = data.transactions.filter(tx => tx.target_id === t.id);
            let shares = 0;
            let cost = 0;

            // Simple AVG Cost Logic
            for (const tx of txs) {
                if (tx.type === 'buy') {
                    const totalCost = (shares * (cost / Math.max(1, shares) || 0)) + (tx.shares * tx.price); // Rough approx
                    // Better: track total invested
                    cost += tx.shares * tx.price;
                    shares += tx.shares;
                } else {
                    // Sell: reduce shares, reduce cost proportionally
                    if (shares > 0) {
                        const avgCost_unit = cost / shares;
                        cost -= (tx.shares * avgCost_unit);
                        shares -= tx.shares;
                    }
                }
            }

            // Clamp
            if (shares < 0) shares = 0;
            if (cost < 0) cost = 0;

            const avg_cost = shares > 0 ? cost / shares : 0;
            const market_value = shares * currentPrice;
            const unrealized_pnl = market_value - cost;
            const unrealized_pnl_pct = cost > 0 ? (unrealized_pnl / cost) * 100 : 0;

            t.summary = {
                total_shares: shares,
                avg_cost: avg_cost,
                market_value: market_value,
                realized_pnl: 0, // Not supported in Lite
                unrealized_pnl: unrealized_pnl,
                unrealized_pnl_pct: unrealized_pnl_pct,
                total_dividend_cash: 0 // Not supported in Lite
            };
        }

        return targets;
    }

    async addTarget(groupId: string, stockId: string, name: string): Promise<Target | null> {
        const data = this.loadData();
        const newTarget: Target = {
            id: uuidv4(),
            group_id: groupId,
            stock_id: stockId,
            stock_name: name || stockId,
        };
        data.targets.push(newTarget);
        this.saveData(data);
        return newTarget;
    }

    async deleteTarget(id: string): Promise<boolean> {
        const data = this.loadData();
        data.targets = data.targets.filter(t => t.id !== id);
        data.transactions = data.transactions.filter(tx => tx.target_id !== id);
        this.saveData(data);
        return true;
    }

    async getTransactions(targetId: string): Promise<Transaction[]> {
        const data = this.loadData();
        return data.transactions.filter(t => t.target_id === targetId);
    }

    async saveTransaction(t: Partial<Transaction> & { target_id?: string }): Promise<boolean> {
        const data = this.loadData();
        if (t.id) {
            // Edit
            const idx = data.transactions.findIndex(tx => tx.id === t.id);
            if (idx !== -1) {
                data.transactions[idx] = { ...data.transactions[idx], ...t } as Transaction;
                this.saveData(data);
                return true;
            }
            return false;
        } else {
            // New
            if (!t.target_id) return false;
            const newTx: Transaction = {
                id: uuidv4(),
                target_id: t.target_id,
                type: t.type || 'buy',
                shares: t.shares || 0,
                price: t.price || 0,
                date: t.date || new Date().toISOString()
            };
            data.transactions.push(newTx);
            this.saveData(data);
            return true;
        }
    }

    async deleteTransaction(id: string): Promise<boolean> {
        const data = this.loadData();
        data.transactions = data.transactions.filter(t => t.id !== id);
        this.saveData(data);
        return true;
    }

    async getDividends(targetId: string): Promise<Dividend[]> {
        return []; // Not supported
    }

    async getDividendStats(): Promise<{ total_cash: number; dividend_count: number }> {
        return { total_cash: 0, dividend_count: 0 }; // Not supported
    }

    async syncDividends(): Promise<boolean> {
        return true; // No-op
    }

    // New granular update method (Local Calculation)
    async getTargetSummary(targetId: string, currentPrice?: number): Promise<any> {
        const data = this.loadData();
        const txs = data.transactions.filter(t => t.target_id === targetId);
        const price = currentPrice || 0;

        let shares = 0;
        let cost = 0;

        for (const tx of txs) {
            if (tx.type === 'buy') {
                cost += tx.shares * tx.price;
                shares += tx.shares;
            } else {
                if (shares > 0) {
                    const avgCost_unit = cost / shares;
                    cost -= (tx.shares * avgCost_unit);
                    shares -= tx.shares;
                }
            }
        }

        if (shares < 0) shares = 0;
        if (cost < 0) cost = 0;

        const avg_cost = shares > 0 ? cost / shares : 0;
        const market_value = shares * price;
        const unrealized_pnl = market_value - cost;
        const unrealized_pnl_pct = cost > 0 ? (unrealized_pnl / cost) * 100 : 0;

        return {
            total_shares: shares,
            avg_cost: avg_cost,
            market_value: market_value,
            realized_pnl: 0,
            unrealized_pnl: unrealized_pnl,
            unrealized_pnl_pct: unrealized_pnl_pct,
            total_dividend_cash: 0
        };
    }
}

// Factory
export class PortfolioFactory {
    static getService(isLoggedIn: boolean): IPortfolioService {
        return isLoggedIn ? new ApiPortfolioService() : new GuestPortfolioService();
    }
}
