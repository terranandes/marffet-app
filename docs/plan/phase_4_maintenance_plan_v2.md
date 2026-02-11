# Phase 4 Plan: Maintenance & Admin Enhancement (v2)

**Author:** AntiGravity Agent
**Date:** 2026-02-12
**Status:** DRAFT (Step 2 of Ralph Loop)

## 1. Objective
Enable the GM (Admin) to safely backfill historical market data (2000-2023) to eliminate data gaps, without compromising the integrity of manually patched data.

## 2. Technical Architecture

### 2.1 Backend Service
- **Service Layer:** `MarketDataService` must support a strictly additive "Smart Merge" operation.
- **Background Task:** Use FastAPI `BackgroundTasks` to decouple the long-running process from the HTTP request cycle.
- **State Management:** `CrawlerService` will maintain a shared state (`is_running`, `progress_pct`, `message`) to report progress to the frontend.

### 2.2 API Layer
- **Endpoint:** `POST /api/admin/market-data/backfill`
- **Parameters:**
    - `period`: Defaults to "max".
    - `overwrite`: Defaults to `False` (Safe Mode).
- **Security:** Strict Admin access control.

### 2.3 Frontend UI
- **Component:** `AdminPage` (GM Dashboard).
- **Feature:** "Universe Maintenance" Control Card.
- **Interaction:**
    - Button triggers the API.
    - Status bar polls `/api/admin/crawl/status`.

## 3. Implementation Strategy (Safe Mode)

### The "Smart Merge" Protocol
To prevent data loss, the backfill process MUST adhere to:
1. **Load Existing Data:** Read the target JSON file into memory first.
2. **Fetch New Data:** Download fresh data from source (Yahoo Finance).
3. **Compare & Append:**
    - Iterate through the fetched data.
    - **IF** ticker key exists in the loaded JSON -> **SKIP** (Do not touch).
    - **IF** ticker key is missing -> **ADD**.
4. **Save:** Write the merged dataset back to disk.

### Trigger Mechanism
- **Primary:** Manual Trigger via **Admin Dashboard** (User Initiated).
- **Secondary:** API Endpoint (`POST /api/admin/market-data/backfill`).
### Dividend Backfill (yfinance Integration)
- **Source:** `yfinance` (actions=True).
- **Process:**
    1. During `backfill_all_stocks`, extract `Dividends` and `Stock Splits`.
    2. Transform:
        - `Dividends` column -> `cash` value.
        - `Stock Splits` column -> `stock` value using formula: `(SplitRatio - 1) * 10`.
    3. Aggregate by Year.
    4. **Smart Merge:** Load `TWSE_Dividends_{Year}.json`, merge new data (key check), save back.
- **Coverage:** Full history (2000-Present) automatically included via `period="max"`.

This ensures that any manual corrections (e.g., split adjustments for 2330.TW) are respected.

## 4. Verification Plan
- **Unit Test:** `test_smart_merge.py` (Mocked data scenario).
- **Integration Test:** Trigger via API and observe status transition.
- **Manual:** Verify on Zeabur post-deployment.
