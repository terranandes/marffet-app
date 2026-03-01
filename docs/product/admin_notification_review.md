# Admin Dashboard & Notification Scheme Review
Date: 2026-03-01
Author: AntiGravity (AI Agent)

This document addresses the two pending questions from `BOSS_TBD.md`.

## 1. Review Admin Dashboard: What are the current operations?
The Admin Dashboard (`/admin`), accessible only to users with an email listed in the `GM_EMAILS` environment variable, currently supports the following operations:

### A. Metrics View
- **Total Registered Users**
- **Active Users** (split by Web / Mobile)
- **Subscription Breakdown** (Free / Premium / VIP tiers)

### B. Routine Operations
- **Smart Supplemental Refresh**: Initiates an incremental market data fetch (`/api/admin/market-data/supplemental`).
- **Sync All Dividends**: Synchronizes the dividend cache for all stocks held by all users across the system (`/api/sync/all-users-dividends`).
- **GitHub Backup (DB)**: Triggers a manual push of the SQLite database to the configured GitHub repository (`/api/admin/backup`).

### C. Maintenance & Repair
- **Crawler Analysis (Standard)**: Runs a standard crawler job (`/api/admin/crawl?force=false`).
- **Force Rebuild (Cold Run)**: Clears the cache and forces a fresh crawler run (`/api/admin/crawl?force=true`).
- **Rebuild Pre-warm Data**: Performs a cold run and pushes ~60 pre-generated cache files to GitHub for fast loading (`/api/admin/refresh-prewarm`).

### D. System Tools & Deep Universe
- **Reload Price Cache (Force)**: Reinitializes core system configurations and caches (`/api/admin/system/initialize`).
- **Copy Metrics URL**: Utility to copy the current metrics endpoint to the clipboard.
- **Universe Backfill (2000+)**: Performs historical price and dividend fetches with configurable toggles:
  - **Safe Mode**: Skip existing vs Overwrite all.
  - **Target System**: Push to GitHub vs Store on Zeabur volume.
  - **Scope**: Smart Universe vs Deep Universe.

### E. User Feedback Management
- View statistics (New, Reviewing, Confirmed, Fixed, Wontfix).
- Read granular feedback, update status, add agent notes, and copy feedback content as JIRA markdown.

---

## 2. Review Notification Scheme: What are the current triggers for Free and Paid users?

### Active Triggers (Currently Global / Unrestricted)
The primary notification system, driven by `NotificationEngine` via `/api/notifications`, runs unconditionally every 30 seconds for any logged-in user. **Currently, there is no code logic separating triggers for Free vs Paid users at the API or Engine level**—all users receive these alerts:

1. **SMA Pair Rebalancing (Gravity Alert)**: 
   - Identifies targets Overvalued (> +20% vs SMA 250) and Undervalued (< -20% vs SMA 250).
   - Suggests a 30% exchange pair trade from the high candidate to the low candidate.
2. **Market Cap Rebalancing (Size Authority)**: 
   - Flags positions representing > 1.2x or < 0.8x the portfolio average market cap.
   - Suggests a 30% exchange pair trade from high capitalization to low capitalization.
3. **Convertible Bond (CB) Arbitrage Alerts**:
   - **Arbitrage**: If CB Premium < -1% (Suggests buying CB, selling underlying stock to equalize weights).
   - **Strong Sell**: If CB Premium >= 30% (Suggests selling CB, buying underlying stock).

### Orphaned / Inactive Triggers (Designed for Premium)
A secondary engine named `RuthlessManager` exists in `app/engines.py`, designed with specific "Premium Rebalancing Notification" logic. However, an architecture search reveals this engine is **orphaned**—it is neither imported nor scheduled anywhere in `app/main.py`. 

Conclusion: To enforce the Free vs Paid distinction, the `/api/notifications` endpoint in `app/main.py` needs to check `user.get('is_premium')` before invoking `NotificationEngine.generate_alerts(portfolio)`, or specific strategies (like CB Arbitrage) need to be gated within the engine itself.
