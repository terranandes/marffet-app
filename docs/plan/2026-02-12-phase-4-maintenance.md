# Phase 4: Maintenance & Admin Enhancement Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement a reliable, background-compatible backfill process for missing historical market data (2000-2023) across the entire stock universe, and provide administrative controls via the GM Dashboard for manual triggering and status monitoring.

**Architecture:** 
- **Backend:** Extend `CrawlerService` to handle "Universe Backfill" as an async background task.
- **Service Logic:** Refactor `market_data_service.py` to support `BackfillSession` with progress reporting and "append-mode" (avoiding overwrites of healthy data).
- **Frontend:** Update `GM Dashboard` with a new Control Card for "Universe Maintenance".

**Tech Stack:** FastAPI `BackgroundTasks`, yfinance, React, TailwindCSS.

---

### Task 1: Refactor Market Data Service for Backfill
**Files:**
- Modify: `app/services/market_data_service.py`
- Test: `tests/unit/test_backfill_logic.py`

**Requirement:**
- Refactor `backfill_all_stocks` to accept a `progress_callback` (callable).
- Add `overwrite: bool = True` parameter. If `False`, it must load existing JSON files and only fetch/append data for tickers not already present in that year/market.
- Ensure efficient batching (50 tickers/chunk) with 1-second delay between chunks to minimize rate limiting.

### Task 2: Implement Backfill Service in CrawlerService
**Files:**
- Modify: `app/services/crawler_service.py`

**Requirement:**
- Add `run_universe_backfill` class method.
- Use a dedicated `_backfill_progress` and `_backfill_status` state (or share current crawler state if logic allows).
- Integration: Call `market_data_service.backfill_all_stocks(overwrite=False, progress_callback=update_progress)`.

### Task 3: API Endpoint for Backfill
**Files:**
- Modify: `app/main.py`
- Modify: `app/routers/admin.py`

**Requirement:**
- Add `POST /api/admin/universe-backfill` endpoint.
- Protect with `get_admin_user` or `GM_EMAILS` check.
- Trigger `CrawlerService.run_universe_backfill` as a `BackgroundTasks`.

### Task 4: Admin Dashboard UI Update
**Files:**
- Modify: `frontend/src/app/admin/page.tsx`

**Requirement:**
- Add "Universe Maintenance" section.
- Button: "🚀 Backfill Missing History (2000-2023)".
- Status: Connect to the `CrawlerStatus` polling mechanism to show progress of the backfill task.
- Ensure the progress bar clearly distinguishes between "Smart Analytics Crawl" and "Full Universe Backfill".

### Task 5: Verification (Local & Remote)
**Files:**
- Create: `tests/integration/test_backfill_flow.py`

**Requirement:**
- Verify that clicking the button initiates the task.
- Verify that data is appended to JSON files rather than completely replacing them (if `overwrite=False`).
- Final manual check on Zeabur after deployment.

---
**Plan saved to:** `docs/plan/2026-02-12-phase-4-maintenance.md`
