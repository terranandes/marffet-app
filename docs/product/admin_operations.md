# Martian Admin Operations Guide 🛰️🕹️

**Owner**: [PL] / [PM]
**Last Updated**: 2026-02-13

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
| **Cold Reset** | 🔥 **Force Rebuild (Cold)** | Clears current year JSON cache and re-crawls from source. | `CrawlerService.run_market_analysis(force=True)` |
| **Global Push** | 📦 **Rebuild Pre-warm Data** | Forced rebuild of all 25 years of persistence files + Upload. | `BackupService.annual_prewarm_with_rebuild()` |

---

### Section C: System Tools & Deep Universe

| Action | Control Label | Technical Context |
| :--- | :--- | :--- |
| **RAM Reload** | 🔋 **Reload Price Cache (Force)** | Re-loads all price JSON files into the FastAPI process memory (O(1) access). |
| **Backfill** | 🚀 **Universe Backfill (2000+)** | Downloads history from 2000 to Present for the entire universe. Note: Toggle **Push to GitHub** to make changes permanent on Zeabur. |

---

## 2. Automated Background Crons (Schedules)

These jobs run on the Zeabur server/local host via `crontab`.

| Job Name | Script Path | Schedule | Logic | GitHub Persistence |
| :--- | :--- | :--- | :--- | :--- |
| **Nightly Refresh** | `refresh_current_year.sh` | 22:00 HKT | Incremental price fetch + merge. | ✅ Yes |
| **Quarterly Sync** | `quarterly_dividend_sync.sh` | Q-Start 02:00 | Global Universe Dividend refresh. | ✅ Yes |
| **Annual Pre-warm** | `annual_prewarm.sh` | Jan 1st 02:00 | Full universe health check + re-upload. | ✅ Yes |
| **DB Backup** | (Internal) | Daily 04:00 | SQLite Snapshot. | ✅ Yes |

---

## 3. Data Integrity & Persistence Loop

The system operates on a **"Crawl-Local-Push"** cycle:
1.  **Crawl**: Data is fetched from TWSE/TPEx or Yahoo Finance.
2.  **Local Storage**: Data is merged into `data/raw/Market_YYYY_Prices.json`.
3.  **Persistence**: The `BackupService` creates a git commit and pushes to `origin master`.
4.  **Deployment**: Zeabur detects the push and redeploys the App with "Pre-warmed" data.

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
