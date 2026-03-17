# Portfolio Tab — Feature Specification

**Date**: 2026-03-13
**Owner**: [SPEC] Agent
**Status**: Production

---

## 1. Overview

The **Portfolio** tab (`/portfolio`) is the personal investment tracker. Users create **Groups** (e.g., "Dividend", "Growth"), add **Targets** (stocks, ETFs, CBs), and log **Transactions** (buy/sell). The system calculates P/L, syncs dividends, and provides live price feeds.

---

## 2. Core Concepts

| Concept       | Description                                                                 |
|:------------- |:--------------------------------------------------------------------------- |
| **Group**     | A logical container (e.g., "Dividend Kings"). Each user can create multiple. |
| **Target**    | A stock/ETF/CB within a group, identified by `stock_id`.                    |
| **Transaction** | A buy or sell record: `type`, `shares`, `price`, `date`.                 |
| **Dividend**  | Auto-synced from DuckDB. Tracks cash dividends per target.                  |

### Entity Relationship

```
User ──1:N──▶ Group ──1:N──▶ Target ──1:N──▶ Transaction
                                │
                                └──1:N──▶ Dividend (auto-synced)
```

---

## 3. Frontend

**Route**: `/portfolio`
**File**: `frontend/src/app/portfolio/page.tsx` (11 sub-files)

### UI Sections (Webull Style)

1. **Group Sidebar** — Create, rename, delete groups
2. **Target List** — Add stocks by code; 7-column stacked desktop layout with hover `...` action menus.
3. **Transaction Log** — Buy/sell entries with date, price, shares
4. **Summary Cards** — Premium stats cards (Total Cost, Market Value, ROI%, Dividend Income) paired with an **ECharts Donut Chart** for asset allocation visualization.
5. **Live Prices** — Real-time price, change, change% for each target
6. **Mobile UX** — "Cyberpunk" styled target cards with `framer-motion` stagger animations for optimal small-screen viewing.

### Asset Types

| Type    | Code    | Example  |
|:------- |:------- |:-------- |
| Stock   | `stock` | 2330     |
| ETF     | `etf`   | 0050     |
| CB      | `cb`    | 65331    |

### State Management & Loading Strategy

- **Initial Load**: Handled by Next.js `loading.tsx` and custom Skeleton components (e.g., `TableSkeleton`, `ChartSkeleton`, `LeaderboardSkeleton`). These provide immediate visual feedback while the first SWR fetch is propagating from the server to the client.
- **Background Revalidation**: Triggered via `isValidating` from SWR hooks (`usePortfolioData`, etc.). To prevent jarring UI flashes on subsequent re-fetches, the global `<SyncIndicator>` component is shown instead of replacing the entire UI with Skeletons.
- **Mutation Sync**: SWR's `mutate` is called automatically after successful API requests (add, delete, sync) to keep the local cache consistent with the DB.
- **Tab Persistence**: The active group tab is persisted using `localStorage` (via the `initialTab` pattern) to ensure the user returns to their last viewed portfolio group upon reload.
- **Client-Side AuthGuard**: The `/portfolio` route enforces authentication via `AuthGuard`. Guest users bypass traditional login but are managed via `localStorage` state (`marffet_guest_mode`). Because of this, direct server-side renderings of the portfolio require hydration before the client-side token is read, or the user may be incorrectly redirected.

---

## 4. Backend API

**Router**: `app/routers/portfolio.py`
**Service**: `app/services/portfolio_service.py`
**Auth**: All endpoints require `get_current_user` (session cookie)

### Groups

| Method   | Endpoint                       | Description          |
|:-------- |:------------------------------ |:-------------------- |
| `GET`    | `/api/portfolio/groups`        | List all groups      |
| `POST`   | `/api/portfolio/groups`        | Create new group     |
| `DELETE` | `/api/portfolio/groups/{id}`   | Delete group         |

### Targets

| Method   | Endpoint                                    | Description                  |
|:-------- |:------------------------------------------- |:---------------------------- |
| `GET`    | `/api/portfolio/groups/{gid}/targets`       | List targets in group        |
| `POST`   | `/api/portfolio/groups/{gid}/targets`       | Add stock/ETF/CB to group    |
| `DELETE` | `/api/portfolio/targets/{tid}`              | Remove target                |
| `GET`    | `/api/portfolio/by-type`                    | All targets grouped by type  |

### Transactions

| Method   | Endpoint                                          | Description          |
|:-------- |:------------------------------------------------- |:-------------------- |
| `GET`    | `/api/portfolio/targets/{tid}/transactions`       | List transactions    |
| `POST`   | `/api/portfolio/targets/{tid}/transactions`       | Add buy/sell         |
| `PUT`    | `/api/portfolio/transactions/{txid}`              | Update transaction   |
| `DELETE` | `/api/portfolio/transactions/{txid}`              | Delete transaction   |

### Dividends

| Method   | Endpoint                                      | Description                      |
|:-------- |:--------------------------------------------- |:-------------------------------- |
| `GET`    | `/api/portfolio/cash`                         | Total dividend cash for user     |
| `POST`   | `/api/portfolio/sync-dividends`               | Sync dividends from DuckDB      |
| `GET`    | `/api/portfolio/targets/{tid}/dividends`      | Dividend history for target      |

### Other

| Method   | Endpoint                               | Description                        |
|:-------- |:-------------------------------------- |:---------------------------------- |
| `GET`    | `/api/portfolio/prices?stock_ids=...`  | Live prices (comma-separated IDs)  |
| `GET`    | `/api/portfolio/trend?months=12`       | Monthly cost trend for chart       |
| `GET`    | `/api/portfolio/race-data`             | Race data for My Race BCR          |
| `GET`    | `/api/portfolio/ladder`                | Asset distribution ladder          |
| `POST`   | `/api/portfolio/sync-stats`            | Sync wealth stats for leaderboard  |
| `GET`    | `/api/portfolio/targets/{tid}/summary` | P/L summary for a target (flat `total_dividend_cash`) |

---

## 5. Database

**Storage**: SQLite (`portfolio.db`)
**Location**: `/data/portfolio.db` (Zeabur volume) or `data/portfolio.db` (local)

### Tables

| Table               | Key Columns                                        |
|:------------------- |:-------------------------------------------------- |
| `users`             | `id`, `email`, `nickname`, `picture`, `is_admin`   |
| `user_groups`       | `id`, `user_id`, `name`, `created_at`              |
| `group_targets`     | `id`, `group_id`, `stock_id`, `stock_name`, `type` |
| `transactions`      | `id`, `target_id`, `type`, `shares`, `price`, `date` |
| `dividends`         | `id`, `target_id`, `ex_date`, `cash_amount`        |
| `user_stats`        | `user_id`, `market_value`, `roi`, `total_cost`     |

---

## 6. Premium Limits

| Feature            | Free Tier | Premium Tier |
|:------------------ |:--------- |:------------ |
| Groups             | 11        | 30           |
| Targets per Group  | 50        | 200          |
| Transactions       | 100       | 1,000        |

---

## 7. Data Flow

```
User Input (Buy/Sell) ──▶ portfolio.db (or localStorage for Guest) ──▶ Portfolio Page
                                             │
DuckDB (dividends table) ──▶ Sync ──▶ portfolio.db (dividends)
                                             │
yfinance (live prices) ──▶ /api/portfolio/prices ──▶ Live Price Cards
```
