# Agents Sync-up Meeting
**Date:** 2026-02-21 21:15
**Participants:** [PM], [SPEC], [PL], [CODE], [UI], [CV]

## 1. Project Live Progress & Status
- Phase 18 (Pure Nominal DB Rebuild) is officially completed. The duckdb ingestion is lightning fast.
- Phases 19-21 (Correlation Edge-Case Tuning) are completed.
- **Current Grand Correlation Match Rate:** 67.45% (±1.5%) / 80.40% (±3.0%).
- **Current Gap to Target (>85%):** 17.55% (±1.5%) / 4.60% (±3.0%).

## 2. Triages & Bug Fixes
- **Reverse Splits (減資):** We discovered that using the raw Open price causes fractional rounding errors (e.g., detecting 1.45 instead of 1.39). Since we do not store the Reference Price (`平盤價`), auto-detecting reverse splits is disabled. Will handle via a `KNOWN_SPLITS` manual patch library.
- **Emerging Market (興櫃) Crossovers:** Successfully added logic to exclude tracking crossovers by checking if `ref_yrs` exceeds `available_yrs + 1.5`. The lack of score change proved our standard stocks are not failing due to data gaps.
- **Data Glitches:** Added Pre-Spike Stability Checks into `split_detector.py` to prevent 1-day extreme spikes (e.g. 3800 -> 88 -> 3800) from triggering fake reverse splits.

## 3. Deployment Completeness
- Local-Run is perfectly functional with zero-latency caching.
- Zeabur deployment remains blocked by Phase 8 (Volume Mount) -> we need persistent storage to hold `market.duckdb` safely.

## 4. Next Phase Planning
- **Phase 8:** Proceed with Zeabur persistent Volume Mounts and Parquet git backups so the >67% functional build is live.
- **Edge Cases:** Patch the exact, known reverse split ratios for major outliers like `6472` manually into `split_detector.py` to hunt down the final 17% gap.
- **UX/UI:** Re-focus on BUG-010 (Mobile Portfolio Card click timeout).
