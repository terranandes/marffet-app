# Admin Tab — Feature Specification

**Date**: 2026-02-28
**Owner**: [SPEC] Agent
**Status**: Production (GM Only)

---

## 1. Overview

The **Admin** tab (`/admin`) is the Game Master (GM) control panel. It provides system metrics, data pipeline controls, crawler management, feedback triage, and database backup/restore operations. **Access is restricted** to GM emails defined in the `GM_EMAILS` environment variable.

### UI Architecture (Phase 23)
- **5 collapsible sections** with `framer-motion` height transitions
- Open/close state persisted in `localStorage`
- All notifications via `react-hot-toast` (no native `alert()`)
- Loading spinners on all async buttons
- **Purple Ban enforced**: amber/emerald color scheme

---

## 2. Access Control

- **Auth**: Google OAuth session cookie + `get_admin_user` dependency
- **GM Emails**: Configured via `GM_EMAILS` env var (comma-separated)
- **Frontend Guard**: Hidden from sidebar navigation for non-admin users

---

## 3. Dashboard Sections

### 3.1 System Metrics

| Metric              | Source                        | Description                       |
|:------------------- |:----------------------------- |:--------------------------------- |
| Total Users         | `users` table (portfolio.db)  | All registered users              |
| Active Web Users    | Session tracking              | Users with recent web sessions    |
| Active Mobile Users | Session tracking              | Users with recent mobile sessions |
| Subscription Tiers  | `users` table                 | Free / Premium / VIP breakdown    |

**Endpoint**: `GET /api/admin/metrics`

### 3.2 Data Pipeline Controls

| Button                    | Endpoint                              | Description                                    |
|:------------------------- |:------------------------------------- |:---------------------------------------------- |
| ⚡ Initialize Cache       | `POST /api/admin/system/initialize`   | Warm MarketDataProvider + init DuckDB schema   |
| 🔄 Supplemental Refresh   | `POST /api/admin/market-data/supplemental` | Fetch latest data for held stocks         |
| 📊 Universe Backfill      | `POST /api/admin/market-data/backfill` | Full backfill from yfinance (period=max)      |
| 💰 Sync All Dividends     | `POST /api/admin/market-data/sync-dividends` | Global dividend sync for all 1,629 stocks|
| 🚀 Rebuild & Push         | `POST /api/admin/refresh-prewarm`     | Annual prewarm rebuild + GitHub push           |
| 💾 Backup to GitHub       | `POST /api/admin/backup`              | Push portfolio.db + DuckDB to GitHub           |

### 3.3 Crawler Management

| Action        | Endpoint                            | Description                         |
|:------------- |:----------------------------------- |:----------------------------------- |
| Smart Crawl   | `POST /api/admin/crawl?force=false` | Incremental market analysis         |
| Cold Crawl    | `POST /api/admin/crawl?force=true`  | Clear cache + full re-crawl         |
| Check Status  | `GET /api/admin/crawl/status`       | `is_running`, progress %, elapsed_s |

### 3.4 Database Operations

| Action             | Endpoint                            | Description                      |
|:------------------ |:----------------------------------- |:-------------------------------- |
| Download DuckDB    | `GET /api/admin/backup/duckdb`      | Download `market.duckdb` file    |
| Download Portfolio | `GET /api/admin/backup/portfolio`   | Download `portfolio.db` file     |
| Upload DuckDB      | `POST /api/admin/upload/duckdb`     | Upload `.duckdb` file to server  |
| Market Data Stats  | `GET /api/admin/market-data/stats`  | DuckDB row counts and stats      |

### 3.5 Feedback Management

| Action         | Endpoint                       | Description                        |
|:-------------- |:------------------------------ |:---------------------------------- |
| List Feedback  | `GET /api/feedback`            | All feedback (filterable by status)|
| Update Status  | `PATCH /api/feedback/{id}`     | Set status: new/reviewing/fixed/wontfix |
| Feedback Stats | `GET /api/feedback/stats`      | Counts by status                   |
| Add Notes      | `PATCH /api/feedback/{id}`     | Add agent_notes to feedback item   |

---

## 4. Frontend

**Route**: `/admin`
**File**: `frontend/src/app/admin/page.tsx`

### UI Features
- Collapsible glass-card sections (Metrics, Routine, Maintenance, System Tools, Feedback)
- Global crawler status bar with real-time polling
- "Copy as JIRA" button for feedback items
- Inline agent notes per feedback item
- Responsive mobile stacking

### Key Functions

| Function                    | Purpose                                           |
|:--------------------------- |:------------------------------------------------- |
| `handleInitializeCache()`   | POST to `/system/initialize`                      |
| `handleSupplementalRefresh()` | POST to `/market-data/supplemental`             |
| `handleBackfill()`          | POST to `/market-data/backfill`                   |
| `handleSyncAllDividends()`  | POST to `/market-data/sync-dividends` (with simulated progress bar) |
| `handleCrawl(force)`        | POST to `/admin/crawl?force=...`                  |
| `handleRebuildPrewarm()`    | POST to `/refresh-prewarm`                        |
| `handleDbBackup()`          | POST to `/backup`                                 |
| `updateFeedbackStatus()`    | PATCH to `/feedback/{id}`                         |
| `updateFeedbackNotes()`     | PATCH to `/feedback/{id}` (agent_notes field)     |
| `handleCopyMetrics()`       | Copy system metrics to clipboard                  |

---

## 5. Backend Router

**File**: `app/routers/admin.py`
**Prefix**: `/api/admin`

All endpoints use `Depends(get_admin_user)` which validates:
1. User is authenticated (session cookie)
2. User's email is in `GM_EMAILS`

### Background Tasks

Heavy operations use FastAPI `BackgroundTasks`:
- Universe Backfill
- Dividend Sync
- Prewarm Rebuild
- Crawler execution

---

## 6. Related Documentation

- [Admin Operations Manual](./admin_operations.md) — Cron jobs, manual procedures
- [Crawler Architecture](./crawler_architecture.md) — Market analysis crawler
- [DuckDB Architecture](./duckdb_architecture.md) — Data lake schema
- [Backup & Restore](./backup_restore.md) — Disaster recovery
