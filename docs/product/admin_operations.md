# Marffet Admin Operations Guide 🛰️🕹️

**Owner**: [PL] / [PM]
**Last Updated**: 2026-02-28

This document serves as the definitive reference for GM (Game Master) operations, including manual dashboard tools and automated background processes.

---

## 1. GM Dashboard Layout (`/admin`)

The dashboard is organized into **5 collapsible sections** with persistent open/close state (saved to `localStorage`). Default open: **Metrics** and **Feedback**. All operation buttons show inline loading spinners and results via `react-hot-toast` notifications (bottom-right).

### Global Status Bar
A persistent crawler status indicator is always visible at the top of the dashboard (outside sections). It shows:
- **Running** state with elapsed time and animated pulse
- **Success/Error** state with last run duration
- **Progress bar** for active crawl operations
- **Dividend sync progress** bar when syncing

---

## 2. Manual Dashboard Operations

### Section: 📊 User Metrics (default: open)

Displays user registration counts, active users (Web/Mobile, last 30 days), and subscription tier breakdown (Free/Premium/VIP).
Includes an **Account Growth History** ECharts line graph showing cumulative registrations and premium/VIP subscriptions over time.

---

### Section: 👑 Membership Injection (default: open)

Manually manage user access via Google emails. Grants are stored persistently in `/data/portfolio.db` (`user_memberships` table).

| Input | Description | Result State |
| :--- | :--- | :--- |
| **Email** | Valid Google account email. | Target user account identifier |
| **Tier** | `VIP` or `PREMIUM` | Access level overrides `FREE` |
| **Duration** | `Monthly` (30d), `Annually` (365d), `Permanent` (99y) | Expiration date of access |
| **Add** | Injects or updates membership. | Appears in active table below |
| **Revoke** | Immediately deletes the injected membership. | User reverts to highest remaining tier |

*Note: Environment variables (`GM_EMAILS`, `VIP_EMAILS`, `PREMIUM_EMAILS`) always take static precedence (`GM > VIP > PREMIUM`). If injected status expires, user reverts to static `.env` settings or Free tier. Guest users (no login) cannot receive injections.*

> **Sponsorship Fulfillment Workflow**: When a user supports the project via **Ko-fi** or **Buy Me a Coffee**, they must provide their registered Google email to the GM. The GM then manually injects the `PREMIUM` or `VIP` status via this dashboard with the appropriate duration (e.g., Annually or Permanent).

---

### Section: 📅 Routine Operations (default: closed)

| Action | Control Label | Technical Endpoint | Scope | Data Persistence |
| :--- | :--- | :--- | :--- | :--- |
| **Price Update** | ✨ **Smart Supplemental Refresh** | `POST /api/admin/market-data/supplemental` | Held Stocks + Top 100 ETFs | **Local Only** (until nightly cron) |
| **Dividend Sync** | 💰 **Sync All Dividends** | `POST /api/sync/all-users-dividends` | All users' held stocks | Shows progress bar during sync |
| **DB Backup** | 💾 **GitHub Backup (DB)** | `POST /api/admin/backup` | `portfolio.db` | ✅ **Auto-Push to GitHub** |

> [!TIP]
> Use **Smart Supplemental Refresh** when you want to see the absolute latest price movement for your active portfolio without waiting for the nightly cron.

---

### Section: 🛠️ Maintenance & Repair (default: closed)

| Action | Control Label | Purpose | Key Script / Method |
| :--- | :--- | :--- | :--- |
| **Full Run** | 🕷️ **Crawler Analysis (Full)** | Re-calculates ROI/Strategy for current year universe. | `run_analysis.main()` |
| **Cold Reset** | 🔥 **Force Rebuild (Cold)** | Drops the DuckDB and recreates it from MI_INDEX snapshot checkpoints. | `scripts/ops/rebuild_market_db.py` |
| **Global Push** | 📦 **Rebuild Pre-warm Data** | Forced rebuild of Parquet persistence files + Upload to git. | `backup_duckdb.py` |

---

### Section: ⚙️ System Tools & Deep Universe (default: closed)

| Action | Control Label | Technical Context |
| :--- | :--- | :--- |
| **RAM Reload** | 🔋 **Reload Price Cache (Force)** | Instructs the `MarketCache` singleton to re-query DuckDB and refresh in-memory tables. |
| **Copy URL** | 🔗 **Copy Metrics URL** | Copies the admin metrics API endpoint to clipboard. |
| **Backfill** | 🚀 **Universe Backfill (2000+)** | Downloads history from 2000 to Present for the entire universe. |

**Backfill Toggles:**
| Toggle | Description |
| :--- | :--- |
| 🛡️ **Safe Mode** | ON = Incremental (won't overwrite). OFF = ⚠️ Full overwrite. |
| 📤 **Push to GitHub** | ON = Push Parquets to GitHub on completion. OFF = Zeabur local only. |
| 🌌 **Deep Universe** | ON = Include warrants. OFF = Stocks/ETFs only. Auto-enabled on localhost. |

---

### Section: 📬 User Feedback & Bug Reports (default: open)

| Feature | Description |
| :--- | :--- |
| **Stats Row** | Counters for New / Reviewing / Confirmed / Fixed / Won't Fix |
| **Feedback List** | Scrollable list with type badges (🐛 Bug, ✨ Feature, 📝 Content) |
| **Status Dropdown** | Inline status update per feedback item (triggers toast + API PATCH) |
| **Agent Notes** | Expandable textarea for internal agent notes per feedback item |
| **Copy as JIRA** | 📋 Copies feedback as formatted markdown for JIRA/ticket systems |

**Supported Feedback Categories (Frontend + Backend):**
`mars_strategy`, `bar_chart_race`, `portfolio`, `trend`, `my_race`, `ai_copilot`, `leaderboard`, `settings`, `subscription`, `cash_ladder`, `compound_interest`, `other`

---

## 3. Automated Background Crons (Schedules)

These jobs run on the Zeabur server/local host via `crontab`.

| Job Name | Script Path | Schedule | Logic | Data Target |
| :--- | :--- | :--- | :--- | :--- |
| **Nightly Full Supplement** | `nightly_full_supplement.py` (via `refresh_current_year.sh`) | 22:00 HKT | Fetches last 2 trading days (`period=2d`) for ALL stocks → DuckDB. 1-day safety buffer in case cron misses a night. | **DuckDB** (1,629 stocks) |
| **Quarterly Sync** | `quarterly_dividend_sync.sh` | Q-Start 02:00 | Global Universe Dividend refresh. | ✅ GitHub |
| **Annual Pre-warm** | `annual_prewarm.sh` | Jan 1st 02:00 | Full universe health check + re-upload. | ✅ GitHub |
| **DB Backup** | (Internal) | Daily 04:00 | SQLite (`portfolio.db`) snapshot. | ✅ GitHub |

---

## 4. Data Integrity & Persistence Loop

The system operates on a **"Crawl → DuckDB → Serve"** cycle:
1.  **Crawl**: Price data is fetched from Yahoo Finance (`yfinance`) for all stocks.
2.  **DuckDB Storage**: Data is upserted into `data/market.duckdb` (or `/data/market.duckdb` on Zeabur).
3.  **Serve**: Mars Strategy and other tabs query DuckDB directly on each request (with SIM_CACHE for performance).
4.  **Persistence**: `portfolio.db` is backed up to GitHub. DuckDB is downloadable via `GET /api/admin/backup/duckdb`.

### Manual Data Patching
If data is missing for a specific ticker (e.g., historical gaps for 5314 or 2330), use:
```bash
uv run python scripts/ops/patch_stock_data.py --tickers 2330,5314 --years 2000..2025
```
Then trigger a manual **Backup** to save to GitHub.

---

## 5. Operational Status Reference

- **Crawler Status**: Monitor via the persistent **Global Status Bar** at the top of `/admin`.
- **Toast Notifications**: All operations confirm success/failure via `react-hot-toast` (bottom-right).
- **System Logs**: View terminal output or Zeabur application logs for `CrawlerService` tags.
- **Persistence Log**: Check GitHub Commit history for automated commits tagged `[PL] / [BM]`.
