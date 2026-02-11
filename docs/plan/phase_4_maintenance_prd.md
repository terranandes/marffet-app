# Product Requirement Document: Phase 4 Maintenance & Admin Enhancement

**Project:** Martian Investment System
**Phase:** 4 - Maintenance & Admin Tools
**Author:** AntiGravity Agent
**Date:** 2026-02-12
**Status:** COMPLETE (v2 - Safe Mode Emphasis)

---

## 1. Executive Summary
The Martian Investment System (MIS) relies on a "Single Source of Truth" (SSOT) JSON cache for market data. Currently, gaps exist in historical data (2000-2023) because the crawler prioritizes recent data for performance. Phase 4 introduces a **Universe Backfill Service** to robustly populate these gaps without overwriting manually corrected data, controlled via the **GM Dashboard**.

## 2. Problem Statement
- **Data Gaps:** New tickers or tickers added post-initialization lack historical data prior to their inclusion.
- **Data Integrity:** A naive "fetch all" backfill overwrites manual patches (e.g., TSMC split adjustments, Syntrend corrections).
- **Usability:** The GM (Admin) has no way to trigger maintenance tasks without CLI access.

## 3. Goals & Objectives
1.  **Complete History:** Ensure 100% data coverage for the target universe (2000-2023).
2.  **Data Safety:** Implement "Smart Merge" logic that *never* overwrites existing ticker data during auto-backfill.
3.  **Admin Control:** Provide a one-click "Backfill" button with real-time progress monitoring in the Admin Dashboard.

## 4. Feature Specifications

### 4.1. Background Backfill Service
- **Type:** Async Background Task (FastAPI).
- **Logic:**
    - Iterate through all tickers in `stock_list.csv`.
    - Download full history (`period="max"`).
    - **Smart Merge Rule (CRITICAL):**
        - Load existing `Market_{Year}_Prices.json`.
        - If `ticker` exists in `json[year]`, **SKIP**.
        - If `ticker` is missing, **APPEND**.
    - **Trigger:** Manual via Admin Dashboard (Phase 4 scope). No automatic cron schedule.
    - **Rate Limiting:** Process in chunks of 50 with 1s delays.
    - **Dividend History:** Extract from `yfinance` (`actions=True`), transform splits, and merge into `TWSE_Dividends_{Year}.json`. Covers 2000-Present.

### 4.2. Admin Dashboard Update
- **Section:** System Operations > Universe Maintenance.
- **Controls:**
    - Button: `🚀 Backfill Missing History (Safe Mode)`
    - Tooltip: "Fetches missing data for 2000-2023. Will NOT overwrite existing data."
- **Feedback:**
    - Progress Bar: Shows generic `CrawlerStatus` percentage.
    - Status Text: `[Backfill] Processing chunk X/Y...`

### 4.3. API Contract
- **Endpoint:** `POST /api/admin/market-data/backfill`
- **Params:**
    - `overwrite` (bool, default=`False`): Toggles Smart Merge vs. Force Overwrite.
- **Response:**
    - `202 Accepted`: "Backfill started in background."
    - `403 Forbidden`: Non-admin access.
    - Status reporting through `/api/admin/crawl/status`.

## 5. Non-Functional Requirements
- **Performance:** Backfill must not degrade "Smart Crawl" performance if running concurrently (though UI prevents concurrent triggers).
- **Reliability:** Must handle network failures gracefully (skip chunk and continue).

## 6. Success Metrics
- **Data Completeness:** 100% of tickers in `stock_list.csv` have entries in `Market_2023_Prices.json` (and prior years).
- **Safety:** Manual patches in `data/raw/` remain unchanged after backfill.

## 7. Implementation Tasks (Ralph Loop)
- [x] **Task 1 (Backend):** Refactor `market_data_service` for Smart Merge.
- [x] **Task 2 (Backend):** Implement `CrawlerService.run_universe_backfill`.
- [x] **Task 3 (Frontend):** Build "Universe Maintenance" UI Card.
- [x] **Task 4 (Verify):** Verify Smart Merge with dummy data integration test.
