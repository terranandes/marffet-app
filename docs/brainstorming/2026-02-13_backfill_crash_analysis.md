# Brainstorming: Root Cause Analysis of Backfill Crash (11%)

**Date**: 2026-02-13
**Topic**: "Why this bug here?" (Silent Failure at 11%)
**Participants**: [PM] (Lead), [CODE] (Technical), [CV] (Challenger), [PL] (Process)

---

## 1. The Core Question ([PM])
**[PM]**: Terran asks: *"Why this bug here?"* effectively asking why we failed to catch this earlier and why it happened exactly at 11%.

## 2. Technical Analysis ([CODE])
**[CODE]**: The crash at ~11% is a textbook **Resource Exhaustion** (OOM) pattern.
-   **Chunk Size 50**: We were sending 50 tickers to `yfinance` at once.
-   **Multithreading**: `yfinance` defaults to `threads=True`. For 50 stocks, it spawns ~50 threads immediately to download data in parallel.
-   **Memory Spike**: Python threads + Pandas DataFrame construction for 25 years of data * 50 stocks creates a massive temporary memory spike (Peak RAM).
-   **Limit**: Zeabur containers (likely <512MB or 1GB) cannot handle this peak.
-   **Result**: The OS Kernel's OOM Killer triggers, silently killing the process. This explains the "disappearing" behavior without a traceback.

## 3. Why 11%? ([CODE])
**[CODE]**: It wasn't *exactly* 11% every time, but 11% is roughly the 3rd or 4th batch (Total 1771 / 50 = 35 batches).
-   **Leak Accumulation**: It's possible we had a minor memory leak, and by batch #4, the baseline RAM usage + the Peak Spike crossed the OOM threshold.
-   **Heavier Stocks**: Batch #3 or #4 might have contained stocks with deeper history or more complex split/dividend data, requiring more RAM to parse.

## 4. Why didn't we catch it? ([CV])
**[CV] (The Challenger)**: This is the critical failure.
1.  **Environment Parity**: We developed and tested on a machine with 16GB+ RAM. A 500MB spike is invisible there. We did not test inside a constrained Docker limit.
2.  **Mocking vs Reality**: We often mock `yfinance` in CI/CD. Real network buffering and object deserialization effectively use much more RAM than mocks.
3.  **Scale Testing**: We verified "it works" with 5-10 stocks. We never ran a full 1,771 stock simulation locally with a 512MB RAM cap enforced.

## 5. The Solution ([PL])
**[PL]**: We have implemented a Defense-in-Depth strategy:
1.  **Reduce Batch**: 50 -> 10 (Reduce Peak RAM by 80%).
2.  **Disable Threads**: Sequential download (Slower, but flat memory profile).
3.  **Aggressive GC**: Force cleanup after every batch to prevent "high water mark" drift.

## 6. Lessons Learned
-   **Rule #1**: "It works on my machine" is a lie for Data Engineering.
-   **Action**: Future bulk-data features MUST be tested with `docker run --memory="512m"` locally before deployment.
-   **Monitoring**: We need container-level metrics (RAM/CPU) to see the OOM curve, not just app logs (which die with the process).

**Outcome**: The fix is deployed. We expect slow but steady completion now.
