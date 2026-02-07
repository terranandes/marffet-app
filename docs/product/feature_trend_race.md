# Feature Architecture: Trend & My Race (V2)

**Version:** 2.0
**Date:** 2026-01-31
**Status:** Stable (Production Ready)

## 1. Overview
This document records the architectural evolution, debugging experiences, and final implementation decisions for the **Trend** (Net Worth History) and **My Race** (Bar Chart Race) features.

## 2. The "Trend" Architecture
The "Trend" tab visualizes the user's Total Assets (Cost vs. Market Value) over time.

-   **Strategy:** **In-Memory Calculation** (Vectorized).
-   **Data Flow:**
    1.  Fetch **ALL** User Transactions (SQL).
    2.  Determine Start Date (First transaction).
    3.  Fetch **ONE** Batch of Historical Prices for all relevant stocks (YFinance Vectorized Download).
    4.  **Replay** transactions in memory day-by-day (or month-by-month) to reconstruct the portfolio state at each interval.
-   **Pros:** Extremely fast (O(1) DB fetch, O(1) Price fetch), low memory footprint.
-   **Cons:** Re-calculates on every request (CPU bound), but acceptable for typical portfolio sizes (<10k txns).

## 3. The "My Race" Evolution

### V1: The "Cache-Heavy" Approach (Legacy)
* **Design:** Iteratively calculated monthly values and stored them in a `race_cache` SQL table.
* **Logic:**
    - Loop 10 years (120 months).
    - For each month, query DB for transactions up to that date.
    - Query DB/API for price at that specific date.
    - Save result to SQL Cache.
* **Failure Mode (Zeabur / Production):**
    - **Socket Hang Up / Timeout:** The iterative process took too long (>30s) for the initial "Cold Run".
    - **OOM (Out of Memory):** Frequent DB writes and holding massive objects in memory caused the container to crash.
    - **Zombie Processes:** Failed runs left the DB in a locked or inconsistent state.

### V2: The "Trend Strategy" Adoption (Current)
* **Decision:** Abandon the iterative cache approach and adopt the stable **In-Memory "Trend" Strategy**.
* **Logic:**
    1.  **Single DB Query:** Fetch all transactions at once.
    2.  **Single Price Query:** `yfinance.download(..., threads=False)` to fetch all required price history in one go.
    3.  **In-Memory Replay:** Reconstruct monthly portfolio values using Python dictionaries.
    4.  **Quarterly Granularity:** Generate frames for Months 3, 6, 9, 12 to reduce frontend payload and align with financial quarters.
    5.  **Current Quarter Extension:** Logic updated to include the current partial quarter (e.g., if today is Jan, show frame for Mar) using latest available data.
* **Result:**
    - **Stability:** Zero OOM crashes.
    - **Speed:** Response time dropped from >60s (timeout) to <2s.
    - **UX:** Smooth playback with Slider control.

## 4. Debugging Experience & Lessons Learned

| Issue | Symptom | Root Cause | Solution |
| :--- | :--- | :--- | :--- |
| **Zeabur OOM** | App restarts silently during Race load | Python Garbage Collection too slow during high-frequency SQL + Network loops. | **Remove Loop.** Switch to Vectorized Batch Processing. |
| **Socket Hang Up** | Frontend waiting indefinitely | Request timeout (NGINX/Gunicorn default 60s) on "Cold Run". | **Optimize Algo.** Reduce complexity from O(N*M) to O(N). |
| **Missing Bond Data** | `00937B.TW` returns no price | YFinance ticker mapping issues for specialized ETFs. | **Suffix Logic.** Added robustness to try `.TW`, `.TWO` (Taipei Exchange) suffixes. |
| **Time Travel** | Animation stops at Dec 2025 in Jan 2026 | `end_date` fixed to `datetime.now()`. | **Logic Update.** Set `end_date` to `QuarterEnd` (Mar 31) to force inclusion of current state. |

## 5. Final Architecture

### Backend (`app/portfolio_db.py`)
-   **Function:** `get_portfolio_race_data_calculated(user_id)`
-   **Granularity:** Quarterly (Mar, Jun, Sep, Dec).
-   **Price Source:** `yfinance` (Real-time/History).
-   **Fallback:** If price missing, uses Cost Basis (Conservative Valuation).

### Frontend (`frontend/.../myrace/page.tsx`)
-   **Viz:** ECharts (Bar Chart Race).
-   **Controls:** Play/Pause, Slider (Timeline Scrubbing).
-   **State:** React `useState` synced with Animation Frame.

## 6. Conclusion
The migration of "My Race" to the "Trend Architecture" was the decisive factor in stabilizing the platform. We successfully traded "Cached Persistence" (complex, write-heavy) for "On-Demand Computation" (simple, CPU-light), which aligns perfectly with the constraints of a containerized environment like Zeabur.
