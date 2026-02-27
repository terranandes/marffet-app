# Agents Sync Meeting - 2026-02-26 Sync

**Date:** 2026-02-26
**Topic:** BCR Data Discrepancy & Consistency Fix
**Status:** Completed

## 1. Executive Summary `[PL]`
This sync concludes the investigation and resolution of the Bar Chart Race (BCR) discrepancy. Boss observed that the BCR values did not align with the Mars Strategy table or the Excel exports. A deep dive into the data pipeline confirmed that the backend correctly generates identical values across all three endpoints by sharing `SIM_CACHE`. The root cause was identified as a serialization artifact where the starting year (e.g., 2006) was duplicated in the time-series `history` array, representing both the pre-simulation baseline and the first computed year. This caused duplicate rendering and rank shifting in the BCR frontend.

## 2. Technical Root Cause `[SPEC]`
- **Data Flow:** `/api/results` (Mars) and `/api/race-data` (BCR) both call `MarsStrategy.analyze()`.
- **Finding:** The backend `SIM_CACHE` data is perfectly consistent. For example, stock 2383 (台光電) final value is `563,616,139` across BCR, Mars, and Excel.
- **The Bug:** `roi_calculator.py` appends an initial baseline entry to `history` using `start_year` (e.g., 2006, value = 1,000,000). The simulation loop then appends the first year's computed result *also* at `start_year` (e.g., 2006, value = 1,396,272).
- **Frontend Impact:** BCR extracts `history` to render the race. Having two entries for year 2006 per stock forced the frontend's Map deduplication to aggregate 2N items for the first frame, creating phantom/duplicate bars and offset issues.

## 3. Resolution & Verification `[CV]`
**Fix Applied:** `[CODE]` modified `roi_calculator.py` to tag the initial baseline entry as `year: start_year - 1` (e.g., 2005). This cleanly separates the chronological timeline before Simulation Year 1.

**Verification Results:**
1. **Duplicate Check:** Passed ✅. 100% of stocks now export exactly N+1 unique years.
2. **Final Value Check:** Passed ✅. BCR year 2026 wealth matches Mars `finalValue` exactly (e.g., 2383 = $563.6M).
3. **Data Integrity:** Passed ✅. No downstream regressions detected in API schema or table rendering.

## 4. Next Steps
- Push commit `a06c45a` (BCR duplicate year fix) to `master`.
- Zeabur will automatically build and deploy.
- Re-run the verification in the remote staging environment if needed.
