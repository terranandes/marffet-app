# Phase 14: Nominal Price Standardization & Mars Tab Correction

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Correct the 'Mars' Tab and DuckDB data schema by enforcing a 100% Nominal Price basis, eliminating "Double Adjustment" artifacts, and ensuring the `ROICalculator` correctly handles splits and dividends from raw physics.

**Architecture:** 
- **Data Layer**: Rebuild `market.duckdb` `daily_prices` table using `fetch_mi_index_mass.py` (TWSE Official Source) to ensure pure Nominal prices (2004-2025).
- **Logic Layer**: Update `SplitDetector` to handle Nominal data and prevent double-counting with Stock Dividends.
- **Verification**: New `verify_nominal_integrity.py` suite.

**Tech Stack**: Python, DuckDB, Pandas, Asyncio, httpx.

---

## Task 1: Data Rebuild (Nominal Foundation)

**Files:**
- Modify: `scripts/ops/fetch_mi_index_mass.py` (Harden schema, error handling)
- Create: `scripts/ops/rebuild_market_db.py` (Orchestrator to wipe/rebuild daily_prices)

**Step 1: Harden `fetch_mi_index_mass.py`**
- Ensure robust parsing of non-numeric columns (`--`).
- Ensure `market` column is set to 'TWSE'.
- Add `batch_size` limiting to prevent RAM spikes.

**Step 2: Dry Run & Schema Verification**
- Run for a single month (e.g., Jan 2024).
- Verify loaded data matches `daily_prices` schema.
- Check a known stock (e.g., 2330) for that month to ensure Nominal prices (e.g., matching TWSE website).

**Step 3: Full History Fetch (2004-2025)**
- Execute the mass fetch. This will take time (rate limited).
- *Note*: This might be run in background or parallel session.

---

## Task 2: Logic Correction (Split vs Dividend)

**Files:**
- Modify: `app/services/split_detector.py`
- Modify: `app/services/roi_calculator.py`
- Test: `tests/unit/test_split_logic.py`

**Step 1: Create Test Case for "Large Stock Dividend"**
- Simulating a stock with a 5.0 stock dividend (1.5x shares, 33% drop).
- Simulating a stock with a 2:1 pure split (50% drop).
- Simulating a stock with a 10.0 stock dividend (2x shares, 50% drop) - The Edge Case.

**Step 2: Update `SplitDetector`**
- Modify `detect_splits` to be aware of Dividends (pass `dividend_history` optional arg?).
- OR, modify `ROICalculator` to prioritize Dividend data over Split Detection if they overlap in the same year/month.
- *Decision*: Modify `SplitDetector` to check against `KNOWN_SPLITS` more aggressively, and potentially suppress detection if a Stock Dividend exists for that year > Threshold.

**Step 3: Update `ROICalculator`**
- Remove "Pre-adjusted" detection logic (Lines 162-177 in `roi_calculator.py`) as we are guaranteeing Nominal data.
- Ensure `calculate_complex_simulation` passes `dividend_data` to `SplitDetector` if needed, or strictly strictly separates the two.

---

## Task 3: Verification & Mars Tab Check

**Files:**
- Create: `tests/integration/verify_nominal_integrity.py`
- Test: `tests/integration/test_mars_strategy.py`

**Step 1: Integrity Script**
- Check specific dates for TSMC (2330).
- 2009-07-?? (Dividend/Split event).
- Verify Price is Nominal.
- Verify `ROICalculator` output matches "MoneyCome" simplified logic manually calculated.

**Step 2: Grand Correlation v4**
- Run the full correlation suite (from Phase 13).
- Expect >90% correlation (improvement from 82% discrepancy).

---

## Execution Handoff

**Plan complete and saved to `docs/plan/2026-02-15-phase14-nominal-correction.md`.**

**Recommended Approach:**
1.  **Subagent-Driven**: I will start Task 1 (Script Hardening) immediately.
2.  **Background**: The actual mass fetch (Task 1 Step 3) takes hours. We should start it and then work on Task 2 (Logic) while it runs, using a partial dataset.

**Which approach?**
