# Martian Admin Operations Guide 🛰️🕹️

**Owner**: [PL] / [PM]
**Last Updated**: 2026-02-17

This document serves as the definitive reference for GM (Game Master) operations, including manual dashboard tools and automated background processes.

---

## 1. Manual Dashboard Operations (System Operations)

Located at `/admin` on the Martian Frontend.

### Section A: Routine Operations (Daily/Weekly)

| Action | Control Label | Technical Endpoint | Scope | Data Persistence |
| :--- | :--- | :--- | :--- | :--- |
| **Price Update** | ✨ **Smart Supplemental Refresh** | `POST /api/admin/market-data/supplemental` | Held Stocks + Top 100 ETFs | **Local Only** (until nightly cron) |
| **Dividend Sync** | 💰 **Sync All Dividends** | `POST /api/admin/market-data/sync-dividends` | **Global Universe** (1,771 stocks) | ✅ **Auto-Push to GitHub** |
| **DB Backup** | 💾 **GitHub Backup (DB)** | `POST /api/admin/backup` | `portfolio.db` | ✅ **Auto-Push to GitHub** |

> [!TIP]
> Use **Smart Supplemental Refresh** when you want to see the absolute latest price movement for your active portfolio without waiting for the nightly cron.

---

### Section B: Maintenance & Repair

| Action | Control Label | Purpose | Key Script / Method |
| :--- | :--- | :--- | :--- |
| **Full Run** | 🕷️ **Crawler Analysis (Full)** | Re-calculates ROI/Strategy for current year universe. | `run_analysis.main()` |
| **Cold Reset** | 🔥 **Force Rebuild (Cold)** | Drops the DuckDB and recreates it from MI_INDEX snapshot checkpoints. | `scripts/ops/rebuild_market_db.py` |
| **Global Push** | 📦 **Rebuild Pre-warm Data** | Forced rebuild of Parquet persistence files + Upload to git. | `backup_duckdb.py` |

---

### Section C: System Tools & Deep Universe

| Action | Control Label | Technical Context |
| :--- | :--- | :--- |
| **RAM Reload** | 🔋 **Reload Price Cache (Force)** | Instructs the `MarketCache` singleton to re-query DuckDB and refresh in-memory tables. |
| **Backfill** | 🚀 **Universe Backfill (2000+)** | Downloads history from 2000 to Present for the entire universe. Note: Toggle **Push to GitHub** to make changes permanent on Zeabur via Parquets. |

---

## 2. Automated Background Crons (Schedules)

These jobs run on the Zeabur server/local host via `crontab`.

| Job Name | Script Path | Schedule | Logic | Data Target |
| :--- | :--- | :--- | :--- | :--- |
| **Nightly Full Supplement** | `nightly_full_supplement.py` (via `refresh_current_year.sh`) | 22:00 HKT | Fetches last 2 trading days (`period=2d`) for ALL stocks → DuckDB. 1-day safety buffer in case cron misses a night. | **DuckDB** (1,629 stocks) |
| **Quarterly Sync** | `quarterly_dividend_sync.sh` | Q-Start 02:00 | Global Universe Dividend refresh. | ✅ GitHub |
| **Annual Pre-warm** | `annual_prewarm.sh` | Jan 1st 02:00 | Full universe health check + re-upload. | ✅ GitHub |
| **DB Backup** | (Internal) | Daily 04:00 | SQLite (`portfolio.db`) snapshot. | ✅ GitHub |

---

## 3. Data Integrity & Persistence Loop

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

## 4. Operational Status Reference

- **Crawler Status**: Monitor via `Crawler Status` bar on `/admin`.
- **System Logs**: View terminal output or Zeabur application logs for `CrawlerService` tags.
- **Persistence Log**: Check GitHub Commit history for automated commits tagged `[PL] / [BM]`.
